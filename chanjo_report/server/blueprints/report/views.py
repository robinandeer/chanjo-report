# -*- coding: utf-8 -*-
import logging
import datetime
from chanjo.store.models import Transcript, TranscriptStat, Sample
from flask import abort, Blueprint, render_template, request, url_for, session, jsonify
from flask_weasyprint import render_pdf

from chanjo_report.server.extensions import api
from chanjo_report.server.constants import LEVELS
from .utils import (samplesex_rows, keymetrics_rows, transcripts_rows, map_samples,
                    transcript_coverage, chromosome_coverage)

logger = logging.getLogger(__name__)
report_bp = Blueprint('report', __name__, template_folder='templates',
                      static_folder='static', static_url_path='/static/report')


@report_bp.route('/genes/<gene_id>')
def gene(gene_id):
    """Display coverage information on a gene."""
    sample_ids = request.args.getlist('sample_id')
    sample_dict = map_samples(sample_ids=sample_ids)
    matching_tx = Transcript.filter_by(gene_id=gene_id).first()
    if matching_tx is None:
        return abort(404, "gene not found: {}".format(gene_id))
    gene_name = matching_tx.gene_name
    tx_groups = transcript_coverage(api, gene_id, *sample_ids)
    link = request.args.get('link')
    return render_template('report/gene.html', gene_id=gene_id,
                           gene_name=gene_name, link=link,
                           tx_groups=tx_groups, samples=sample_dict)


@report_bp.route('/genes', methods=['GET', 'POST'])
def genes():
    """Display an overview of genes that are (un)completely covered."""
    skip = int(request.args.get('skip', 0))
    limit = int(request.args.get('limit', 30))
    exonlink = request.args.get('exonlink')
    sample_ids = request.args.getlist('sample_id')
    samples_q = Sample.filter(Sample.id.in_(sample_ids))
    level = request.args.get('level', 10)
    raw_gene_ids = request.args.get('gene_id') or request.form.get('gene_ids')
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
    return render_template('report/genes.html', incomplete=incomplete_left,
                           level=level, skip=skip, limit=limit,
                           has_next=has_next, gene_ids=gene_ids,
                           exonlink=exonlink, samples=samples_q,
                           sample_ids=sample_ids)



@report_bp.route('/json_chrom_coverage', methods=['POST'])
def json_chrom_coverage():
    """Calculate mean coverage over all gene transcripts of a chromosome for one or more samples and return results as json"""

    results = {}
    data = request.json

    if not (data.get('chrom') and data.get('sample_ids')):
        return jsonify(results)

    chrom = str(data.get('chrom'))
    sample_ids = data.get('sample_ids').split(",")

    metrics_rows = chromosome_coverage(sample_ids, chrom).all()
    for row in metrics_rows:
        ts = row[0] # An object of class TranscriptStat
        results[ts.sample_id] = row[1] # Collect mean coverage over the chromosome transcripts

    return jsonify(results)


@report_bp.route('/json_gene_coverage', methods=['POST'])
def json_gene_coverage():
    """Calculate mean coverage over a list of genes for one or more samples and return results as json"""
    results = {}
    data = request.json

    if not (data.get('gene_ids') and data.get('sample_ids')):
        return jsonify(results)

    gene_ids = data.get('gene_ids').split(",")
    sample_ids = data.get('sample_ids').split(",")

    metrics_rows = keymetrics_rows(sample_ids, genes=gene_ids).all()

    for row in metrics_rows:
        ts = row[0] # An object of class TranscriptStat
        results[ts.sample_id] = row[1] # Collect mean coverage over the genes
    return jsonify(results)


@report_bp.route('/report', methods=['GET', 'POST'])
def report():
    """Generate a coverage report for a group of samples."""
    sample_ids = request.args.getlist('sample_id') or request.form.getlist('sample_id')
    raw_gene_ids = (request.args.get('gene_ids') or request.form.get('gene_ids'))
    gene_ids = []
    if raw_gene_ids:
        session['all_genes'] = raw_gene_ids
        gene_ids = [gene_id.strip() for gene_id in raw_gene_ids.split(',')]
    else:
        if request.method=='GET' and session.get('all_genes'):
            gene_ids = [gene_id.strip() for gene_id in session.get('all_genes').split(',')]
    try:
        # gene ids should be numerical, if they are strings print error String instead
        gene_ids = [int(gene_id) for gene_id in gene_ids]
    except ValueError:
        return "Gene format not supported. Gene list should contain comma-separated HGNC numerical identifiers, not strings."

    level = int(request.args.get('level') or request.form.get('level') or 10)
    extras = {
        'panel_name': (request.args.get('panel_name') or request.form.get('panel_name')),
        'level': level,
        'gene_ids': gene_ids,
        'show_genes': any([request.args.get('show_genes'), request.form.get('show_genes')]),
    }
    samples = Sample.query.filter(Sample.id.in_(sample_ids))
    case_name = request.args.get('case_name') or request.form.get('case_name')
    sex_rows = samplesex_rows(sample_ids)
    metrics_rows = keymetrics_rows(sample_ids, genes=gene_ids)
    tx_rows = transcripts_rows(sample_ids, genes=gene_ids, level=level)
    return render_template('report/report.html', extras=extras,
                           samples=samples, case_name=case_name, sex_rows=sex_rows,
                           sample_ids=sample_ids, levels=LEVELS,
                           metrics_rows=metrics_rows, tx_rows=tx_rows)


@report_bp.route('/report/pdf', methods=['GET', 'POST'])
def pdf():
    data_dict = request.form if request.method == 'POST' else request.args
    # make a PDF from another view
    response = render_pdf(url_for('report.report', **data_dict))

    # check if the request is to download the file right away
    if 'dl' in data_dict:
        date_str = str(datetime.datetime.now().strftime("%Y-%m-%d"))
        fname = '_'.join(['coverage-report', date_str+'.pdf'])

        if 'case_name' in data_dict: # if downloaded pdf should be named after a case sisplay name
            fname = '_'.join([str(data_dict['case_name']),fname])

        header = "attachment; filename={}".format(fname)
        response.headers['Content-Disposition'] = header

    return response
