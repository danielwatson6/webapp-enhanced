import os
import re
import cgi
import json
import urllib
import logging
import importlib

import webapp2
import jinja2

from lib.xml import dicttoxml as xml

from google.appengine.ext import ndb, blobstore


# Jinja2 variables
template_dir = os.path.join(os.path.dirname(__file__), '..', "views")
jinja_env    = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir))


def render_str(template, **params):
	"""Return a rendered Jinja2 template."""
	return jinja_env.get_template(template).render(params)


class Request(webapp2.Request):
	"""Custom Request class for controllers.
	
	The custom request class is used to add more
	functionality to controllers, and to keep
	the project's structure at the same time.
	
	"""
	
	def add_head(self, head, value):
		"""Add a header to the request."""
		self.headers[head] = value
	
	def get_cookie(self, name, default = None):
		"""Get a specified cookie's value."""
		return self.cookies.get(name, default)
	
	def get_cookies(self):
		"""Get a list with every existing cookie."""
		cookies = []
		for i in self.cookies.items():
			cookies.append((i[0], i[1]))
		return cookies
	
	def get_extension(self):
		"""If the current path has one, get the file extension."""
		separation = self.path.split('.')
		if len(separation) > 1:
			return separation[-1]


class Response(webapp2.Response):
	"""Custom Response class for controllers.
	
	Like the custom Request class, this class
	includes more functionality for the controllers
	and maintains the project's structure.
	
	"""
	
	def add_head(self, head, value):
		"""Add a header to the response."""
		self.headers[head] = value
	
	def render(self, filename, **params):
		"""Render and display a template."""
		html = render_str(filename, ** params)
		self.out.write(html)
	
	def set_content(self, t):
		"""Shortcut to set the Content-Type header."""
		self.headers["Content-Type"] = t


class webapp_enhanced(webapp2.WSGIApplication):
	"""Application class.
	
	An application instance is created in the main script,
	where settings may also be configured.
	
	Unlike the default Application class, this class
	also handles the mapping of paths to controllers.
	
	"""
	
	# Initialize the custom Request and Response classes.
	request_class = Request
	response_class = Response
	
	def __init__(self):
		"""NOTE: to actually start the application, use the start() method.
		
		By starting the application after creating the class instance,
		routing and settings don't need to be all clumped in this method.
		
		"""
		self._controller_map = []
	
	def start(self, **kw):
		"""Grab the controller map and start the application."""
		super(webapp_enhanced, self).__init__(self._controller_map, **kw)
	
	def add_route(self, path_re, controller):
		"""Add a custom path to the given controller.
		
		Unlike the route() method, the path regexp must be specified here.
		
		"""
		self._controller_map.append((path_re, controller))
	
	def route(self, controllers):
		"""Determine the path for a controller and route it.
		
		If the controllers do not have their path specified
		(they should be a regexp below the class name, as documentation)
		this method will give it the class name, formatted to lowercase.
		
		Instances of ModelController are given more paths to work
		accordingly with the class, and, if the default path is not
		specified, it will be the formatted, pluralized class name.
		
		NOTE: Normal controllers, as well as index & show pages for
		      ModelController instances are allowed to have extensions
		      for XML and JSON compatibility. This may be turned off
		      by setting the allow_extensions variable to false.
		
		"""
		for c in controllers:
			
			# Check if a path is already specified:
			if c.__doc__:
				current = c.__doc__
			else:
				
				# Set a default path instead:
				current = '/' + _lowercase(c.__name__)
				if c._supports_model: current += 's'
			
			# Check for extensions
			if c.allow_extensions:
				e = r'(?:\.(.+))?'
			
			self.add_route(current + e, c) # Index page
			
			# Missing routes for model controllers:
			if c._supports_model:
				self.add_route(current + r'/new', c) # Create page
				self.add_route(current + r'/([0-9]+)' + e, c) # Show page
				self.add_route(current + r'/([0-9]+)/edit', c) # Edit page
	
	
	def set_jinja2_options(self, **kw):
		"""Change any Jinja2 settings.
		
		See the Jinja2 documentation for details: http://jinja.pocoo.org/docs/
		
		"""
		global jinja_env
		jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), **kw)
	
	def set_views_folder(self, *path):
		"""Change the default location of the views folder.
		
		Multiple arguments are used to support os.path.join.
		
		"""
		global template_dir
		template_dir = os.path.join(os.path.dirname(__file__), *path)
		self.set_jinja2_options()


