"""
forms.py

Web forms based on Flask-WTForms

See: http://flask.pocoo.org/docs/patterns/wtforms/
     http://wtforms.simplecodes.com/

"""

from flaskext import wtf
from flaskext.wtf import validators
from wtforms.ext.appengine.ndb import model_form

from models import StreamModel

class StreamForm(wtf.Form):
	"""Stream Form"""
	stream_name = wtf.TextField('Name', validators=[validators.Required()])
	stream_type = wtf.SelectField('Type', choices=[('sc2', 'Shoutcast 2')])
	stream_hostname = wtf.TextField('Hostname', validators=[validators.Required()])
	stream_port = wtf.IntegerField('Port', [validators.required()])
	stream_shoutcast_sid = wtf.IntegerField('Shoutcast SID')
