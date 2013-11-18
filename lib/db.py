import re
import hashlib

from lib import utils
from google.appengine.ext import ndb, blobstore


EMAIL_RE = re.compile(r'^[_a-z0-9-]+(?:\.[_a-z0-9-]+)*@[a-z0-9-]+(?:\.[a-z0-9-]+)*(?:\.[a-z]{2,4})$')

class Model(ndb.Model):
    
    # Get all entities from the class
    @classmethod
    def all(cls, max = None):
            if max:
                    return cls.query().fetch(20)
            return cls.query()
    
    # Destroy the entity from the database
    def destroy(self):
            self.key.delete()
    
    # Get an entity's URI
    def uri(self):
        return '%ss/%s' % (utils.lowercase(self.__module__[7:]), self.key.id())
    
    # Get an entity's blob-serving URI
    # Note: this only works for classes that inherit the
    #       BlobController class from the server module.
    def serve_uri(self):
        return '/%ss/serve/%s' % (utils.lowercase(self.__module__[7:]), self.key.id())
    
    # From class, create a new entity
    @classmethod
    def create(cls, *a, **kw):
            new_model = cls(*a, **kw)
            new_model.put()
            return new_model

# Model for users
class AccountModel(Model):
    
    # Default paswword hashing
    @classmethod
    def hash_pw(cls, pw):
        return hashlib.md5(pw).hexdigest()
    
    # Validation
    def valid_pw(self, pw):
        return self.pw_hash == self.__class__.hash_pw(pw)
    
    # Email validation
    def valid_email(self, email):
        return EMAIL_RE.match(email)

# Model for blob handling
class BlobModel(Model):
    blob_key = ndb.StringProperty(required = True)
    
    def filename(self):
        obj = blobstore.BlobInfo.get(self.blob_key)
        return obj.filename
    
    def size(self):
        obj = blobstore.BlobInfo.get(self.blob_key)
        return obj.size

# NDB Property shortcuts that are
# accessible directly from this module
# [Note] this might need to be updated
string = ndb.StringProperty
integer = ndb.IntegerProperty
double = ndb.FloatProperty
boolean = ndb.BooleanProperty
text = ndb.TextProperty
blob = ndb.BlobProperty
date = ndb.DateTimeProperty
key = ndb.KeyProperty
blob_key = ndb.BlobKeyProperty
function = ndb.ComputedProperty
json = ndb.JsonProperty
pickle = ndb.PickleProperty
blob_key = blobstore.BlobReferenceProperty

