#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask.ext.script import Manager, Server

from chanjo_report.server.app import create_app

app = create_app()
manager = Manager(app)


manager.add_command('vagrant', Server(host='0.0.0.0', use_reloader=True))


if __name__ == '__main__':
    manager.run()