class BaseController(webapp2.RequestHandler):
	"""The parent controller.
	
	Most of the new functionality of all the controllers
	is set in this class.
	
	"""
	
	# The webapp_enhanced class uses this to determine whether to add
	# the extra paths for controllers linked to models.
	_supports_model = False
	
	# This is used to determine whether to add the option of allowing
	# file extensions in the controller's path.
	allow_extensions = True
	
	### Methods child classes may override:
	
	def index(self):
		"""When showing the index.html page."""
	
	def init(self):
		"""Before any and all requests."""
	
	def authorized(self):
		"""Determine if the user has access to the controller.
		This method is similar to deny_access(), but it is meant to
		deny access to the entire controller and to be triggered by
		this module.
		"""
		return True
	
	### RESTful methods:
	
	def get(self, *a):
		"""Handle GET requests."""
		self.init()
	
	def post(self, *a):
		"""Handle POST requests."""
		self.init()
	
	def put(self, *a):
		"""Handle PUT requests."""
		self.init()
	
	def delete(self, *a):
		"""Handle DELETE requests."""
		self.init()
	
	
	### Functions:
	
	def initialize(self, *a, **kw):
		"""Default __init__ actions that are handled by this class."""
		super(BaseController, self).initialize(*a, **kw)
		
		# Set the variable-like name for the class:
		self._name = _lowercase(self.__class__.__name__)
		
		self._params = {}		# Arguments that pass to templates
		
		# Arguments used only by the server:
		self._flags = {
			"render": True,
			"errors": None,
		}
	
	def deny_access(self):
		"""Destroy the response and send an unauthorized error.
		If you wish to block the entire controller, override the
		authorized() method instead.
		"""
		self.abort(401)
	
	def get_flag(self, f):
		"""Get the specified flag's value."""
		try:
			return self._flags[f]
		except KeyError: pass
	
	def set_flag(self, f, value):
		"""Change a flag's value, or add a new flag."""
		self._flags[f] = value
		return value
	
	def get_data(self, *params):
		"""Fetch arguments and their values from the request."""
		return {i: self.request.get(i) for i in list(params)}
	
	def send_data(self, **params):
		"""Add data that can be used by the views."""
		self._params = dict(self._params.items() + dict(params).items())
	
	def send_data_dict(self, d):
		"""Same as send_data(), but takes in a dictionary
		instead of multiple keyword args."""
		self.send_data(**d)
	
	def render_json(self, d):
		"""Render and display a data structure as JSON."""
		self.set_flag("render", False)
		self.response.headers["Content-Type"] = "application/json"
		json_txt = json.dumps(d)
		self.response.out.write(json_txt)
	
	def render_xml(self, d):
		"""Render and display a data structure as XML."""
		self.set_flag("render", False)
		self.response.headers["Content-Type"] = "application/xml"
		xml_txt = xml.dicttoxml(d)
		self.response.out.write(xml_txt)
	
	def intercept(self, *a):
		"""Check for a hidden form to perform appropriate method.
		Called by post().
		"""
		method = self.request.get("_method")
		if method == 'PUT':
			logging.info("Intercept: PUT" )
			self.put(*a)
			return True
		if method == 'DELETE':
			logging.info("Intercept: DELETE")
			self.delete(*a)
			return True


class Controller(BaseController):
	"""Controller for simple pages.
	
	Default controllers have a single path.
	
	"""
	
	def get(self, *a):
		"""Handle GET requests.
		"""
		super(Controller, self).get(*a)
		
		# Check for authorization:
		if not self.authorized(): self.abort(401)
		
		# Actions from index method:
		self.index()
		
		# Check if render flag is on:
		if self._flags["render"]:
			self.response.render(self._name + '/index.html', **self._params)


