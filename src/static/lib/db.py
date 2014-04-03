import re
import logging

from google.appengine.ext import ndb


EMAIL_RE = r'.*'		# TO-DO: Add a real regexp.


class Model(ndb.Model):
	"""Custom Model class."""
	
	form = None 		# Link to form class
	
	def __init__(self, validate=False, *a, **kw):
		
		form = self.form
		if form is not None and validate:
			
			assert type(form) == dict
			validated_form = self.validate(form, dict(kw))
			super(Model, self).__init__(*a, **validated_form)
			
		else:
			super(Model, self).__init__(*a, **kw)
	
	def validate(self, form, data):
		result = {}
		for field in form:
			for validator in form[field]:
				try:
					result[field] = validator(data[field])
				except StopValidation: break	# Automatically pass
		return result
	
	@staticmethod
	def get_errors(form, data):
		result = {}
		for field in form:
			for validator in form[field]:
				try:
					validator(data[field])
				except IOError as i:
					result[field] = i.message
				except StopValidation: break
		return result
	
	@classmethod
	def create(cls, **properties):
		"""Create and save an instance from this model."""
		entity = cls(**properties)
		entity.put()
	
	@classmethod
	def find(cls, id_):
		"""Fetch the entity with the specified id, otherwise return None."""
		return ndb.Key(cls, int(id_)).get()
	
	def destroy(self):
		"""Remove the entity from the datastore."""
		self.key.delete()
	
	def link(self):
		"""Return the link for the entity's show page."""
		return '/%ss/%s' % (_lowercase(self.__module__[7:]), self.key.id())
	
	def edit_link(self):
		"""Return the link for the entity's edit page."""
		return self.link() + '/edit'
	
	def get_id(self):
		"""Shortcut for key.id()"""
		return str(self.key.id())
	
	@classmethod
	def fetch(cls, n):
		"""Get the given number of the model's entities from the datastore."""
		return cls.query().fetch(quantity)
	
	@classmethod
	def all(cls):
		"""Get all the model's entities from the datastore."""
		return cls.query().fetch()


class BaseValidator(object):
	"""Class for creating individual validator instances."""
	
	def __init__(self, message="Please correct this field."):
		self.message = message
	
	def __call__(self, field):
		return self.validate(field)
	
	def validate(self, field):
		"""Called when calling the validator.
		
		A validate() method takes in a field and will either
		return its value (possibly modifying it) or raise
		a IOError.
		(Note: the IOError should contain self.message)
		
		Validators may also contain StopValidation to automatically
		pass.
		
		"""

class AnyOf(BaseValidator):
	"""Validator that checks if the input is in a list of given values."""
	
	def __init__(self, values, **kw):
		self.values = values
		super(AnyOf, self).__init__(**kw)
	
	def validate(self, field):
		if field in self.values: return field
		raise IOError(self.message)

class Email(BaseValidator):
	"""Validator that checks if the input is a valid email."""
	
	def validate(self, field):
		if re.match(EMAIL_RE, field): return field
		raise IOError(self.message)

class EqualTo(BaseValidator):
	"""Validator that checks if the input is equal to a certain value."""
	
	def __init__(self, default_value, **kw):
		self.default_value = default_value
		super(EqualTo, self).__init__(**kw)
	
	def validate(self, field):
		if field == self.default_value: return field
		raise IOError(self.message)

class Length(BaseValidator):
	"""Validator that checks if the input's length is between a certain range."""
	
	def __init__(self, min=-1, max=-1, **kw):
		self.min = min
		self.max = max
		super(Length, self).__init__(**kw)
	
	def validate(self, field):
		if self.min <= len(field) <= self.max: return field
		raise IOError(self.message)

class NoneOf(BaseValidator):
	"""Validator that checks if the input is not in the given values."""
	
	def __init__(self, values, **kw):
		self.values = values
		super(NoneOf, self).__init__(**kw)
	
	def validate(self, field):
		if not (field in self.values): return field
		raise IOError(self.message)

class NumberRange(BaseValidator):
	"""Validator that checks if the input's length is between a certain range."""
	
	def __init__(self, min=None, max=None, **kw):
		self.min = min
		self.max = max
		super(NumberRange, self).__init__(**kw)
	
	def validate(self, field):
		if not self.min: self.min = field
		if not self.max: self.max = field
		if self.min <= field <= self.max: return field
		raise IOError(self.message)

class Optional(BaseValidator):
	"""Validator that makes the value pass automatically if it's empty."""
	
	def validate(self, field):
		if field == "" or field is None:
			raise StopValidation
		return field

class Regexp(BaseValidator):
	"""Validator that checks if the input matches a certain regular expression."""
	
	def __init__(self, regex, **kw):
		self.regex = regex
		super(Regexp, self).__init__(**kw)
	
	def validate(self, field):
		if re.match(self.regex, field): return field
		raise IOError(self.message)

class Required(BaseValidator):
	"""Validator that checks if the input is not empty."""
	
	def validate(self, field):
		if field is not None and field != '': return field
		raise IOError(self.message)


class StopValidation(Exception):
	"""Error thrown by validators to indicate to stop the validation."""


class validators(object):
	"""Validators shortcut."""
	
	any_of = AnyOf
	email = Email
	equal_to = EqualTo
	length = Length
	none_of = NoneOf
	number_range = NumberRange
	optional = Optional
	regexp = Regexp
	required = Required


### Model properties:
generic = ndb.GenericProperty
string = ndb.StringProperty
integer = ndb.IntegerProperty
boolean = ndb.BooleanProperty
double = ndb.FloatProperty
text = ndb.TextProperty
date = ndb.DateProperty
user = ndb.UserProperty
key = ndb.KeyProperty
pickle = ndb.PickleProperty
json = ndb.JsonProperty


# This is used within the module.
def _lowercase(s):
	"""Convert class-like names to varliable-like names."""
	s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', s)
	return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
