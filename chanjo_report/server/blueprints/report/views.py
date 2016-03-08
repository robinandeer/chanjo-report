# -*- coding: utf-8 -*-
from __future__ import division
import datetime
import itertools
import logging

from chanjo.store.txmodels import Transcript, TranscriptStat, Sample
from chanjo.store.utils import predict_gender
from flask import abort, Blueprint, render_template, request, url_for
from flask_weasyprint import render_pdf
from sqlalchemy import func
from sqlalchemy.exc import OperationalError

from chanjo_report.server.extensions import api

LEVELS = [(10, 'completeness_10'), (15, 'completeness_15'),
          (20, 'completeness_20'), (50, 'completeness_50'),
          (100, 'completeness_100')]
logger = logging.getLogger(__name__)
report_bp = Blueprint('report', __name__, template_folder='templates',
                      static_folder='static', static_url_path='/static/report')


def transcript_coverage(api, gene_id, *sample_ids):
    """Return coverage metrics per transcript for a given gene."""
    query = (api.query(TranscriptStat)
                .join(TranscriptStat.transcript)
                .filter(Transcript.gene_id == gene_id)
                .order_by(TranscriptStat.transcript_id,
                          TranscriptStat.sample_id))
    if sample_ids:
        query = query.filter(TranscriptStat.sample_id.in_(sample_ids))

    tx_groups = itertools.groupby(query, key=lambda tx: tx.transcript_id)
    return tx_groups


def map_samples(api, group_id=None, sample_ids=None):
    query = api.query(Sample)
    if group_id:
        query = query.filter(Sample.group_id == group_id)
    elif sample_ids:
        query = query.filter(Sample.id.in_(sample_ids))
    try:
        samples = {sample_obj.id: sample_obj for sample_obj in query}
        return samples
    except OperationalError as error:
        logger.exception(error)
        api.session.rollback()
        return abort(500, 'MySQL error, try again')


@report_bp.route('/<gene_id>')
def gene(gene_id):
    """Display coverage information on a gene."""
    sample_ids = request.args.getlist('sample_id')
    tx_groups = transcript_coverage(api, gene_id, *sample_ids)
    sample_dict = map_samples(api, sample_ids=sample_ids)
    link = request.args.get('link')
    # generate id map
    id_map = {key.lstrip('alt_'): value for key, value in request.args.items()
              if key.startswith('alt_')}
    return render_template('report/gene.html', gene_id=gene_id, link=link,
                           tx_groups=tx_groups, levels=LEVELS,
                           samples=sample_dict, id_map=id_map)


