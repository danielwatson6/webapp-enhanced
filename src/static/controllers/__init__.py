import os
import inspect
import pkgutil
import importlib

from lib import utils

# Controllers to exclude from application
exclude = ('core', 'lib')

# Get all the controllers' module names
def package_names():
	return [name for _, name, _ in pkgutil.iter_modules(['controllers']) if not name in exclude]

# Import and get all the controller modules with given names
def package_contents(module_names):
	return [importlib.import_module('controllers.' + m) for m in module_names]

# Actually do both of the above, and get the controller from each module
def all_classes():
	classes = []
	for module in package_contents(package_names()):
		for name, obj in inspect.getmembers(module):
			if inspect.isclass(obj) and utils.lowercase(obj.__name__) in package_names():
				classes.append(obj)
	return classes
