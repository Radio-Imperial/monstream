"""
check.py

Stream check functions

"""

import logging

import urllib2
from google.appengine.api import urlfetch
import xml.etree.ElementTree as ET

from models import StreamModel
from models import StreamCheckModel

def check_stream_service(stream_id):
	stream = StreamModel.get_by_id(stream_id)
	if stream.stream_type == 'sc2':
		check_sc2_stream(stream)

def check_sc2_stream(stream):
	url = "http://" + stream.stream_hostname + ":" + str(stream.stream_port) + "/stats?sid=" + str(stream.stream_shoutcast_sid)

	server_status = 0
	stream_status = 0
	current_listeners = None
	average_listen_time = None
	
	try:
		res = urlfetch.fetch(url, method=urlfetch.GET, deadline=10)
		server_status = 1
		root = ET.fromstring(res.content)
		stream_status = int(root.find('STREAMSTATUS').text)
		current_listeners = int(root.find('CURRENTLISTENERS').text)
		average_listen_time = float(root.find('AVERAGETIME').text)
	except urllib2.URLError, e:
		logging.error(u'Failed connecting to server: ' + url)
		logging.error(str(e))
		server_status = 0
	except AttributeError, e:
		logging.error(u'Failed parsing response from server: ' + url)
		logging.error(str(e))
	except Error:
		logging.error(str(e))

	add_stream_check(stream, server_status, stream_status, current_listeners, average_listen_time, None)

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