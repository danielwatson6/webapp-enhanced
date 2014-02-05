"""

TO-DO's:
- Make the put() code in BlobModel. (EDIT: It's done in ModelController.)
- Fix the delete() issue (sometimes the page needs to be refreshed twice
                          to see the changes)
"""


import os
import re
import cgi
import json
import urllib
import logging

import webapp2
import jinja2

from lib.xml import dicttoxml as xml

from lib import utils
from google.appengine.ext import ndb, blobstore
from google.appengine.ext.webapp import blobstore_handlers


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
		
	def del_cookie(self, *a, **kw):
		"""Delete a cookie from the client."""
		self.delete_cookie(*a, **kw)
	
	def set_content(self, t):
		"""Shortcut to set the Content-Type header."""
		self.headers["Content-Type"] = t


class Application(webapp2.WSGIApplication):
	"""Application class.
	
	An application instance is created in the main script,
	where settings may also be configured.
	
	Unlike the default Application class, this class
	also handles the mapping of paths to controllers.
	
	"""
	
	# Initialize the custom Request and Response classes.
	request_class = Request
	response_class = Response
	
	# NOTE: Unlike the default Application class, this will not
	# initialize the application (see initialize() method). This
	# only handles the mapping of classes to their paths.
	def __init__(self, controllers):
		self._controller_map = []
		
		for c in controllers:
			
			# Check if a path is already specified:
			if c.__doc__:
				current = c.__doc__
			else:
				
				# Set a default path instead:
				current = '/' + utils.lowercase(c.__name__)
				if c._supports_model: current += 's'
			
			# Add the mappings:
			self._controller_map.append((current + r'(?:\.(.+))?', c)) # Index page (extension allowed).
			
			# Extra maps for controllers linked to models:
			if c._supports_model and not c._blob_class:
				self._controller_map.append((current + r'/new', c)) # Create page.
				self._controller_map.append((current + r'/([0-9]+)(?:\.(.+))?', c)) # Show page (extension allowed).
				self._controller_map.append((current + r'/([0-9]+)/edit', c)) # Edit page.
	
	
	def set_jinja_options(self, **kw):
		"""Change any Jinja2 options."""
		global jinja_env
		jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), **kw)
	
	def initialize(self, **kw):
		"""Actually initialize the Application instance."""
		super(Application, self).__init__(self._controller_map, **kw)


class BaseController(webapp2.RequestHandler):
	"""The parent controller.
	
	Most of the new functionality of all the controllers
	is set in this class.
	
	"""
	
	# The Application class uses this to determine whether to add
	# the extra mappings for controllers linked to models.
	_supports_model = False
	
	# Upload and download classes are model-supporting, but do not
	# need the extra mappings.
	_blob_class = False
	
	
	### Methods child classes may override:
	
	def authorized(self):
		"""If not authorized, send a 401 error."""
		return True
	
	def index(self, *a):
		"""When showing the index.html page."""
		pass
	
	def init(self, *a):
		"""Before any and all requests."""
		pass
	
	
	### RESTful methods:
	
	def get(self, *a):
		"""Handle GET requests."""
		self.init(*a)
	
	def post(self, *a):
		"""Handle POST requests."""
		self.init(*a)
	
	def put(self, *a):
		"""Handle PUT requests."""
		self.init(*a)
	
	def delete(self, *a):
		"""Handle DELETE requests."""
		self.init(*a)
	
	
	### Functional methods:
	
	def initialize(self, *a, **kw):
		"""Default actions."""
		super(BaseController, self).initialize(*a, **kw)
		
		# Set the variable-like name for the class:
		self._name = utils.lowercase(self.__class__.__name__)
		
		self._params = {}		# Params for the views
		
		# Miscellaneous flags:
		self._flags = {
			"render": True,
		}
	
	def get_flag(self, f):
		"""Get the specified flag's value."""
		try:
			return self._flags[f]
		except KeyError:
			logging.exception("Unknown flag: `%s`" % f)
			raise
	
	def set_flag(self, f, value):
		"""Change a flag's value, or add a new flag."""
		self._flags[f] = value
		return value
	
	# TO-DO: Automate this based on form
	def get_data(self, *a):
		"""Fetch arguments and their values from the request."""
		return {i: self.request.get(i) for i in list(a)}
	
	def send_data(self, **params):
		"""Add variables to the views."""
		self._params = dict(self._params.items() + dict(params).items())
	
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
		data = self.get_data("_method")
		if data['_method'] == 'PUT':
			logging.info("Intercept: PUT" )
			self.put(*a)
			return True
		if data['_method'] == 'DELETE':
			logging.info("Intercept: DELETE")
			self.delete(*a)
			return True
	
	

