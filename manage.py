#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask.ext.script import Manager

from chanjo_report.app import create_app

manager = Manager(create_app)


if __name__ == '__main__':
  manager.run()
