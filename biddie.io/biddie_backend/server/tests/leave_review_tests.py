"""
Exercise and test the /bids/ endpoing and everything in the bids.py view.
"""

from flask.ext.pymongo import PyMongo
from bson.objectid import ObjectId
from server.constants import *
from server.tests.test_helpers import *
from server.utils import *
from bson.objectid import ObjectId

import unittest
import server
import json
import datetime

past_date_bid_obj = {
  "receiver_id" : ObjectId("54b7385d194498a1acecc5c1"),
  "time_bid_created_at" : datetime.datetime.strptime("2015-01-25T22:39:31.319", "%Y-%m-%dT%H:%M:%S.%f"),
  "sender_id" : ObjectId("54c53ed54298651ae2758044"),
  "bid_state" : "sender_confirmed",
  "timestamp_list" : [ [ "outstanding",
  datetime.datetime.strptime("2015-01-25T22:39:31.320", "%Y-%m-%dT%H:%M:%S.%f") ],
  [ "receiver_accepted",
  datetime.datetime.strptime("2015-01-25T22:39:43.678", "%Y-%m-%dT%H:%M:%S.%f") ],
  [ "sender_confirmed",
  datetime.datetime.strptime("2015-01-27T04:11:10.956", "%Y-%m-%dT%H:%M:%S.%f") ] ],
  "bid_amount" : 63,
  "times_and_places_list" : [ { "selectedAmOrPm" : "am",
  "selectedDuration" : "30m",
  "selectedMinute" : 30,
  "selectedHour" : 5,
  "seconds_since_epoch" : 1322527400,
  "selectedDate" : "2015-1-29-Thursday",
  "place_name" : "my place" } ],
  "accepted_time_and_place_index" : 0,
  "card_id" : "card_15P7Et2eZvKYlo2CRGjNYr0y"
}

