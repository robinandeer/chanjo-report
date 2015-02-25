# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from chanjo.store import BlockData, IntervalData
from flask import (abort, Blueprint, current_app, render_template, request,
                   url_for)
from flask_weasyprint import render_pdf

from ...extensions import api

report_bp = Blueprint('report', __name__, template_folder='templates',
                      static_folder='static', static_url_path='/static/report')


@report_bp.route('/')
def index():
  sample_models = api.samples()

  return render_template('report/index.html', samples=sample_models)


@report_bp.route('/samples/<filter_id>')
def samples(filter_id):
  superblock_ids = current_app.config.get('CHANJO_PANEL')
  if superblock_ids:
    data_class = BlockData
  else:
    data_class = IntervalData

  return render_template(
    'report/report.html',
    samples=api.samples().filter_by(id=filter_id),
    key_metrics=api.average_metrics(superblock_ids=superblock_ids)\
                   .filter(data_class.sample_id == filter_id),
    diagnostic_yield=api.diagnostic_yield(sample_ids=(filter_id,),
                                          superblock_ids=superblock_ids),
    genders=api.sex_checker(sample_ids=(filter_id,), include_coverage=True)
  )


@report_bp.route('/groups/<filter_id>')
def groups(filter_id):
  superblock_ids = current_app.config.get('CHANJO_PANEL')
  if superblock_ids:
    data_class = BlockData
  else:
    data_class = IntervalData

  return render_template(
    'report/report.html',
    samples=api.samples().filter_by(group_id=filter_id),
    key_metrics=api.average_metrics(superblock_ids=superblock_ids)\
                   .filter(data_class.group_id == filter_id),
    diagnostic_yield=api.diagnostic_yield(group_id=filter_id,
                                          superblock_ids=superblock_ids),
    genders=api.sex_checker(group_id=filter_id, include_coverage=True)
  )


@report_bp.route('/<route>/<filter_id>.pdf')
def pdf(route, filter_id):
  # make a PDF from another view
  if route in ('samples', 'groups'):
    response = render_pdf(url_for("report.{}".format(route),
                          filter_id=filter_id))
  else:
    return abort(404)

  # check if the request is to download the file right away
  if 'dl' in request.args:
    fname = "coverage-report_{}.pdf".format(filter_id)
    response.headers['Content-Disposition'] = 'attachment; filename=' + fname

  return response
