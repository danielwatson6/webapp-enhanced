import os
import re
import cgi
import json
import urllib
import logging

import webapp2
import jinja2

from lib import utils

from google.appengine.ext import ndb, blobstore
from google.appengine.ext.webapp import blobstore_handlers


# Initialize global variables
template_folder = os.path.join(os.path.dirname(__file__), '..', "views")
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_folder))


# Custom request object used by controllers
class Request(webapp2.Request):
	
	# Add request header
	def add_head(self, head, value):
		self.headers[head] = value
	
	# (Overriden) Get a specified argument from the request
	def get(self, arg, escape = False, **kw):
		r = webapp2.Request.get(self, arg, **kw)
		if escape and r:
			return cgi.escape(r, quote = True)
		return r
	
	# Get a specified cookie's value
	def get_cookie(self, name, default = None):
		return self.cookies.get(name, default)
	
	# Get a list of all cookies
	def get_cookies(self):
		cookies = []
		for i in self.cookies.items():
			cookies.append((i[0], i[1]))
		return cookies


# Custom response object used by controllers
class Response(webapp2.Response):
	
	# Add response header
	def add_head(self, head, value):
		self.headers[head] = value
	
	# Render an html template
	def render(self, filename, **params):
		filename = os.path.join(*filename.split('/'))
		html = jinja_env.get_template(filename).render(params)
		self.out.write(html)
	
	# Write a dict as a json string
	def render_json(self, d):
		json_txt = json.dumps(d)
		self.out.write(json_txt)
	
	# Delete a cooie from the client
	def del_cookie(self, *a, **kw):
		self.delete_cookie(*a, **kw)
	
	# Set the output content type
	def set_content(self, t):
		self.headers["Content-Type"] = t


# Error thrown by controllers when no routing path is found
class MissingPathError(Exception):
	pass

# Application class
class Application(webapp2.WSGIApplication):
	
	# Initialize the custom request/response classes
	request_class = Request
	response_class = Response
	
	# Application initializing
	def __init__(self, *a, **kw):
		controllers = list(a)
		tuples = []
		
		for c in controllers:
			
			# Check if routhing path exists
			if c._path:
				current = c._path
			elif c.__doc__:
				current = c.__doc__
			else:
				raise MissingPathError("No path was found for class `%s`!" % c.__name__)
			
			# Add maps for classes that support models
			if c._supports_model and not c._blob_class:
				current += 's'
				tuples.append((current + r'/new', c))
				tuples.append((current + r'/([0-9]+)', c))
			tuples.append((current, c))
		
		webapp2.WSGIApplication.__init__(self, tuples, **kw)
	
	# Change the html templates location
	@staticmethod
	def set_views_folder(*path):
		global template_folder, jinja_env
		
		template_folder = os.path.join(os.path.dirname(__file__), '..', *path)
		jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_folder))

# Base request handler
class BaseController(webapp2.RequestHandler):
	
	# Handler path. Override or set as class doc (regex).
	_path = None
	
	# Variable to identify if the class supports a model
	_supports_model = False
	
	# Variable to identify if the class supports blob serving
	_blob_class = False
	
	
	### Methods child classes may override:
	
	# If not authorized, throw a 403 error
	def authorized(self):
		return True
	
	# When showing the index.html page
	def index(self, *a):
		pass
    
    
    ### Default request handlers:
    ### Overriding without care will screw up the application.
    
    # Before any below
	def init(self, *a):
		pass
    
	def get(self, *a):
		self.init(*a)
		return self.do_authorized()
	
	def post(self, *a):
		self.init(*a)
		return self.do_authorized()
	
	def put(self, *a):
		self.init(*a)
		return self.do_authorized()
	
	def delete(self, *a):
		self.init(*a)
		return self.do_authorized()
	
	def head(self, *a):
		self.init(*a)
		return self.do_authorized()
	
	def options(self, *a):
		self.init(*a)
		return self.do_authorized()
	
	def trace(self, *a):
		self.init(*a)
		return self.do_authorized()
	
	
	# Default actions
	def initialize(self, *a, **kw):
		webapp2.RequestHandler.initialize(self, *a, **kw)
		
		# Extension detector
		extension = self.request.path.split('.')[-1]
		if re.match(r'^[A-Za-z0-9_-]+$', extension):
			self.format = extension
		else:
			self.format = "html"
		
		# Set the variable-like name for the class
		self._name = utils.lowercase(self.__class__.__name__)
		
		# Arguments to consider when rendering templates
		self._params = {}
	
	# Return a dict with results from all arguments in the page
	def get_data(self, *a):
		return {i: self.request.get(i) for i in list(a)}
	
	# Add arguments to consider when rendering the page	
	def send_data(self, data = {}, **kw):
		self._params = dict(dict(kw).items() + data.items())
	
	# Stop and throw a 403 if authorization is denied
	def do_authorized(self):
		if not self.authorized():
			self.error(403)
			return
		return True


