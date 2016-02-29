# -*- coding: utf-8 -*-
from __future__ import division
from collections import OrderedDict
import datetime
import itertools
import logging

from chanjo.store.api import filter_samples
from chanjo.store import Exon, ExonStatistic, Transcript, Gene, Sample
from flask import abort, Blueprint, render_template, request, url_for
from flask_weasyprint import render_pdf
from sqlalchemy import func
from sqlalchemy.exc import OperationalError

from chanjo_report.server.extensions import api

logger = logging.getLogger(__name__)
report_bp = Blueprint('report', __name__, template_folder='templates',
                      static_folder='static', static_url_path='/static/report')


def transcript_coverage(api, gene_id, *sample_ids):
    """Return coverage metrics per transcript for a given gene."""
    query = (api.query(Transcript.transcript_id, Sample.sample_id,
                       ExonStatistic.metric, api.weighted_average)
                .join(ExonStatistic.sample, ExonStatistic.exon,
                      Exon.transcripts, Transcript.gene)
                .filter(Gene.gene_id == gene_id)
                .group_by(Sample.sample_id, ExonStatistic.metric,
                          Transcript.transcript_id)
                .order_by(Transcript.transcript_id, Sample.sample_id))

    if sample_ids:
        query = query.filter(Sample.sample_id.in_(sample_ids))

    tx_groups = itertools.groupby(query, key=lambda group: group[0])
    for tx_id, tx_group in tx_groups:
        sample_groups = itertools.groupby(tx_group, key=lambda group: group[1])
        results = []
        for sample_id, sample_group in sample_groups:
            group_data = {metric: average for _, _, metric, average
                          in sample_group}
            results.append((sample_id, group_data))
        yield (tx_id, results)


def exon_stats(api, gene_id, *sample_ids):
    """Return exons stats for a gene per sample."""
    query = (api.query(Sample.sample_id, ExonStatistic.metric,
                       ExonStatistic.value)
                .join(ExonStatistic.exon, ExonStatistic.sample,
                      Exon.transcripts, Transcript.gene)
                .filter(Gene.gene_id == gene_id)
                .order_by(Sample.sample_id, Exon.start))
    if sample_ids:
        query = query.filter(Sample.sample_id.in_(sample_ids))

    sample_groups = itertools.groupby(query, key=lambda group: group[0])
    for sample_id, sample_group in sample_groups:
        yield sample_id, exon_plot(sample_group)


def exon_plot(stats):
    """Parse exons stats and prepare Highcharts input data."""
    lines = OrderedDict()
    labels = []
    complete_stats = (stat for stat in stats if stat[1] != 'mean_coverage')
    sorted_stats = sorted(complete_stats,
                          key=lambda stat: int(stat[1].split('_')[-1]))
    for index, (_, metric, value) in enumerate(sorted_stats):
        labels.append(index + 1)
        if metric not in lines:
            lines[metric] = []
        lines[metric].append(value)

    return labels, lines


def map_samples(api, group_id=None, sample_ids=None):
    sample_objs = api.samples(group_id=None, sample_ids=sample_ids)
    try:
        samples = {sample_obj.sample_id: sample_obj for sample_obj
                   in sample_objs}
        return samples
    except OperationalError as error:
        logger.exception(error)
        api.session.rollback()
        return abort(500, 'MySQL error, try again')


@report_bp.route('/<gene_id>')
def gene(gene_id):
    """Display coverage information on a gene."""
    sample_ids = request.args.getlist('sample_id')
    levels = list(api.completeness_levels())
    tx_stats = transcript_coverage(api, gene_id, *sample_ids)
    ex_plots = exon_stats(api, gene_id, *sample_ids)
    gene_obj = api.query(Gene).filter_by(gene_id=gene_id).first()
    if gene_obj is None:
        return abort(404, "Gene ({}) not found".format(gene_id))
    sample_dict = map_samples(api, sample_ids=sample_ids)
    # generate id map
    id_map = {key.lstrip('alt_'): value for key, value in request.args.items()
              if key.startswith('alt_')}
    return render_template('report/gene.html', gene_id=gene_id, gene=gene_obj,
                           tx_stats=tx_stats, ex_plots=ex_plots,
                           levels=levels, samples=sample_dict, id_map=id_map)


