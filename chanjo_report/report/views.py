# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division

from flask import Blueprint, current_app, render_template, request, url_for
from flask_weasyprint import render_pdf
import sqlalchemy as sqa

from ..miner import key_metrics
from ..extensions import api
from .utils import read_lines

report = Blueprint(
  'report', __name__, template_folder='templates', static_folder='static')


@report.route('/report/<group_id>')
@report.route('/report/samples/<sample_ids>')
def report_html(group_id=None, sample_ids=None):
  # load superblock ids from gene list file
  # if 'CHANJO_SUPERBLOCK_PANEL' in current_app.config:
  #   superblock_ids = read_lines(current_app.config['CHANJO_SUPERBLOCK_PANEL'])
  # else:
  #   raise TypeError(
  #     "Missing 'report/superblock_panel' variabel in 'chanjo.toml'")
  sample_list = (sample_ids or '').split(',')

  results = key_metrics(api, sample_ids=sample_list, group_id=group_id)
  return render_template('report.html', data=results)


# @report.route('/report/<group_id>')
# def report_html(group_id):
#   # extend total block count query to include perfectly covered blocks
#   covered_blocks = total_block_counts.filter(BlockData.completeness == 1)

#   # initialize data arrays to populate report template with
#   sample_data = samples.all()
#   data = {sample: [sample, cutoff] for sample, cutoff in sample_data}
#   samples = [sample for sample, _ in sample_data]

#   # optionally filter by a list of genes
#   gene_list = current_app.config.get('CHANJO_GENE_LIST')

#   # add metrics to the arrays (match with correct samples)
#   for sample, coverage, completeness in metrics.all():
#     data[sample].append(round(coverage, 4))
#     data[sample].append(round(completeness * 100, 4))

#   total_covered = zip(total_block_counts.all(), covered_blocks.all())
#   for total, covered in total_covered:
#     assert total[0] == covered[0], 'Out of sync!'

#     # calculate diagnostic yield by dividing fully covered sets by all sets
#     diagnostic_yield = round(covered[1] / total[1] * 100, 4)
#     data[total[0]].append(diagnostic_yield)

#   return render_template(
#     'report.html', group=group_id, samples=samples, data=itervalues(data))


@report.route('/report/<group_id>.pdf')
def report_pdf(group_id):
  # make a PDF from another view
  response = render_pdf(url_for('report.report_html', group_id=group_id))

  # check if the request is to download the file right away
  if 'dl' in request.args:
    fname = "coverage_report_%s.pdf" % group_id
    response.headers['Content-Disposition'] = 'attachment; filename=' + fname

  return response
