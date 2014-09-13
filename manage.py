#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask.ext.script import Manager, Server
from chanjo_report.app import create_app

manager = Manager(create_app)
manager.add_command('vagrant', Server(host='0.0.0.0', use_reloader=True))
manager.add_option(
  '-c', '--config', dest='config', required=False, help='config file path')


if __name__ == '__main__':
  manager.run()
