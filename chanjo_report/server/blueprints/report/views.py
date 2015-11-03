# -*- coding: utf-8 -*-
from __future__ import division
import datetime
import logging

from chanjo.store.api import filter_samples
from chanjo.store import Exon, Gene
from flask import abort, Blueprint, render_template, request, url_for
from flask_weasyprint import render_pdf

from chanjo_report.server.extensions import api

logger = logging.getLogger(__name__)
report_bp = Blueprint('report', __name__, template_folder='templates',
                      static_folder='static', static_url_path='/static/report')


@report_bp.route('/')
def index():
    sample_objs = api.samples()
    gene_objs = api.query(Gene).limit(50)
    return render_template('report/index.html', samples=sample_objs,
                           genes=gene_objs)


@report_bp.route('/<gene_id>')
def gene(gene_id):
    """Display coverage information on a gene."""
    sample_vals = api.gene(gene_id)
    return render_template('report/gene.html', samples=sample_vals,
                           gene_id=gene_id)


@report_bp.route('/group/<group_id>')
@report_bp.route('/samples')
def group(group_id=None):
    """Generate a coverage report for a group of samples."""
    gene_ids = request.args.getlist('gene_id')
    level = request.args.get('level', 10)
    panel_name = request.args.get('panel_name')
    sample_ids = request.args.getlist('sample_id')
    show_genes = 'show_genes' in request.args

    logger.debug('fetch samples for group %s', group_id)
    sample_objs = api.samples(group_id=group_id, sample_ids=sample_ids)
    sample_dict = {sample_obj.sample_id: sample_obj
                   for sample_obj in sample_objs}

    logger.debug('generate base queries for report')
    group_query = filter_samples(api.query(), group_id=group_id,
                                 sample_ids=sample_ids)
    if gene_ids:
        exon_ids = [exon_obj.exon_id for exon_obj in api.gene_exons(*gene_ids)]
        panel_query = group_query.filter(Exon.exon_id.in_(exon_ids))
    else:
        panel_query = group_query

    logger.debug('generate general stats (gene panel)')
    key_metrics = api.means(panel_query)
    levels = api.completeness_levels()

    logger.debug('calculate diagnostic yield for each sample')
    tx_samples = [(sample_obj, api.diagnostic_yield(sample_obj.sample_id,
                                                    query=panel_query,
                                                    level=level))
                  for sample_obj in sample_objs]

    return render_template(
        'report/report.html',
        samples=sample_dict,
        key_metrics=key_metrics,
        panel_name=panel_name,
        levels=levels,
        selected_level=level,
        diagnostic_yield=tx_samples,
        genders=api.sex_check(group_id=group_id, sample_ids=sample_ids),
        show_genes=show_genes,
        created_at=datetime.date.today(),
        group_id=group_id,
        query_args=request.args,
    )


@report_bp.route('/<route>/<filter_id>.pdf')
def pdf(route, filter_id):
    # make a PDF from another view
    if route == 'group':
        response = render_pdf(url_for('report.group', group_id=filter_id,
                                      **request.args))
    else:
        return abort(404)

    # check if the request is to download the file right away
    if 'dl' in request.args:
        fname = "coverage-report_{}.pdf".format(filter_id)
        header = "attachment; filename={}".format(fname)
        response.headers['Content-Disposition'] = header

    return response
