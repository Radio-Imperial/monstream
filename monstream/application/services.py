"""
check.py

Stream check functions

"""

import logging

from models import StreamModel
from models import StreamCheckModel

def check_stream_service(stream):
	if stream.stream_type == 'sc2':
		check_sc2_stream(stream)

def check_sc2_stream(stream):
	add_stream_check(stream)

def add_stream_check(stream):
	stream_check = StreamCheckModel(
		stream = stream.key,
		server_status = 1,
		stream_status = 1
	)
	try:
		stream_check.put()
		stream_check_id = stream_check.key.id()
	except CapabilityDisabledError:
		logging.error(u'App Engine Datastore is currently in read-only mode.')