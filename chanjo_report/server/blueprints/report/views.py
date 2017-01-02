# -*- coding: utf-8 -*-
from __future__ import division
import itertools
import logging

from chanjo.store.models import Transcript, TranscriptStat, Sample
from chanjo.sex.core import predict_sex
from flask import abort, Blueprint, render_template, request, url_for, flash
from flask_weasyprint import render_pdf
from sqlalchemy import func
from sqlalchemy.exc import OperationalError

from chanjo_report.server.extensions import api

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


def map_samples(group_id=None, sample_ids=None):
    if group_id:
        query = Sample.query.filter(Sample.group_id == group_id)
    elif sample_ids:
        query = Sample.query.filter(Sample.id.in_(sample_ids))
    try:
        samples = {sample_obj.id: sample_obj for sample_obj in query}
        return samples
    except OperationalError as error:
        logger.exception(error)
        api.session.rollback()
        return abort(500, 'MySQL error, try again')


@report_bp.route('/genes/<gene_id>')
def gene(gene_id):
    """Display coverage information on a gene."""
    sample_ids = request.args.getlist('sample_id')
    sample_dict = map_samples(sample_ids=sample_ids)
    gene_name = Transcript.filter_by(gene_id=gene_id).first().gene_name
    tx_groups = transcript_coverage(api, gene_id, *sample_ids)
    link = request.args.get('link')
    return render_template('report/gene.html', gene_id=gene_id,
                           gene_name=gene_name, link=link,
                           tx_groups=tx_groups, samples=sample_dict)


@report_bp.route('/genes')
def genes():
    """Display an overview of genes that are (un)completely covered."""
    skip = int(request.args.get('skip', 0))
    limit = int(request.args.get('limit', 30))
    exonlink = request.args.get('exonlink')
    sample_ids = request.args.getlist('sample_id')
    samples_q = Sample.filter(Sample.id.in_(sample_ids))
    level = request.args.get('level', 10)
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
    return render_template('report/genes.html', incomplete=incomplete_left,
                           level=level, skip=skip, limit=limit,
                           has_next=has_next, gene_ids=gene_ids,
                           exonlink=exonlink, samples=samples_q,
                           sample_ids=sample_ids)


@report_bp.route('/report/<group_id>', methods=['GET', 'POST'])
def report(group_id):
    """Generate a coverage report for a group of samples."""
    raw_gene_ids = (request.args.get('gene_ids') or
                    request.form.get('gene_ids'))
    if raw_gene_ids:
        gene_ids = [int(gene_id.strip()) for gene_id in raw_gene_ids.split(',')]
    else:
        gene_ids = []
    level_raw = request.args.get('level') or request.form.get('level') or 10
    extras = {
        'panel_name': (request.args.get('panel_name') or
                       request.form.get('panel_name')),
        'level': int(level_raw),
        'gene_ids': gene_ids,
        'show_genes': any([request.args.get('show_genes'),
                           request.form.get('show_genes')]),
    }
    samples = Sample.query.filter_by(group_id=group_id)
    sample_ids = [sample.id for sample in samples]
    sex_rows = samplesex_rows(sample_ids)
    metrics_rows = keymetrics_rows(sample_ids, genes=gene_ids)
    tx_rows = transcripts_rows(sample_ids, genes=gene_ids)
    return render_template('report/report.html', extras=extras,
                           samples=samples, sex_rows=sex_rows,
                           group_id=group_id,
                           metrics_rows=metrics_rows, tx_rows=tx_rows)


def samplesex_rows(sample_ids):
    """Generate sex prediction info rows."""
    sex_query = (api.query(TranscriptStat.sample_id,
                           Transcript.chromosome,
                           func.avg(TranscriptStat.mean_coverage))
                    .join(TranscriptStat.transcript)
                    .filter(Transcript.chromosome.in_(['X', 'Y']),
                            TranscriptStat.sample_id.in_(sample_ids))
                    .group_by(TranscriptStat.sample_id, Transcript.chromosome))

    samples = itertools.groupby(sex_query, lambda row: row[0])
    for sample_id, chromosomes in samples:
        chr_coverage = [coverage for _, _, coverage in chromosomes]
        logger.debug('predicting sex')
        predicted_sex = predict_sex(*chr_coverage)
        sample_obj = Sample.query.get(sample_id)
        sample_row = {
            'sample': sample_obj.name,
            'group': sample_obj.group_name,
            'analysis_date': sample_obj.created_at,
            'sex': predicted_sex,
            'x_coverage': chr_coverage[0],
            'y_coverage': chr_coverage[1],
        }
        yield sample_row


