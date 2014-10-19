# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from flask import Blueprint, render_template

from ...extensions import api

report_bp = Blueprint('report', __name__, template_folder='templates',
                      static_folder='static')


@report_bp.route('/')
def index():
  samples = api.samples()

  return render_template(
    'index.html',
    samples=samples
  )


@report_bp.route('/samples/<sample_id>')
def samples(sample_id):
  return render_template(
    'report.html',
    samples=api.samples().filter_by(id=sample_id),
    key_metrics=api.average_metrics().filter_by(sample_id=sample_id),
    diagnostic_yield=api.diagnostic_yield(sample_ids=(sample_id,)),
    genders=api.sex_checker(sample_ids=(sample_id,), include_coverage=True)
  )


@report_bp.route('/groups/<group_id>')
def groups(group_id):
  return render_template(
    'report.html',
    samples=api.samples().filter_by(group_id=group_id),
    key_metrics=api.average_metrics().filter_by(group_id=group_id),
    diagnostic_yield=api.diagnostic_yield(group_id=group_id),
    genders=api.sex_checker(group_id=group_id, include_coverage=True)
  )