class ModelController(BaseController):
	"""Controller with full model support.
	
	Model Controllers include index and new pages,
	as well as show and edit pages for each resource.
	
	"""
	_supports_model = True
	
	# Model that the class supports:
	model = None
	
	
	def get(self, *a):
		"""Handle GET requests."""
		super(ModelController, self).get(*a)
		
		# Check for authorization:
		if not self.authorized(): self.abort(401)
		
		# Select mode and use corresponding methods:
		mode = self.get_mode()
		if mode == "index":
			self.get_resources()
			self.index()
		elif mode == "new":
			self.new()
		elif mode == "show":
			self.get_resource(list(a)[0])
			self.show()
		elif mode == "edit":
			self.get_resource(list(a)[0])
			self.edit()
		
		# Check if render flag is on:
		if self._flags["render"]:
			self.render_appropriate(mode, **self._params)
	
	def post(self, *a):
		BaseController.post(self, *a)
		
		# Check for authorization:
		if not self.authorized(): self.abort(401)
		
		if self.intercept(*a): return 	# Catches PUT and DELETE methods
		
		form = self.model.form
		assert form is not None
		
		data = self.get_data(*form.keys())
		self.set_flag('inputs', data)
		
		try:
			new_entity = self.model(validate=True, **data)
			new_entity.put()
			self.create(new_entity)		# This is called in child classes after default stuff is done.
			return self.redirect(new_entity.link())
		
		# NOTE: An IOError is raised when validation fails.
		except IOError:
			self.set_flag('errors', self.model.get_errors(form, data))
			self.create(None)
			self.get(*a)
	
	def put(self, *a):
		BaseController.put(self, *a)
		
		# Check for authorization:
		if not self.authorized(): self.abort(401)
		
		form = self.model.form
		assert form is not None
		
		data = self.get_data(*form.keys())
		
		resource = self.get_resource(list(a)[0])
		if resource is None:
			self.abort(404)
		
		for name, value in data.items():
			if value != getattr(resource, name):
				try:
					for validator in form[name]:
						value = validator(value)
					setattr(resource, name, value)
				except IOError: pass
		resource.put()
		self.update(resource)			# This is the overriden actions after updating the resource.
		return self.redirect(resource.link())
	
	# TO-DO: Refresh the index page; resource still 'appears' after redirect.
	def delete(self, *a):
		"""Handle DELETE requests.
		Will destroy the current resource.
		"""
		
		# Check for authorization:
		if not self.authorized(): self.abort(401)
		
		self._flags["render"] = False
		resource_id = self.request.get("_resource_id")
		resource = self.get_resource(resource_id)
		if resource:
			self.destroy(resource)		# Overridable
			resource.destroy()
			logging.info("DELETE %r" % resource)
		self.redirect('/%ss' % self._name)
	
	def get_mode(self):
		"""Get the mode string depending on the current page.
		Used in get() and render_appropriate() to select the
		appropriate methods and templates.
		"""
		path = self.request.path
		if path[:-1] == '/' + self._name or path[:-1] == '/' + self._name + 's':
			return "index"
		elif re.match(r'([0-9]+)(?:\.(.+))?', path.split('/')[-1]):
			return "show"
		else:
			return path.split('/')[-1]
	
	def render_appropriate(self, mode, **params):
		"""Render and display the appropriate template."""
		
		# Index page:
		if mode == "index":
			resources = self.get_resources()
			self.response.render(self._name + '/index.html', resources = resources, **params)
		
		# Resoucrce page:
		elif mode == "show":
			self.response.render(self._name + '/show.html', **params)
		
		# Resource edit page:
		elif mode == "edit":
			self.response.render(self._name + '/edit.html', **params)
		
		# Any other page:
		else: self.response.render(self._name + '/' + mode + '.html', **params)
	
	def get_resource(self, resource_id):
		"""Get the entity from the given id, stop if it doesn't exist,
		otherwise add it to the template and to self."""
		
		resource = ndb.Key(self.model.__name__, int(resource_id)).get()
		if not resource:
			self.abort(404)
		self._params['resource'] = resource
		self.resource = resource
		return resource
	
	### Methods child classes may override:
	
	def new(self):
		"""When displaying new.html."""
	
	def show(self):
		"""When displaying show.html."""
	
	def edit(self):
		"""When displaying edit.html."""
	
	def create(self, resource):
		"""When creating an entity.
		Called on a POST request.
		"""
	
	def update(self, resource):
		"""When modifying an entity.
		Called on a PUT request.
		"""
	
	def destroy(self, resource):
		"""When attempting to destroy an entity.
		Called on DELETE request.
		"""
	
	def get_resources(self):
		"""Get the resources from the linked model.
		Called when displaying index.html.
		"""
		return self.model.all()


class AJAXController(BaseController):
	"""Controller for AJAX requests
	
	AJAX Controllers don't work with views.
	
	"""
	
	def initialize(self, *a, **kw):
		BaseController.initialize(self, *a, **kw)
		self._flags["render"] = False
	
	
	### Methods child classes may override:
	
	def GET(self, *a):
		"""Actions for GET requests."""
		pass
	
	def POST(self, *a):
		"""Actions for POST requests."""
		pass
	
	def PUT(self, *a):
		"""Actions for PUT requests."""
		pass
	
	def DELETE(self, *a):
		"""Actions for DELETE requests."""
		pass
	
	
	### Add the methods above to the default ones:
	
	def get(self, *a):
		super(AJAXController, self).get(*a)
		
		# Check for authorization:
		if not self.authorized(): self.abort(401)
		
		self.GET(*a)
	
	def post(self, *a):
		super(AJAXController, self).post(*a)
		
		# Check for authorization:
		if not self.authorized(): self.abort(401)
		
		self.POST(*a)
	
	def put(self, *a):
		super(AJAXController, self).put(*a)
		
		# Check for authorization:
		if not self.authorized(): self.abort(401)
		
		self.PUT(*a)
	
	def delete(self, *a):
		super(AJAXController, self).delete(*a)
		
		# Check for authorization:
		if not self.authorized(): self.abort(401)
		
		self.DELETE(*a)


# This is used within the module.
def _lowercase(s):
	"""Convert class-like names to varliable-like names."""
	s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', s)
	return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
