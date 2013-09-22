#!/usr/bin/env python

import os
import settings
from setuptools import setup, find_packages

setup(name=settings.name,
      version=settings.version,
      description=settings.description,
      author=settings.author,
      author_email=settings.email,
      url=settings.url,
      scripts=['we', 'settings.py'],
      include_package_data=True,
      package_data = {
      	'': ['*', '*.txt', '*.py', '*.yaml', '*.css', '*.js', '*.html']
      },
)