class Controller(BaseController):
	"""Controller for simple pages.
	
	Default controllers only include a home page.
	
	"""
	
	def get(self, *a):
		"""Handle GET requests.
		This calls the authorized() and index() methods.
		"""
		super(Controller, self).get(*a)
		
		# Check for authorization:
		if not self.authorized():
			self.abort(401)
		
		# Actions from index method:
		self.index(*a)
		
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
		
		# Select mode and use corresponding methods:
		mode = self.get_mode()
		if mode == "index":
			self.get_resources()
			self.index(*a)
		elif mode == "new":
			self.new(*a)
		elif mode == "show":
			resource = self.get_resource(list(a)[0])
			self.show(*a)
		elif mode == "edit":
			self.get_resource(list(a)[0])
			self.edit(*a)
		
		# Check if render flag is on:
		if self._flags["render"]:
			self.render_appropriate(mode, **self._params)
	
	def post(self, *a):
		BaseController.post(self, *a)
		
		if self.intercept(*a): return 	# Catches PUT and DELETE methods
		
		form = self.model.form
		assert form is not None
		
		data = self.get_data(*form.keys())
		
		try:
			new_entity = self.model(validate=True, **data)
			new_entity.put()
			return self.redirect('/%ss/%s' % (self._name, new_entity.get_id()))
		
		# NOTE: An IOError is raised when validation fails.
		except IOError:
			self.redirect('/%ss/new' % self._name)
	
	def put(self, *a):
		BaseController.put(self, *a)
		
		form = self.model.form
		assert form is not None
		
		data = self.get_data(*form.keys())
		
		resource = self.get_resource(list(a)[0])
		if resource is not None:
			self.abort(404)
		
		for name, value in data.items():
			if value != getattr(resource, name):
				try:
					for validator in form[name]:
						value = validator(value)
					setattr(resource, name, value)
				except IOError: pass
		resource.put()
		return self.redirect(resource.link())
	
	# TO-DO: Refresh the index page; resource still 'appears' after redirect.
	def delete(self, *a):
		"""Handle DELETE requests.
		Will destroy the current resource.
		"""
		self._flags["render"] = False
		resource = self.get_resource(list(a)[0])
		resource.destroy()
		logging.info("Deleted resource. Redirecting to /%ss" % self._name)
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
		
		# Resource page:
		elif mode == "show":
			self.response.render(self._name + '/show.html', **params)
		
		# Resource edit page:
		elif mode == "edit":
			self.response.render(self._name + '/edit.html', **params)
		
		# Any other page:
		else: self.response.render(self._name + '/' + mode + '.html', **params)
	
	def get_resource(self, resource_id):
		"""Get the entity from the given id, stop if it doesn't exist,
		otherwise add it to the template."""
		
		resource = ndb.Key(self.model.__name__, int(resource_id)).get()
		if not resource:
			self.abort(404)
		self._params['resource'] = resource
		return resource
	
	### Methods child classes may override:
	
	def new(self):
		"""When displaying new.html."""
		pass
	
	def create(self):
		"""When creating an entity.
		Called on a POST request.
		"""
		pass
	
	def show(self, *a):
		"""When displaying show.html."""
		pass
	
	def edit(self, *a):
		"""When displaying edit.html."""
		pass
	
	def update(self, *a):
		"""When modifying an entity.
		Called on a PUT request.
		"""
		pass
	
	def get_resources(self):
		"""Get the resources from the linked model.
		Called when displaying index.html.
		"""
		return self.model.all()


# TO-DO: Implement this on the default Model Controller class.
# TO-DO: Add support for multiple blobs.
class BlobController(ModelController):
	"""Model Controller with blob support.
	
	BlobController classes are only used to link with the model
	and to instruct the use of the Upload Controller.
	
	"""
	
	def get(self, *a):
		"""Handle GET requests.
		This will always send the upload url for the HTML form.
		"""
		upload_url = blobstore.create_upload_url('/%ss/upload' % self._name)
		self.send_data(upload_url = upload_url)
		super(BlobController, self).get(*a)
	
	def post(self, *a):
		"""Handle POST requests.
		Since the Upload Controller handles the POST requests,
		nothing is done here.
		"""
		BaseController.post(self, *a)
		if self.intercept(*a): return 	# Catches PUT and DELETE methods


# TO-DO: Major edit along ModelController's POST and PUT.
# TO-DO: Support for PUT requests.
class UploadController(blobstore_handlers.BlobstoreUploadHandler, ModelController):
	"""Controller that handles POST requests for the Blob Controller.
	
	The UploadController classes require a link with their Blob Controller.
	
	"""
	_blob_class = True
	
	# Controller that the class supports:
	default_class = None
	
	def upload(self):
		"""Upload a blob to the Blobstore."""
		try:
			return self.get_uploads()[0]
		except IndexError: pass
	
	def init(self):
		self.model = self.default_class.model
	
	def get(self, *a):
		self.error(405)
	
	def post(self, *a):
		BaseController.post(self, *a)
		
		if self.intercept(*a): return 	# Catches PUT and DELETE methods
		
		form = self.model.form
		if form is not None:
			data = self.get_data(*form.keys())
			
		upload = self.upload()
		if upload:
			data['blob'] = str(upload.key())
			new_entity = self.model(validate=True, **data)
			new_entity.put()
			
			return self.redirect('/%ss/%s' % (self._name, new_entity.get_id()))
		
		self.redirect('/%ss/new' % self._name)


# TO-DO: Use a single download controller for everything,
# instead of having one per Blob Controller.
class DownloadController(blobstore_handlers.BlobstoreDownloadHandler, ModelController):
	"""Controller that handles file downloads.
	
	Download Controllers also require a link with their Blob Controller.
	
	"""
	_blob_class = True
	
	# Controller that the class supports:
	default_class = None
	
	def download(self):
		"""When downloading files from the Blobstore."""
		pass
	
	def init(self, *a):
		self.model = self.default_class.model
	
	def get(self, resource, *a):
		BaseController.get(self, resource)
		entity = self.model.get_by_id(long(resource))
		resource = str(urllib.unquote(entity.blob))
		blob_info = blobstore.BlobInfo.get(resource)
		self.send_blob(blob_info)


class AJAXController(BaseController):
	"""Controller for AJAX requests
	
	AJAX Controllers don't include any templates.
	
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
		self.GET(*a)
	
	def post(self, *a):
		super(AJAXController, self).post(*a)
		self.POST(*a)
	
	def put(self, *a):
		super(AJAXController, self).put(*a)
		self.PUT(*a)
	
	def delete(self, *a):
		super(AJAXController, self).delete(*a)
		self.DELETE(*a)

