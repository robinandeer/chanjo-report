#!/usr/bin/env python
# -*- coding: utf-8 -*-

import importlib

from chanjo.sql.models import Sample
from flask import render_template, url_for, request, redirect

from . import app, db
from .settings import DEBUG


@app.route('/')
def index():
  return render_template('index.html')


@app.route('/demo')
def demo():
  return render_template('demo_report.html', debug=DEBUG)


@app.route('/report')
@app.route('/report/group/<group_id>')
@app.route('/report/samples/<sample_ids>')
def report(group_id=None, sample_ids=None):

  if sample_ids:
    # Prepare 'sample_ids'
    sample_ids = sample_ids.split(',')

  else:
    sample_query = db.query(Sample.id)
    if group_id:
      sample_query = sample_query.filter(Sample.group_id == group_id)

    samples = sample_query.all()

  further_info = []
  components_data = []
  component_ids = request.args.get('components')

  if not component_ids:
    return redirect(url_for('index'), code=302)

  for component_id in component_ids.split(','):
    print('Calculating values for: ' + component_id)
    import_path = 'chanjo_report.components.' + component_id
    component = importlib.import_module(import_path)
    data, info = component.index(db, group_id=group_id, sample_ids=sample_ids)

    components_data.append((component_id, data))

    if info:
      further_info.append((component_id, info))

  return render_template(
    'report.html',
    group=group_id,
    samples=sample_ids or [sample[0] for sample in samples],
    components=components_data,
    further_info=further_info,
    debug=DEBUG
  )
