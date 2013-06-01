"""
views.py

URL route handlers

Note that any handler params must match the URL route params.
For example the *say_hello* handler, handling the URL route '/hello/<username>',
  must be passed *username* as the argument.

"""
from google.appengine.api import users
from google.appengine.runtime.apiproxy_errors import CapabilityDisabledError

from flask import request, render_template, flash, url_for, redirect

from flask_cache import Cache

from application import app
from decorators import login_required, admin_required
from forms import StreamForm
from models import StreamModel

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
            stream_descriptor = form.stream_descriptor.data,
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
            stream.stream_descriptor = form.data.get('stream_descriptor')
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
    """SHow stream object"""
    stream = StreamModel.get_by_id(stream_id)
    return render_template('show_stream.html', stream=stream)


def warmup():
    """App Engine warmup handler
    See http://code.google.com/appengine/docs/python/config/appconfig.html#Warming_Requests

    """
    return ''

