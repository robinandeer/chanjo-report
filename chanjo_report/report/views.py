# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
from codecs import open

from chanjo.store import Block, BlockData, IntervalData, Sample
from flask import Blueprint, current_app, render_template, request, url_for
from flask_weasyprint import render_pdf
import sqlalchemy as sqa

from .._compat import zip, itervalues
from ..extensions import api

report = Blueprint(
  'report', __name__, template_folder='templates', static_folder='static')


def load_list(list_path):
  with open(list_path, 'r', encoding='utf-8') as handle:
    return [line.rstrip() for line in handle.readlines()]


@report.route('/report/<group_id>')
@report.route('/report/samples/<sample_ids>')
def report_html(group_id=None, sample_ids=None):
  # load superblock ids from gene list file
  if 'CHANJO_SUPERBLOCK_PANEL' in current_app.config:
    superblock_ids = load_list(current_app.config['CHANJO_SUPERBLOCK_PANEL'])
  else:
    raise TypeError(
      "Missing 'report/superblock_panel' variabel in 'chanjo.toml'")

  # build base queries (fetch data on ALL samples)
  samples = api.query(Sample.id, Sample.cutoff)

  # build base queries for average coverage and completeness
  metrics = api.query(
    BlockData.sample_id,
    sqa.func.avg(BlockData.coverage),
    sqa.func.avg(BlockData.completeness)
  ).join(BlockData.parent)\
   .filter(Block.superblock_id.in_(superblock_ids))\
   .group_by(BlockData.sample_id)

  # build base queries for the total number of annotated blocks
  count = sqa.func.count(BlockData.sample_id)
  total_blocks = api.query(BlockData.sample_id, count)\
                         .join(BlockData.parent)\
                         .filter(Block.superblock_id.in_(superblock_ids))\
                         .group_by(BlockData.sample_id)

  if sample_ids:
    sample_list = sample_ids.split(',')

    # optionally limit by a list of samples
    samples = samples.filter(Sample.id.in_(sample_list))
    metrics = metrics.filter(BlockData.sample_id.in_(sample_list))
    total_blocks = total_blocks.filter(BlockData.sample_id.in_(sample_list))

  elif group_id:
    # ... or limit to a group of samples
    samples = samples.filter(Sample.group_id == group_id)
    # inner join 'Sample' and filter by the 'group_id'
    metrics = metrics.filter(BlockData.group_id == group_id)
    # do the same for diagnostic yield calculation
    total_blocks = total_blocks.filter(
      BlockData.group_id == group_id)

  # extend total set count query to include only perfectly covered blocks
  covered_blocks = total_blocks.filter(BlockData.completeness == 1)

  # unless sample ids or group id was submitted, all samples are included
  # let's assemble the final results
  aggregate = zip(
    sorted(samples.all()),
    metrics.all(),
    total_blocks.all(),
    covered_blocks.all()
  )

  panel_caption = current_app.config.get('CHANJO_PANEL_CAPTION', 'gene panel')
  data = []
  sample_ids = []
  for sample, metric, total_blocks, covered_blocks in aggregate:
    # calculate diagnostic yield by dividing fully covered blocks by all blocks
    diagnostic_yield = round(
      covered_blocks[1] / total_blocks[1] * 100, 4)

    sample_ids.append(sample[0])
    data.append((
      sample[0],                  # sample id
      sample[1],                  # cutoff
      round(metric[1], 4),        # coverage
      round(metric[2] * 100, 4),  # completeness, %
      diagnostic_yield            # diagnostic yield
    ))

    # make sure we are not out of sync
    assert sample[0] == metric[0]
    assert metric[0] == total_blocks[0]
    assert total_blocks[0] == covered_blocks[0]

  return render_template(
    'report.html', samples=sample_ids, data=data, caption=panel_caption)


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
