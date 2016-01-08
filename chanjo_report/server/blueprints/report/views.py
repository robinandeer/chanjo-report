# -*- coding: utf-8 -*-
from __future__ import division
import datetime
import logging

from chanjo.store.api import filter_samples
from chanjo.store import Exon
from flask import abort, Blueprint, render_template, request, url_for
from flask_weasyprint import render_pdf

from chanjo_report.server.extensions import api

logger = logging.getLogger(__name__)
report_bp = Blueprint('report', __name__, template_folder='templates',
                      static_folder='static', static_url_path='/static/report')


@report_bp.route('/<gene_id>')
def gene(gene_id):
    """Display coverage information on a gene."""
    sample_vals = api.gene(gene_id)
    return render_template('report/gene.html', samples=sample_vals,
                           gene_id=gene_id)


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
        'show_genes': 'show_genes' in request.args,
        'id_map': id_map
    }

    logger.debug('fetch samples for group %s', group_id)
    sample_objs = api.samples(group_id=group_id,
                              sample_ids=customizations['sample_ids'])

    sample_dict = {sample_obj.sample_id: sample_obj
                   for sample_obj in sample_objs}

    if len(sample_dict) == 0:
        return abort(404, "no samples matching group: {}".format(group_id))

    logger.debug('generate base queries for report')
    group_query = filter_samples(api.query(), group_id=group_id,
                                 sample_ids=customizations['sample_ids'])
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
                  for sample_obj in sample_objs]

    return render_template(
        'report/report.html',
        samples=sample_dict,
        key_metrics=key_metrics,
        customizations=customizations,
        levels=levels,
        diagnostic_yield=tx_samples,
        genders=api.sex_check(group_id=group_id,
                              sample_ids=customizations['sample_ids']),
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