class LeaveReviewTestCase(HelperTestCase):
  def _create_users_and_seed_database(self, is_sender=True, bid_timestamp=1322527400):
    [sender_data, receiver_data] = self._create_n_random_users(2)
    if is_sender:
      self._post_login(sender_data['email'])
    else:
      self._post_login(receiver_data['email'])

    past_date_bid_obj[BID_FIELD_NAMES.SENDER_ID] = ObjectId(sender_data['id'])
    past_date_bid_obj[BID_FIELD_NAMES.RECEIVER_ID] = ObjectId(receiver_data['id'])
    tapl = BID_FIELD_NAMES.TIMES_AND_PLACES_LIST
    sse = BID_FIELD_NAMES.SECONDS_SINCE_EPOCH
    past_date_bid_obj[tapl][0][sse] = bid_timestamp

    with server.app.app_context():
      server.app.config['DATABASE'].db.bids.insert(past_date_bid_obj)

    return sender_data, receiver_data

  def _leave_review(self, reviewer_id, person_being_reviewed_id, fields_dict):
    fields_dict[BID_FIELD_NAMES.RECEIVER_ID] = person_being_reviewed_id
    resp = self.app.post('/leave_review/'+reviewer_id+'/', 
      headers={'Content-Type': 'application/json'},
      data=json.dumps(fields_dict)
    )
    del fields_dict[BID_FIELD_NAMES.RECEIVER_ID]
    return json.loads(resp.data)

  def test_sender_leave_review(self):
    sender_data, receiver_data = self._create_users_and_seed_database()

    srv = SENDER_REVIEW_FIELDS
    fields_dict = {
      srv.RECEIVER_SHOWED_UP: False,
      srv.WOULD_LIKE_TO_PAY: True,
      srv.RECEIVER_RATING: 1,
      srv.QUESTION_TEXT: 'Did receivier show up? Blah blah',
      srv.LOOKED_WORSE_THAN_PICS: True,
    }
    resp = self._leave_review(sender_data['id'], receiver_data['id'], fields_dict)

    with server.app.app_context():
      bid_created = server.app.config['DATABASE'].db.bids.find_one({})
    self.assertIsNotNone(resp)
    self.assertTrue(resp['success'], msg="Response should have success set to true.")
    self.assertIsNotNone(bid_created, msg="Bid created shouldn't be non-None")
    self.assertIsNotNone(bid_created.get(
        BID_FIELD_NAMES.SENDER_REVIEW), msg="Bid created shouldn't be non-None")
    self.assertEqual(
      bid_created[BID_FIELD_NAMES.SENDER_REVIEW], fields_dict
    )

  def test_receiver_leave_review(self):
    sender_data, receiver_data = self._create_users_and_seed_database(is_sender=False)

    rcv = RECEIVER_REVIEW_FIELDS
    fields_dict = {
      rcv.DID_SHOW_UP: False,
      rcv.COMFORT_RATING: 2,
      rcv.LOOKED_WORSE_THAN_PICS: True,
      rcv.QUESTION_TEXT: "Did they blah blah?"
    }
    resp = self._leave_review(receiver_data['id'], sender_data['id'], fields_dict)

    self.assertIsNotNone(resp)
    self.assertTrue(resp['success'], msg="Response should have success set to true.")
    with server.app.app_context():
      bid_created = server.app.config['DATABASE'].db.bids.find_one({})
    self.assertIsNotNone(bid_created, msg="Bid created shouldn't be non-None")
    self.assertIsNotNone(bid_created.get(
        BID_FIELD_NAMES.RECEIVER_REVIEW), msg="Bid created shouldn't be non-None")
    self.assertEqual(
      bid_created[BID_FIELD_NAMES.RECEIVER_REVIEW], fields_dict
    )

  def test_sender_leave_review_missing_field(self):
    sender_data, receiver_data = self._create_users_and_seed_database()

    srv = SENDER_REVIEW_FIELDS
    fields_dict = {
      srv.RECEIVER_SHOWED_UP: False,
      srv.RECEIVER_RATING: 1,
      srv.QUESTION_TEXT: 'Did receivier show up? Blah blah',
      srv.LOOKED_WORSE_THAN_PICS: True,
    }
    resp = self._leave_review(sender_data['id'], receiver_data['id'], fields_dict)
    self.assertIsNotNone(resp)
    self.assertFalse(resp.get('success'), msg="Response should have success set to false.")
    self.assertEqual(resp.get('message_key'), 'missing_field')

  def test_sender_leave_review_too_many_field(self):
    sender_data, receiver_data = self._create_users_and_seed_database()

    srv = SENDER_REVIEW_FIELDS
    fields_dict = {
      srv.RECEIVER_SHOWED_UP: False,
      srv.WOULD_LIKE_TO_PAY: True,
      srv.RECEIVER_RATING: 1,
      srv.QUESTION_TEXT: 'Did receivier show up? Blah blah',
      srv.LOOKED_WORSE_THAN_PICS: True,
      'injection_attack_field': True
    }
    resp = self._leave_review(sender_data['id'], receiver_data['id'], fields_dict)
    self.assertIsNotNone(resp)
    self.assertFalse(resp.get('success'), msg="Response should have success set to false.")
    self.assertEqual(resp.get('message_key'), 'too_many_fields')

  def test_sender_leave_review_bid_too_new(self):
    sender_data, receiver_data = self._create_users_and_seed_database(bid_timestamp=1622527400)

    srv = SENDER_REVIEW_FIELDS
    fields_dict = {
      srv.RECEIVER_SHOWED_UP: False,
      srv.WOULD_LIKE_TO_PAY: True,
      srv.RECEIVER_RATING: 1,
      srv.QUESTION_TEXT: 'Did receivier show up? Blah blah',
      srv.LOOKED_WORSE_THAN_PICS: True,
    }
    resp = self._leave_review(sender_data['id'], receiver_data['id'], fields_dict)
    self.assertIsNotNone(resp)
    self.assertFalse(resp.get('success'), msg="Response should have success set to false.")
    self.assertEqual(resp.get('message_key'), 'invalid_review')

  def test_sender_bid_without_review(self):
    sender_data, receiver_data = self._create_users_and_seed_database()

    resp = self._bid_on_user(sender_data, receiver_data)
    self.assertIsNotNone(resp)
    self.assertFalse(resp.get('success'), msg="Response should have success set to false.")
    self.assertEqual(resp.get('message_key'), 'you_need_to_review')

  def test_receiver_bid_without_review(self):
    sender_data, receiver_data = self._create_users_and_seed_database()

    self._post_login(receiver_data['email'])
    resp = self._bid_on_user(receiver_data, sender_data)
    self.assertIsNotNone(resp)
    self.assertFalse(resp['success'], msg="Response should have success set to false.")
    self.assertEqual(resp.get('message_key'), 'you_need_to_review',
        msg="Response should have success set to false.")

  def test_receiver_bid_after_sender_review_without_review(self):
    sender_data, receiver_data = self._create_users_and_seed_database()

    srv = SENDER_REVIEW_FIELDS
    fields_dict = {
      srv.RECEIVER_SHOWED_UP: False,
      srv.WOULD_LIKE_TO_PAY: True,
      srv.RECEIVER_RATING: 1,
      srv.QUESTION_TEXT: 'Did receivier show up? Blah blah',
      srv.LOOKED_WORSE_THAN_PICS: True,
    }
    self._leave_review(sender_data['id'], receiver_data['id'], fields_dict)

    resp = self._bid_on_user(sender_data, receiver_data)
    self.assertIsNotNone(resp)
    self.assertFalse(resp.get('success'), msg="Response should have success set to false.")
    self.assertEqual(resp.get('message_key'), 'waiting_on_review',
        msg="Response should have success set to false.")