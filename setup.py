#!/usr/bin/env python

import os
from setuptools import setup, find_packages

setup(name="Webapp Enhanced",
      version="0.0.3",
      author="Daniel Watson",
      author_email="watsondaniel6@gmail.com",
      description="Enhanced framework for Google App Engine",
      url="https://github.com/djwatt5/webapp-enhanced",
      license="MIT",
      
      # Adding packages
      include_package_data = True,
      packages=['static'],
      package_dir = {'static':'src/static'},
      package_data = {
        'static': ['*.*'],
      },
      
      scripts=['src/we'],
)
