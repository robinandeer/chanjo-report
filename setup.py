#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Based on https://github.com/pypa/sampleproject/blob/master/setup.py."""
import codecs
import os
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand
import sys

# if you are not using vagrant, just delete os.link directly,
# the hard link only saves a little disk space, so you should not care
# http://stackoverflow.com/a/22147112/2310187
if os.environ.get('USER', '') == 'vagrant':
    del os.link

# shortcut for building/publishing to Pypi
if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist bdist_wheel upload')
    sys.exit()


# this is a plug-in for setuptools that will invoke py.test
class PyTest(TestCommand):

    """Set up the py.test test runner."""

    user_options = [('pytest-args=', 'a', 'Arguments to pass to py.test')]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

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
with codecs.open(os.path.join(HERE, 'README.md'), encoding='utf-8') as f:
    LONG_DESCRIPTION = f.read()


setup(name='chanjo-report',
      # versions should comply with PEP440
      version='4.0.0',
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
      package_data={
          'chanjo_report': [
              'server/blueprints/report/static/*.css',
              'server/blueprints/report/static/vendor/*.css',
              'server/blueprints/report/templates/report/*.html',
              'server/blueprints/report/templates/report/layouts/*.html',
              'server/blueprints/report/templates/report/components/*.html',
              'server/translations/sv/LC_MESSAGES/*',
          ]
      },
      zip_safe=False,
      install_requires=[
          'setuptools',
          'chanjo>=3.0.2',
          'Flask-WeasyPrint',
          'cairocffi',
          'lxml>=3.0',
          'cffi',
          'Flask',
          'SQLAlchemy',
          'Flask-Babel',
          'tabulate'
      ],
      tests_require=['pytest'],
      cmdclass={'test': PyTest},
      # to provide executable scripts, use entry points
      entry_points={
          'chanjo.subcommands.3': ['report = chanjo_report.cli:report'],
          'chanjo_report.interfaces': [
              'html = chanjo_report.interfaces:render_html',
              'pdf = chanjo_report.interfaces:render_pdf'
          ]
      },
      # see: http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Developers',
          'Topic :: Software Development',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.3',
          'Programming Language :: Python :: 3.4',
          'Environment :: Console'
      ])
