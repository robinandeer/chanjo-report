# -*- coding: utf-8 -*-
from datetime import datetime
import os


# Instance folder path, make it independent.
INSTANCE_FOLDER_PATH = os.path.expanduser('~/instance')

HTTP_METHODS = ['OPTIONS', 'GET', 'POST', 'PUT', 'DELETE']
PLURAL_METHODS = ['OPTIONS', 'GET', 'POST']
SINGLE_METHODS = ['OPTIONS', 'GET', 'PUT', 'DELETE']


def get_current_time():
  return datetime.utcnow()


def make_dir(dir_path):
  try:
    if not os.path.exists(dir_path):
      os.mkdir(dir_path)
  except Exception as e:
    raise e
