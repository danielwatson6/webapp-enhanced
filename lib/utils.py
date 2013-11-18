import re
import cgi
import hmac
import urllib
import hashlib
import datetime

# Return the parsed html of a template
def html(jinja_env, filename, **params):
        return jinja_env.get_template(filename).render(params)

# Return an html-safe version of a string or list
def escape(s):
        return cgi.escape(s, quote = True)

# Replace the string's newlines with html newlines
def newlines(txt):
        return txt.replace('\n', '<br>')

# Encrypt a string with any algorithm
def encrypt(s, alg = hashlib.md5):
        return alg(s).hexdigest()

# HMAC two strings
def key_encrypt(s, key = "foo"):
        return hmac.new(key, s).hexdigest()

# Check if a string contains a given word
def contains_word(a, b):
        return ' %s ' % b in ' %s ' % a

# Return if the input is a number
def is_num(n):
        return re.match(str(n), r'^[0-9]+$')

# Return if the date set is valid
def valid_date(d, m, y):
        try:
                return datetime.date(y, m, d)
        except:
                return False

# Given an email, return its gravatar url
def gravatar(email, size = None):
        url = "http://www.gravatar.com/avatar/" + hashlib.md5(email.lower()).hexdigest()
        if size:
                url += "?"
                return url + urllib.urlencode({'s':str(size)})
        return url

# Convert class-like names to varliable-like names
def lowercase(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

# Opposite function
def uppercase(name):
	return filter(str.isalnum, s.title())

# Human-readable file size from bytes
def file_size(num):
	for x in ['bytes','KB','MB','GB','TB']:
		if num < 1024.0:
			return "%3.1f %s" % (num, x)
		num /= 1024.0

