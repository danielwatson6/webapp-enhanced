#!/usr/bin/env python

import os
from setuptools import setup, find_packages

setup(name="webapp-enhanced",
	  version="1.0.1",
	  author="Daniel Watson",
	  author_email="watsondaniel6@gmail.com",
	  url="https://github.com/djwatt5/webapp-enhanced",
	  license="MIT",
	  description="Enhanced library for Google App Engine",
	  long_description="""Webapp Enhanced is a library meant to improve web development in Google App Engine.
The key elements in Webapp Enhanced are: RESTful methods, an MVC architecture, and
scripts with code templates ready to generate.""",
	  
	  include_package_data=True,
	  scripts=['src/we'],
	  packages=['static'],
	  package_dir={'static':'src/static'},
	  package_data={
		'static': ['*.*'],
	  },
)