#!/usr/bin/env python

from distutils.core import setup

setup(name='wwwc',
      version='0.1',
      description='Watching Wilmaa TV with Coop',
      author='DerCoop',
      author_email='dercoop@users.sourceforge.net',
      url='',
      long_description='short script to extract the TV stream from '\
                       'the Wilmaa-webpage.',
      license='GPL v2',
      packages=['wwwc'],
      data_files=[('wwwc/config', ['cfg/default_config.ini'])],
      scripts=['watch_wilmaa.py']
      )
