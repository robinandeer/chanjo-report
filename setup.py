#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Based on https://github.com/pypa/sampleproject/blob/master/setup.py."""
from __future__ import unicode_literals
from codecs import open
import os
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand
import sys

# shortcut for building/publishing to Pypi
if sys.argv[-1] == 'publish':
  os.system('python setup.py sdist bdist_wheel upload')
  sys.exit()


# this is a plug-in for setuptools that will invoke py.test
class PyTest(TestCommand):

  """Set up the py.test test runner."""

  def finalize_options(self):
    """Set options for the command line."""
    TestCommand.finalize_options(self)
    self.test_args = []
    self.test_suite = True

  def run_tests(self):
    """Execute the test runner command."""
    # import here, because outside the required eggs aren't loaded yet
    import pytest
    sys.exit(pytest.main(self.test_args))

# get the long description from the relevant file
HERE = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(HERE, 'README.md'), encoding='utf-8') as f:
  LONG_DESCRIPTION = f.read()


setup(name='chanjo-report',
      # versions should comply with PEP440
      version='0.0.1',
      description='Automatically render coverage reports from Chanjo ouput',
      long_description=LONG_DESCRIPTION,
      # what does your project relate to?
      keywords='chanjo-report development',
      author='Robin Andeer',
      author_email='robin.andeer@scilifelab.se',
      license='MIT',
      # the project's main homepage
      url='https://github.com/robinandeer/chanjo-report',
      packages=find_packages(exclude=('tests*', 'docs', 'examples')),
      # if there are data files included in your packages
      include_package_data=True,
      zip_safe=False,
      package_data={
        '': ['README.md', 'LICENSE', 'AUTHORS'],
      },
      install_requires=[
        'setuptools',
        'chanjo>=2.1.0',
        'Flask-WeasyPrint',
        'Flask-Assets',
        'pyscss',
        'cairocffi',
        'toml',
        'lxml>=3.0',
        'cffi',
        'Flask',
        'SQLAlchemy',
        'Flask-Babel',
        'tabulate',
      ],
      tests_require=[
        'pytest',
      ],
      cmdclass=dict(
        test=PyTest,
      ),
      # to provide executable scripts, use entry points
      entry_points={
        'chanjo.subcommands': [
          'report = chanjo_report.cli:report',
        ],
        'chanjo_report.interfaces': [
          'tabular = chanjo_report.interfaces:render_tabular',
          'html = chanjo_report.interfaces:render_html',
          'pdf = chanjo_report.interfaces:render_pdf',
        ],
      },
      # see: http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        # how mature is this project?
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',
        # indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development',
        # pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',
        # specify the Python versions you support here.
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Environment :: Console',
      ])
