import os
import re
import inspect
import pkgutil
import importlib

# Modules to exclude
exclude = ('core', 'lib')

# Get all the controllers' module names
def package_names():
	return [name for _, name, _ in pkgutil.iter_modules(['controllers']) if not name in exclude]

# Import and get all the controller modules with given names
def package_contents(module_names):
	return [importlib.import_module('controllers.' + m) for m in module_names]

# Determine if the given object should be added to the router
def should_route(obj):
	if inspect.isclass(obj):
		
		# Format the object's name to variable-like name
		lname = re.sub('([a-z0-9])([A-Z])', r'\1_\2', re.sub('(.)([A-Z][a-z]+)', r'\1_\2', obj.__name__)).lower()
		
		# TO-DO: Add upload and download classes
		return lname in package_names()


def all_classes():
	"""Return a list with all valid controllers.
	
	This is used by default in main.py to route all valid controllers.
	However, it is also possible to just list them individually.
	
	"""
	
	classes = []
	
	# Go through all modules in the controllers package
	for module in package_contents(package_names()):
		
		# Go through all objects in the module and
		# return the ones that are controllers
		for name, obj in inspect.getmembers(module):
			if should_route(obj):
				classes.append(obj)
	
	return classes	