@report_bp.route('/genes')
def genes():
    """Display an overview of genes that are (un)completely covered."""
    skip = int(request.args.get('skip', 0))
    limit = int(request.args.get('limit', 50))
    sample_ids = request.args.getlist('sample_id')
    levels = list(api.completeness_levels())
    level = request.args.get('level', levels[0][0])
    raw_gene_ids = request.args.get('gene_id')
    query = (api.query(Transcript, Sample.sample_id,
                       func.avg(ExonStatistic.value))
                .join(ExonStatistic.exon, ExonStatistic.sample,
                      Exon.transcripts)
                .filter(ExonStatistic.metric == "completeness_{}".format(level))
                .group_by(Transcript.transcript_id)
                .order_by(func.avg(ExonStatistic.value)))

    gene_ids = raw_gene_ids.split(',') if raw_gene_ids else None
    if raw_gene_ids:
        tx_ids = [tx_tuple[0] for tx_tuple in
                  api.query(Transcript.id)
                     .join(Transcript.gene)
                     .filter(Gene.gene_id.in_(gene_ids))]
        query = query.filter(Transcript.id.in_(tx_ids))

    if sample_ids:
        query = query.filter(Sample.sample_id.in_(sample_ids))

    incomplete_left = query.offset(skip).limit(limit)
    total = query.count()
    has_next = total > skip + limit

    # generate id map
    id_map = {key.lstrip('alt_'): value for key, value in request.args.items()
              if key.startswith('alt_')}

    link_args = {key: value for key, value in request.args.items()
                 if key.startswith('alt_')}
    link_args['sample_id'] = sample_ids
    return render_template('report/genes.html', incomplete=incomplete_left,
                           levels=levels, level=level, sample_ids=sample_ids,
                           skip=skip, limit=limit, has_next=has_next,
                           id_map=id_map, gene_ids=gene_ids,
                           link_args=link_args)


@report_bp.route('/group/<group_id>', methods=['GET', 'POST'])
@report_bp.route('/samples')
def group(group_id=None):
    """Generate a coverage report for a group of samples.

    It's possible to map existing group and sample ids to display ids
    by passing them as key/value pair request args.
    """
    if request.method == 'POST':
        data_dict = request.form
    else:
        data_dict = request.args

    gene_ids = data_dict.get('gene_ids', [])
    if gene_ids:
        gene_ids = [gene_id.strip() for gene_id in gene_ids.split(',')]
    sample_ids = data_dict.get('sample_ids', [])
    if sample_ids:
        sample_ids = sample_ids.split(',')
    try:
        level = int(data_dict.get('level'))
    except (ValueError, TypeError):
        level = 10

    # generate id map
    id_map = {key.lstrip('alt_'): value for key, value in data_dict.items()
              if key.startswith('alt_')}

    customizations = {
        'level': level,
        'gene_ids': gene_ids,
        'panel_name': data_dict.get('panel_name'),
        'sample_ids': sample_ids,
        'show_genes': 'show_genes' in data_dict,
        'id_map': id_map
    }

    logger.debug('fetch samples for group %s', group_id)
    sample_dict = map_samples(api, group_id=group_id, sample_ids=sample_ids)

    if len(sample_dict) == 0:
        return abort(404, "no samples matching group: {}".format(group_id))

    logger.debug('generate base queries for report')
    group_query = filter_samples(api.query(), group_id=group_id,
                                 sample_ids=sample_ids)
    if customizations['gene_ids']:
        exon_ids = [exon_obj.exon_id for exon_obj
                    in api.gene_exons(*customizations['gene_ids'])]
        panel_query = group_query.filter(Exon.exon_id.in_(exon_ids))
    else:
        panel_query = group_query
        exon_ids = None

    logger.debug('generate general stats (gene panel)')
    key_metrics = api.means(panel_query)
    levels = api.completeness_levels()
    if not customizations['level'] in [item[0] for item in levels]:
        return abort(400, ('completeness level not supported: {}'
                           .format(customizations['level'])))

    logger.debug('calculate diagnostic yield for each sample')
    tx_samples = [(sample_obj,
                   api.diagnostic_yield(sample_obj.sample_id,
                                        exon_ids=exon_ids,
                                        level=customizations['level']))
                  for sample_obj in sample_dict.values()]

    return render_template(
        'report/report.html',
        samples=sample_dict,
        key_metrics=key_metrics,
        customizations=customizations,
        levels=levels,
        diagnostic_yield=tx_samples,
        genders=api.sex_check(group_id=group_id, sample_ids=sample_ids),
        created_at=datetime.date.today(),
        group_id=group_id,
    )


@report_bp.route('/group/<group_id>.pdf', methods=['GET', 'POST'])
def pdf(group_id):
    data_dict = request.form if request.method == 'POST' else request.args

    # make a PDF from another view
    response = render_pdf(url_for('report.group', group_id=group_id,
                                  **data_dict))

    # check if the request is to download the file right away
    if 'dl' in request.args:
        fname = "coverage-report_{}.pdf".format(group_id)
        header = "attachment; filename={}".format(fname)
        response.headers['Content-Disposition'] = header

    return response
