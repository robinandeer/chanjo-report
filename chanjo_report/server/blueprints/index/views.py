# -*- coding: utf-8 -*-
import logging

from chanjo.store.txmodels import Sample, Transcript
from flask import Blueprint, render_template

from chanjo_report.server.extensions import api

logger = logging.getLogger(__name__)
index_bp = Blueprint('index', __name__, template_folder='templates',
                     static_folder='static', static_url_path='/static/index')


@index_bp.route('/')
def index():
    sample_objs = api.query(Sample)
    tx_models = api.query(Transcript).distinct(Transcript.gene_id).limit(50)
    return render_template('index/index.html', samples=sample_objs,
                           transcripts=tx_models)
