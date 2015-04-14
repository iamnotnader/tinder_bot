"""
Defines a testing helper class that extends from unittest and defines a
bunch of helpful functions needed by all the test packages.
"""

from flask.ext.pymongo import PyMongo
from bson.objectid import ObjectId
from server.constants import *

import unittest
import server
import json
import datetime
import stripe
import random

# Set your secret key: remember to change this to your live secret key in production
# See your keys here https://dashboard.stripe.com/account
# TODO(daddy): Get a real API key.
stripe.api_key = "sk_test_BQokikJOvBiI2HlWgH4olfQ2"

class HelperTestCase(unittest.TestCase):
  @classmethod
  def setUpClass(cls):
    server.app.config['TESTING'] = True

    # We swap out the database when we're testing. This works because we always
    # get the database using get_db().
    server.app.config['MONGO2_DBNAME'] = 'test'
    server.app.config['DATABASE'] = PyMongo(server.app, config_prefix='MONGO2')

  @classmethod
  def setUp(self):
    self.longMessage = True

    with server.app.app_context():
      server.app.config['DATABASE'].db.users.remove({})
      server.app.config['DATABASE'].db.bids.remove({})
      server.app.config['DATABASE'].db.likes.remove({})
      server.app.config['DATABASE'].db.pokes.remove({})

    self.app = server.app.test_client()

  def tearDown(self):
    pass

  def _create_n_random_users(self, num_users):
    user_data = []
    for i in xrange(num_users):
      name = str(random.random())
      resp = self._create_user(name)
      user_data.append(resp)
      self._logout()
    return user_data

  def _create_sender_receiver(self):
    receiver_dict = self._create_user(name='a')
    self._logout()
    sender_dict = self._create_user(name='b')
    return sender_dict, receiver_dict

  def seconds_since_utc_epoch(self, datetime_obj):
    return (datetime_obj - datetime.datetime(1970,1,1)).total_seconds()

  def _bid_on_user(self, sender_dict, receiver_dict, amount="2",
                   input_date=datetime.datetime.utcnow()+datetime.timedelta(days=1)):
    rv = self.app.post('/bids/'+sender_dict['id']+'/',
        headers={'Content-Type': 'application/json'},
        data=json.dumps({
          BID_FIELD_NAMES.RECEIVER_ID:receiver_dict['id'],
          BID_FIELD_NAMES.BID_AMOUNT:amount,
          BID_FIELD_NAMES.TIMES_AND_PLACES_LIST: [{
            BID_FIELD_NAMES.SECONDS_SINCE_EPOCH: self.seconds_since_utc_epoch(input_date),
            "duration": "30m",
            "place_name": "my place"
          }]
        })
      )
    return json.loads(rv.data)

  def _adjust_time_selected(self, sender_dict, receiver_dict, input_date):
      new_time_and_places_list = [{
        BID_FIELD_NAMES.SECONDS_SINCE_EPOCH: self.seconds_since_utc_epoch(input_date),
        "duration": "30m",
        "place_name": "my place"
      }]
      with server.app.app_context():
        server.app.config['DATABASE'].db.bids.update(
          {BID_FIELD_NAMES.SENDER_ID: ObjectId(sender_dict['id']),
           BID_FIELD_NAMES.RECEIVER_ID: ObjectId(receiver_dict['id'])},
          {'$set': {BID_FIELD_NAMES.TIMES_AND_PLACES_LIST: new_time_and_places_list}}
        )

  def _generate_fake_token(self, card_number='4242424242424242'):
    return stripe.Token.create(
      card={
        "number": card_number,
        "exp_month": 12,
        "exp_year": 2015,
        "cvc": '123'
      },
    )

  def _pay_and_confirm(self, sender_dict, receiver_dict):
    rv = self.app.post('/pay_and_confirm/'+sender_dict['id']+'/',
          headers={'Content-Type': 'application/json'},
          data=json.dumps(
            {BID_FIELD_NAMES.RECEIVER_ID: receiver_dict['id'],
             PAYMENT_FIELDS.PAYMENT_TOKEN: self._generate_fake_token()}
          )
        )
    return json.loads(rv.data)

  def _post_three_photos(self, user_dict):
    self.app.post('/photo/'+user_dict['id']+'/',
      headers={'Content-Type': 'application/json'},
      data=json.dumps(
        {'photo': {'facebook_id': "3", 'photo_position': 3, 'source_url': "3"}})
    )
    self.app.post('/photo/'+user_dict['id']+'/',
      headers={'Content-Type': 'application/json'},
      data=json.dumps(
        {'photo': {'facebook_id': "1", 'photo_position': 1, 'source_url': "1"}})
    )
    self.app.post('/photo/'+user_dict['id']+'/',
      headers={'Content-Type': 'application/json'},
      data=json.dumps(
        {'photo': {'facebook_id': "2", 'photo_position': 2, 'source_url': "2"}})
      )

  def _basic_search(self, must_have_photos=True):
    rv = self.app.post('/search_with_criteria/',
          headers={'Content-Type': 'application/json'},
          data=json.dumps(
            {'orientation': None, 'photos': must_have_photos, 'sex': None,
             'zip_code': None}
          )
        )
    return json.loads(rv.data)

  def _create_user(self, name):
    rv = self.app.post('/users/',
      headers={'Content-Type': 'application/json'},
      data=json.dumps({'email': name, 'password': name}))
    return json.loads(rv.data)

  def _get_login(self):
    return json.loads(self.app.get('/login/').data)

  def _post_login(self, name):
    rv = self.app.post('/login/',
      headers={'Content-Type': 'application/json'},
      data=json.dumps({'email': name, 'password': name})
    )
    return json.loads(rv.data)

  def _logout(self):
    return json.loads(self.app.delete('/login/').data)

  def _patch_user_first_name(self, user_dict, name):
    self.app.patch('/users/'+user_dict['id']+'/',
      headers={'Content-Type': 'application/json'},
      data=json.dumps({'first_name': name}))

  def _get_photos_for_user(self, user_dict):
    return json.loads(self.app.get('/user_photos/'+user_dict['id']+'/').data)

  def _cancel_bid(self, sender_obj, receiver_obj):
    self._post_login(sender_obj['email'])
    rv = self.app.post('/bids/cancel/'+sender_obj['id']+'/',
      headers={'Content-Type': 'application/json'},
      data=json.dumps({BID_FIELD_NAMES.RECEIVER_ID: receiver_obj['id']})
    )
    return json.loads(rv.data)
  
  def _accept_bid(self, sender_obj, receiver_obj, accepted_time_and_place_index=0):
    rv = self.app.post('/bids/accept/'+sender_obj['id']+'/',
      headers={'Content-Type': 'application/json'},
      data=json.dumps({
        BID_FIELD_NAMES.RECEIVER_ID: receiver_obj['id'],
        BID_FIELD_NAMES.ACCEPTED_TIME_AND_PLACE_INDEX: accepted_time_and_place_index
      })
    )
    return json.loads(rv.data)

  def _get_bids_from_db(self):
    with server.app.app_context():
      updated_bids = list(server.app.config['DATABASE'].db.bids.find({})
        .sort([
          (BID_FIELD_NAMES.TIME_BID_CREATED_AT, -1)
        ])
      )
    return updated_bids

  def _create_four_users(self):
    user_a = self._create_user(name='a')
    self._logout()
    user_b = self._create_user(name='b')
    self._logout()
    user_c = self._create_user(name='c')
    self._logout()
    user_d = self._create_user(name='d')
    self._logout()
    return user_a, user_b, user_c, user_d
