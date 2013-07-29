"""
check.py

Stream check functions

"""

import logging
import numpy

from urllib2 import URLError, HTTPError
from google.appengine.api import urlfetch
import xml.etree.ElementTree as ET

from models import StreamModel
from models import StreamCheckModel

def check_stream_service(stream_id):
	stream = StreamModel.get_by_id(stream_id)
	if stream.stream_type == 'sc2':
		check_sc2_stream(stream)
	elif stream.stream_type == 'ic2':
		check_ic2_stream(stream)

def check_ic2_stream(stream):
	url = "http://" + stream.stream_hostname + ":" + str(stream.stream_port) + "/xml_status.xsl?mount=" + str(stream.stream_mount)

	server_status = 0
	stream_status = 0
	current_listeners = None

	try:
		res = urlfetch.fetch(url, method=urlfetch.GET, deadline=10)
		server_status = 1
		root = ET.fromstring(res.content)
		for source in root.findall('source'):
			mount = source.find('mount').text
			if (mount == stream.stream_mount):
				stream_status = 1
				current_listeners = int(source.find('listeners').text)
	except HTTPError, e:
		logging.error(u'Failed connecting to server: ' + url)
		logging.error(e.code)
		server_status = 0
	except URLError, e:
		logging.error(u'Failed connecting to server: ' + url)
		logging.error(e.args)
		server_status = 0
	except AttributeError, e:
		logging.error(u'Failed parsing response from server: ' + url)
		logging.error(str(e))
	except Exception, e:
		logging.error(str(e))

	add_stream_check(stream, server_status, stream_status, current_listeners, None, None)

def check_sc2_stream(stream):
	url = "http://" + stream.stream_hostname + ":" + str(stream.stream_port) + "/stats?sid=" + str(stream.stream_sid)

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
	except HTTPError, e:
		logging.error(u'Failed connecting to server: ' + url)
		logging.error(e.code)
		server_status = 0
	except URLError, e:
		logging.error(u'Failed connecting to server: ' + url)
		logging.error(e.args)
		server_status = 0
	except AttributeError, e:
		logging.error(u'Failed parsing response from server: ' + url)
		logging.error(str(e))
	except Exception, e:
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
	except CapabilityDisabledError:
		logging.error(u'App Engine Datastore is currently in read-only mode.')

def get_server_uptime_moving_average(stream_checks, window_size):
	interval = []
	for stream_check in stream_checks:
		interval.append(stream_check.server_status)
	return moving_average(interval, window_size)

def get_stream_uptime_moving_average(stream_checks, window_size):
	interval = []
	for stream_check in stream_checks:
		interval.append(stream_check.stream_status)
	return moving_average(interval, window_size)

def moving_average(interval, window_size):
	weigths = numpy.repeat(1.0, window_size) / window_size
	return numpy.convolve(interval, weigths, 'valid')