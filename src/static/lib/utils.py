import re
import cgi
import hmac
import urllib
import hashlib
import datetime


# NOTE: adding extra methods is perfectly
# safe, but deleting any existing ones will
# interfere with the other modules.

def html(jinja_env, filename, **params):
	"""Get the parsed html of a template."""
	return jinja_env.get_template(filename).render(params)

def escape(s):
	"""Get an html-safe version of a string or list."""
	return cgi.escape(s, quote = True)

def newlines(txt):
	"""Replace the string's newlines with html newlines."""
	return txt.replace('\n', '<br>')

def encrypt(s, alg = hashlib.md5):
	"""Encrypt a string with any algorithm."""
	return alg(s).hexdigest()

def key_encrypt(a, b):
	"""Encrypt two strings."""
	return hmac.new(a, b).hexdigest()

def contains_word(a, b):
	"""Check if a string contains a given word."""
	return ' %s ' % b in ' %s ' % a

def is_num(n):
	"""Check if the input is a number."""
	return re.match(str(n), r'^[0-9]+$')

def valid_date(d, m, y):
	"""Check if the date set is valid."""
	try:
		return datetime.date(y, m, d)
	except:
		return False

def lowercase(s):
	"""Convert class-like names to varliable-like names."""
	s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', s)
	return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

def uppercase(s):
	"""Opposite function to lowercase()."""
	return filter(str.isalnum, s.title())

def file_size(num):
	"""Get the human-readable file size (from bytes)."""
	for x in ['bytes','KB','MB','GB','TB']:
		if num < 1024.0:
			return "%3.1f %s" % (num, x)
		num /= 1024.0

def gravatar(email, size = None):
	"""Given an email, get its gravatar url."""
	url = "http://www.gravatar.com/avatar/" + hashlib.md5(email.lower()).hexdigest()
	if size:
		url += "?"
		return url + urllib.urlencode({'s':str(size)})
	return url

