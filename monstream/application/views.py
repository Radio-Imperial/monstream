"""
views.py

URL route handlers

Note that any handler params must match the URL route params.
For example the *say_hello* handler, handling the URL route '/hello/<username>',
  must be passed *username* as the argument.

"""
from __future__ import division

import logging
import datetime


from google.appengine.api import users
from google.appengine.api import taskqueue
from google.appengine.runtime.apiproxy_errors import CapabilityDisabledError

from flask import request, render_template, flash, url_for, redirect

from flask_cache import Cache

from application import app
from decorators import login_required, admin_required
from forms import StreamForm
from models import StreamModel
from models import StreamCheckModel

from services import check_stream_service

# Flask-Cache (configured to use App Engine Memcache API)
cache = Cache(app)

def home():
    return redirect(url_for('list_streams'))

@login_required
def list_streams():
    """List all streams"""
    streams = StreamModel.query()
    form = StreamForm()
    if form.validate_on_submit():
        stream = StreamModel(
            stream_name = form.stream_name.data,
            stream_type = form.stream_type.data,
            stream_hostname = form.stream_hostname.data,
            stream_port = form.stream_port.data,
            stream_shoutcast_sid = form.stream_shoutcast_sid.data,
            added_by = users.get_current_user()
        )
        try:
            stream.put()
            stream_id = stream.key.id()
            flash(u'Stream %s successfully saved.' % stream_id, 'success')
            return redirect(url_for('list_streams'))
        except CapabilityDisabledError:
            flash(u'App Engine Datastore is currently in read-only mode.', 'info')
            return redirect(url_for('list_streams'))
    return render_template('list_streams.html', streams=streams, form=form)

@login_required
def edit_stream(stream_id):
    stream = StreamModel.get_by_id(stream_id)
    form = StreamForm(obj=stream)
    if request.method == "POST":
        if form.validate_on_submit():
            stream.stream_name = form.data.get('stream_name')
            stream.stream_type = form.data.get('stream_type')
            stream.stream_hostname = form.data.get('stream_hostname')
            stream.stream_port = form.data.get('stream_port')
            stream.stream_shoutcast_sid = form.data.get('stream_shoutcast_sid')
            stream.put()
            flash(u'Stream %s successfully saved.' % stream_id, 'success')
            return redirect(url_for('list_streams'))
    return render_template('edit_stream.html', stream=stream, form=form)

@login_required
def delete_stream(stream_id):
    """Delete a stream object"""
    stream = StreamModel.get_by_id(stream_id)
    try:
        stream.key.delete()
        flash(u'Stream %s successfully deleted.' % stream_id, 'success')
        return redirect(url_for('list_streams'))
    except CapabilityDisabledError:
        flash(u'App Engine Datastore is currently in read-only mode.', 'info')
        return redirect(url_for('list_streams'))

@login_required
def show_stream(stream_id):
    """Show stream object"""
    stream = StreamModel.get_by_id(stream_id)
    stream_checks_query = StreamCheckModel.query().filter(StreamCheckModel.stream == stream.key).order(StreamCheckModel.timestamp)
    stream_checks = stream_checks_query.fetch(4320)
    logging.error(str(len(stream_checks)))
    uptime_sum = 0
    average_listeners_sum = 0
    average_listeners_count = 0
    average_listen_time_count = 0
    average_listen_time_sum = 0

    for stream_check in stream_checks:
        if stream_check.stream_status > 0:
            uptime_sum += 1
        if stream_check.current_listeners is not None:
            average_listeners_sum += stream_check.current_listeners
            average_listeners_count += 1
        if stream_check.average_listen_time is not None:
            average_listen_time_sum += stream_check.average_listen_time
            average_listen_time_count += 1

    status = 'Up'
    uptime = round(((uptime_sum / len(stream_checks)) * 100), 2)
    average_listeners = round((average_listeners_sum / average_listeners_count), 2)
    average_listen_time = str(datetime.timedelta(seconds=int(average_listen_time_sum / average_listen_time_count)))

    return render_template('show_stream.html', stream=stream, stream_checks=stream_checks, status=status, uptime=uptime, average_listeners=average_listeners, average_listen_time=average_listen_time)

def check():
    """Check streams cron job"""
    streams = StreamModel.query()
    for stream in streams:
        stream_id = stream.key.id()
        queue = taskqueue.Queue('check')
        task = taskqueue.Task(url='/stream/' + str(stream_id) + '/check', method='GET')
        queue.add(task)
    return ''

def check_stream(stream_id):
    """Check stream"""
    check_stream_service(stream_id)
    return ''

def warmup():
    """App Engine warmup handler
    See http://code.google.com/appengine/docs/python/config/appconfig.html#Warming_Requests

    """
    return ''
