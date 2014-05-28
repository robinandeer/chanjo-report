#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from logging.handlers import RotatingFileHandler

from chanjo_report import app
from chanjo_report.settings import DEBUG


if __name__ == '__main__':

  if DEBUG:
    # Run in development mode

    handler = RotatingFileHandler(
      'flask-server.log', maxBytes=1024 * 1024 * 100, backupCount=20)
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.INFO)
    log.addHandler(handler)

    app.run('localhost', port=8080)

  else:
    # Run in production mode
    app.run('0.0.0.0', port=80)
