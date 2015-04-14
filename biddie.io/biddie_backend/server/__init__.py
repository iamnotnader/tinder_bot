from flask import Flask
from server.constants import USER_FIELD_NAMES
from flask.ext.pymongo import PyMongo
import pymongo
import boto
import boto.s3.connection

S3_KEY_ID = 'AKIAIG7755NS5AF6TD7Q'
S3_ACCESS_KEY = '4oFRXnOJNSAEF56nVJxecoeNRg6R0ZyT0wRPLxtj'

# Create the application.
app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('SERVER_SETTINGS', silent=True)

APP_SECRET = 'Nader is pretty damn chill'
app.secret_key = APP_SECRET

# Mongo stuff. This gets overridden when testing!
app.config['DATABASE'] = PyMongo(app)
with app.app_context():
    app.config['DATABASE'].db.users.ensure_index(
        [(USER_FIELD_NAMES.LOCATION, pymongo.GEOSPHERE)],
        background=True
    )

app.config['S3_KEY_ID'] = S3_KEY_ID
app.config['S3_ACCESS_KEY'] = S3_ACCESS_KEY
app.config['BOTO_CONN'] = boto.connect_s3(
    aws_access_key_id = app.config['S3_KEY_ID'],
    aws_secret_access_key = app.config['S3_ACCESS_KEY'],
    host = 'objects.dreamhost.com',
    #is_secure=False,               # uncomment if you are not using ssl
    calling_format = boto.s3.connection.OrdinaryCallingFormat(),
)

# Import all the endpoints.
import server.views.users
import server.views.bids
import server.views.login
import server.views.photos
import server.views.payment
import server.views.likes
import server.views.leave_review
import server.views.pokes