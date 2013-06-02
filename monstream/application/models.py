"""
models.py

App Engine datastore models

"""

from google.appengine.ext import ndb

class StreamModel(ndb.Model):
	"""Stream Model"""
	stream_name = ndb.StringProperty(required=True)
	stream_type = ndb.StringProperty(required=True)
	stream_hostname = ndb.StringProperty(required=True)
	stream_port = ndb.IntegerProperty(required=True)
	stream_shoutcast_sid = ndb.IntegerProperty()
	added_by = ndb.UserProperty()

class StreamCheckModel(ndb.Model):
	"""Stream Check Model"""
	stream = ndb.KeyProperty(required=True)
	timestamp = ndb.DateTimeProperty(auto_now_add=True)
	server_status = ndb.IntegerProperty(required=True)
	stream_status = ndb.IntegerProperty(required=True)
	current_listeners = ndb.IntegerProperty()
	average_listen_time = ndb.FloatProperty()
	max_listen_time = ndb.FloatProperty()