# Class for simple pages
class Controller(BaseController):
	
	# Handle GET requests
	def get(self, *a):
		BaseController.get(self, *a)
		
		# Actions from index method
		self.index(*a)
		
		# Display index page
		self.render(self._name + '/index.html', ** self._params)


# Class for model-supporting pages
class ModelController(BaseController):
	
	# Model-supporting verification
	_supports_model = True
	
	# Model that the class supports
	model = None
	
	# Handle GET requests
	def get(self, *a):
		
		# Super
		BaseController.get(self, *a)
		
		# Do appropriate actions
		mode = self.get_mode()
		if mode == "index":
			self.index()
			self.get_resources()
		elif mode == "new":
			self.new()
		elif mode == "show":
			self.show(*a)
		
		# Display the correct page
		self.render_appropriate(** self._params)
	
	def post(self, *a):
		BaseController.post(self, *a)
		
		# Check if successful
		c = self.create()
		if c:
			new_entity = self.model(** c)
			new_entity.put()
			self.redirect('/%ss/%s' % (self._name, new_entity.key.id()))
		else:
			self.new()
			self.render_appropriate(** self._params)
	
	# Render appropriate template
	def render_appropriate(self, **params):
		
		# Index page
		if self.get_mode() == "index":
			self.render(self._name + '/index.html', ** params)
		
		# Resource page
		elif self.get_mode() == "show":
			
			resource = ndb.Key(self.model.__name__, int(self.request.path.split('/')[-1])).get()
			self.render(self._name + '/show.html', resource = resource, ** params)
		
		# Other pages
		else:
			self.render(self._name + '/' + self.get_mode() + '.html', ** params)
	
	### Methods child classes may override:
	
	# When displaying new.html
	def new(self):
		pass
	
	# When displaying show.html
	def show(self, *a):
		pass
	
	# When doing a POST request
	def create(self):
		pass
	
	# When doing a PUT request
	def edit(self, *a):
		pass
	
	# When getting the resources on index mode
	def get_resources(self, *a):
		r = self.model.all()
		self.send_data(resources = r)
	
	### End
	
	
	# Get the correct page
	def get_mode(self):
		path = self.request.path
		if path[:-1] == '/' + self._name:
			return "index"
		elif re.match(r'[0-9]+$', path.split('/')[-1]):
			return "show"
		else:
			return path.split('/')[-1]

# Regular class for blob-serving controllers
class BlobController(ModelController):
	
	def get(self, *a):
		upload_url = blobstore.create_upload_url('/%ss/upload' % self._name)
		self.send_data(upload_url = upload_url)
		ModelController.get(self, *a)
	
	# Overriden: only do default stuff
	# The UploadController class takes care of the procedure.
	def post(self, *a):
		BaseController.post(self, *a)


# Upload class for blob-serving controllers
class UploadController(blobstore_handlers.BlobstoreUploadHandler, ModelController):
	
	_blob_class = True
	default_class = None
	
	def upload(self):
		try:
			return self.get_uploads()[0]
		except IndexError: pass
	
	def init(self):
		self.model = self.default_class.model
	
	# On GET request
	def get(self, *a):
		self.error(405)
	
	# On POST request
	def post(self, *a):
		BaseController.post(self, *a)
		
		# Check if successful
		c = self.create()
		if c:
			
			# Try to upload
			upload = self.upload()
			if upload:
				
				# Get blob reference
				c['blob_key'] = str(upload.key())
				
				# Delete useless blob argument
				del c['blob']
				
				# Use current arguments left to create the model
				new_entity = self.model(** c)
				new_entity.put()
				self.redirect('/%ss/%s' % (self._name, new_entity.key.id()))
			else:
				self.redirect('/%ss/new' % self._name)
		
		# Bounce back if form did not pass
		else:
			self.redirect('/%ss/new' % self._name)


# Upload class for blob-serving controllers
class DownloadController(blobstore_handlers.BlobstoreDownloadHandler, ModelController):
	
	_blob_class = True
	default_class = None
	
	# Download files from blobstore
	def download(self):
		pass
	
	def init(self, *a):
		self.model = self.default_class.model
	
	def get(self, resource):
		BaseController.get(self, resource)
		entity = self.model.get_by_id(long(resource))
		resource = str(urllib.unquote(entity.blob_key))
		blob_info = blobstore.BlobInfo.get(resource)
		self.send_blob(blob_info)