@report_bp.route('/genes')
def genes():
    """Display an overview of genes that are (un)completely covered."""
    skip = int(request.args.get('skip', 0))
    limit = int(request.args.get('limit', 50))
    exonlink = request.args.get('exonlink')
    sample_ids = request.args.getlist('sample_id')
    level = request.args.get('level', LEVELS[0][0])
    raw_gene_ids = request.args.get('gene_id')
    completeness_col = getattr(TranscriptStat, "completeness_{}".format(level))
    query = (api.query(TranscriptStat)
                .join(TranscriptStat.transcript)
                .filter(completeness_col < 100)
                .order_by(completeness_col))

    gene_ids = raw_gene_ids.split(',') if raw_gene_ids else []
    if raw_gene_ids:
        query = query.filter(Transcript.gene_id.in_(gene_ids))
    if sample_ids:
        query = query.filter(TranscriptStat.sample_id.in_(sample_ids))

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
                           levels=LEVELS, level=level, sample_ids=sample_ids,
                           skip=skip, limit=limit, has_next=has_next,
                           id_map=id_map, gene_ids=gene_ids, exonlink=exonlink,
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

    logger.debug('generate general stats (gene panel)')
    key_query = key_metrics(api, genes=customizations['gene_ids'],
                            samples=sample_ids, group=group_id)
    if not customizations['level'] in [item[0] for item in LEVELS]:
        return abort(400, ('completeness level not supported: {}'
                           .format(customizations['level'])))

    logger.debug('calculate diagnostic yield for each sample')
    tx_samples = diagnostic_yield(api, genes=gene_ids, samples=sample_ids,
                                  group=group_id, level=customizations['level'])

    return render_template(
        'report/report.html',
        samples=sample_dict,
        key_metrics=key_query,
        customizations=customizations,
        levels=LEVELS,
        diagnostic_yield=tx_samples,
        genders=sex_check(api, group=group_id, samples=sample_ids),
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


def key_metrics(api, genes=None, samples=None, group=None):
    """Calculate key means across potentially a gene panel."""
    query = api.query(
        TranscriptStat,
        func.avg(TranscriptStat.mean_coverage).label('mean_coverage'),
        func.avg(TranscriptStat.completeness_10).label('completeness_10'),
        func.avg(TranscriptStat.completeness_15).label('completeness_15'),
        func.avg(TranscriptStat.completeness_20).label('completeness_20'),
        func.avg(TranscriptStat.completeness_50).label('completeness_50'),
        func.avg(TranscriptStat.completeness_100).label('completeness_100')
    ).group_by(TranscriptStat.sample_id)
    if genes:
        query = (query.join(TranscriptStat.transcript)
                      .filter(Transcript.gene_id.in_(genes)))
    if samples:
        query = query.filter(TranscriptStat.sample_id.in_(samples))
    elif group:
        query = (query.join(TranscriptStat.sample)
                      .filter(Sample.group_id == group))
    return query


def diagnostic_yield(api, genes=None, samples=None, group=None, level=10):
    """Calculate transcripts that aren't completely covered.

    This metric only applies to one sample in isolation. Otherwise
    it's hard to know what to do with exons that are covered or
    not covered across multiple samples.

    Args:
        sample_id (str): unique sample id
    """
    threshold = 100
    str_level = "completeness_{}".format(level)
    completeness_col = getattr(TranscriptStat, str_level)

    all_tx = api.query(Transcript)
    missed_tx = (api.query(TranscriptStat)
                    .filter(completeness_col < threshold)
                    .order_by(TranscriptStat.sample_id))

    if genes:
        missed_tx = (missed_tx.join(TranscriptStat.transcript)
                              .filter(Transcript.gene_id.in_(genes)))
        all_tx = all_tx.filter(Transcript.gene_id.in_(genes))

    if samples:
        missed_tx = missed_tx.filter(TranscriptStat.sample_id.in_(samples))
    elif group:
        missed_tx = (missed_tx.join(TranscriptStat.sample)
                              .filter(Sample.group_id == group))

    all_count = all_tx.count()
    sample_groups = itertools.groupby(missed_tx, key=lambda tx: tx.sample_id)
    for sample_id, tx_models in sample_groups:
        tx_models = list(tx_models)
        tx_count = len(tx_models)
        diagnostic_yield = 100 - (tx_count/all_count * 100)
        result = {
            "sample_id": sample_id,
            "diagnostic_yield": diagnostic_yield,
            "count": tx_count,
            "total_count": all_count,
            "transcripts": tx_models
        }
        yield result


def sex_coverage(api, sex_chromosomes=('X', 'Y')):
    """Query for average on X/Y chromsomes.

    Args:
        sex_chromosomes (Optional[tuple]): chromosome ids

    Returns:
        List[tuple]: sample, chromosome, weighted average coverage
    """
    query = (api.query(TranscriptStat.sample_id,
                       Transcript.chromosome,
                       func.avg(TranscriptStat.mean_coverage))
                .join(TranscriptStat.transcript)
                .filter(Transcript.chromosome.in_(sex_chromosomes))
                .group_by(TranscriptStat.sample_id, Transcript.chromosome))
    return query


def sex_check(api, group=None, samples=None):
    """Predict gender based on coverage of sex chromosomes.

    Args:
        group (Optional[str]): sample group identifier
        samples (Optional[List[str]]): sample ids

    Returns:
        tuple: sample, gender, coverage X, coverage, Y
    """
    query = sex_coverage(api)
    if samples:
        query = query.filter(TranscriptStat.sample_id.in_(samples))
    elif group:
        query = (query.join(TranscriptStat.sample)
                      .filter(Sample.group_id == group))
    logger.debug('group rows based on sample')
    samples = itertools.groupby(query, lambda row: row[0])
    for sample_id, chromosomes in samples:
        coverage = [cov for _, _, cov in chromosomes]
        logger.debug('predict gender')
        gender = predict_gender(*coverage)
        yield sample_id, gender, coverage[0], coverage[1]
