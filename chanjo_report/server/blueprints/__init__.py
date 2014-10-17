# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from flask import Blueprint, render_template

report_bp = Blueprint('report', __name__, template_folder='templates')


@report_bp.route('/')
def index():
  return render_template('index.html')
