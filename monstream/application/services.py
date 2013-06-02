"""
check.py

Stream check functions

"""

import logging

from models import StreamModel
from models import StreamCheckModel

def check_stream_service(stream_id):
	stream = StreamModel.get_by_id(stream_id)
	if stream.stream_type == 'sc2':
		check_sc2_stream(stream)

def check_sc2_stream(stream):
	add_stream_check(stream, 1, 1, 100, 10.0, 20.0)

def add_stream_check(stream, server_status, stream_status, current_listeners, average_listen_time, max_listen_time):
	stream_check = StreamCheckModel(
		stream = stream.key,
		server_status = server_status,
		stream_status = stream_status,
		current_listeners = current_listeners,
		average_listen_time = average_listen_time,
		max_listen_time = max_listen_time
	)
	try:
		stream_check.put()
		# stream_check_id = stream_check.key.id()
	except CapabilityDisabledError:
		logging.error(u'App Engine Datastore is currently in read-only mode.')