def keymetrics_rows(samples_ids, genes=None):
    """Generate key metrics rows."""
    fields = (
        TranscriptStat,
        func.avg(TranscriptStat.mean_coverage).label('mean_coverage'),
        func.avg(TranscriptStat.completeness_10).label('completeness_10'),
        func.avg(TranscriptStat.completeness_15).label('completeness_15'),
        func.avg(TranscriptStat.completeness_20).label('completeness_20'),
        func.avg(TranscriptStat.completeness_50).label('completeness_50'),
        func.avg(TranscriptStat.completeness_100).label('completeness_100'),
    )
    query = (api.query(*fields)
                .filter(TranscriptStat.sample_id.in_(samples_ids))
                .group_by(TranscriptStat.sample_id))
    if genes:
        query = (query.join(TranscriptStat.transcript)
                      .filter(Transcript.gene_id.in_(genes)))
    return query


def transcripts_rows(sample_ids, genes=None):
    """Generate metrics rows for transcripts."""
    for sample_id in sample_ids:
        sample_obj = Sample.query.get(sample_id)
        all_tx = TranscriptStat.query.filter_by(sample_id=sample_id)
        if genes:
            all_tx = (all_tx.join(TranscriptStat.transcript)
                            .filter(Transcript.gene_id.in_(genes)))
        tx_count = all_tx.count()
        missed_tx = all_tx.filter(TranscriptStat.completeness_10 < 100)
        missed_count = missed_tx.count()
        if tx_count == 0:
            tx_yield = 0
            flash("no matching transcripts found!")
        else:
            tx_yield = 100 - (missed_count / tx_count * 100)
        yield {
            'sample': sample_obj,
            'yield': tx_yield,
            'missed': missed_tx,
            'missed_count': missed_count,
            'total': tx_count,
        }


@report_bp.route('/report/<group_id>.pdf', methods=['GET', 'POST'])
def pdf(group_id):
    data_dict = request.form if request.method == 'POST' else request.args

    # make a PDF from another view
    response = render_pdf(url_for('report.report', group_id=group_id,
                                  **data_dict))

    # check if the request is to download the file right away
    if 'dl' in request.args:
        fname = "coverage-report_{}.pdf".format(group_id)
        header = "attachment; filename={}".format(fname)
        response.headers['Content-Disposition'] = header

    return response


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

    samples_query = api.query(Sample.id)
    if samples:
        samples_query = samples_query.filter(Sample.id.in_(samples))
        missed_tx = missed_tx.filter(TranscriptStat.sample_id.in_(samples))
    elif group:
        samples_query = samples_query.filter_by(group_id=group)
        missed_tx = (missed_tx.join(TranscriptStat.sample)
                              .filter(Sample.group_id == group))

    all_count = all_tx.count()
    all_samples = [row[0] for row in samples_query.all()]

    sample_groups = itertools.groupby(missed_tx, key=lambda tx: tx.sample_id)
    missed_samples = {}
    for sample_id, tx_models in sample_groups:
        gene_ids = set()
        tx_count = 0
        for tx_model in tx_models:
            gene_ids.add(tx_model.transcript.gene_id)
            tx_count += 1
        diagnostic_yield = 100 - (tx_count / all_count * 100)
        result = {'sample_id': sample_id}
        result['diagnostic_yield'] = diagnostic_yield
        result['count'] = tx_count
        result['total_count'] = all_count
        result['genes'] = list(gene_ids)
        missed_samples[sample_id] = result

    for sample_id in all_samples:
        if sample_id in missed_samples:
            yield missed_samples[sample_id]
        else:
            # all transcripts are covered!
            result = {'sample_id': sample_id, 'diagnostic_yield': 100}
            yield result
