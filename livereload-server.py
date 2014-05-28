#!/usr/bin/env python
# -*- coding: utf-8 -*-

from livereload import Server, shell
from chanjo_report import app

server = Server(app)


# Run a function
def alert():
  print('foo')

server.watch('chanjo_report/static/**', alert)

server.serve()
