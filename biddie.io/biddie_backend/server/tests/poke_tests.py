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


class PokesTestCase(HelperTestCase):
  def _poke_user(self, sender_id, receiver_id):
    resp = self.app.post('/pokes/create/'+sender_id+'/', 
      headers={'Content-Type': 'application/json'},
      data=json.dumps({
        BID_FIELD_NAMES.RECEIVER_ID: receiver_id
      })
    )
    return json.loads(resp.data)

  def _cancel_poke(self, sender_id, poke_sender_id, poke_receiver_id):
    resp = self.app.post('/pokes/cancel/'+sender_id+'/', 
      headers={'Content-Type': 'application/json'},
      data=json.dumps({
        BID_FIELD_NAMES.RECEIVER_ID: poke_receiver_id,
        BID_FIELD_NAMES.SENDER_ID: poke_sender_id
      })
    )
    return json.loads(resp.data)

  def test_sender_poke(self):
    [sender_data, receiver_data] = self._create_n_random_users(2)
    self._post_login(sender_data['email'])

    resp = self._poke_user(sender_data['id'], receiver_data['id'])

    with server.app.app_context():
      poke_created = server.app.config['DATABASE'].db.pokes.find_one({})
    self.assertIsNotNone(resp)
    self.assertTrue(resp['success'], msg="Response should have success set to true.")
    self.assertIsNotNone(poke_created, msg="Poke created shouldn't be non-None")
    self.assertEqual(
      poke_created[BID_FIELD_NAMES.SENDER_ID], ObjectId(sender_data['id']))
    self.assertEqual(
      poke_created[BID_FIELD_NAMES.RECEIVER_ID], ObjectId(receiver_data['id']))


  def test_sender_poke_sender_cancel(self):
    [sender_data, receiver_data] = self._create_n_random_users(2)
    self._post_login(sender_data['email'])

    self._poke_user(sender_data['id'], receiver_data['id'])
    resp = self._cancel_poke(sender_data['id'], sender_data['id'], receiver_data['id'])

    with server.app.app_context():
      poke_created = server.app.config['DATABASE'].db.pokes.find_one({})

    self.assertIsNotNone(resp)
    self.assertTrue(resp['success'], msg="Response should have success set to true.")
    self.assertIsNotNone(poke_created, msg="Poke created shouldn't be non-None")
    self.assertEqual(
      poke_created[BID_FIELD_NAMES.BID_STATE], POKE_STATES.POKE_CANCELLED_BY_POKER)


  def test_sender_poke_receiver_cancel(self):
    [sender_data, receiver_data] = self._create_n_random_users(2)
    self._post_login(sender_data['email'])

    # Create the poke
    self._poke_user(sender_data['id'], receiver_data['id'])

    # Cancel the poke
    self._logout()
    self._post_login(receiver_data['email'])
    # Note that the first argument is receiver not sender.
    resp = self._cancel_poke(receiver_data['id'], sender_data['id'], receiver_data['id'])

    with server.app.app_context():
      poke_created = server.app.config['DATABASE'].db.pokes.find_one({})

    self.assertIsNotNone(resp)
    self.assertTrue(resp['success'], msg=str(resp))
    self.assertIsNotNone(poke_created, msg="Poke created shouldn't be non-None")
    self.assertEqual(
      poke_created[BID_FIELD_NAMES.BID_STATE], POKE_STATES.POKE_REJECTED_BY_OTHER)


  def test_sender_poke_twice(self):
    [sender_data, receiver_data] = self._create_n_random_users(2)
    self._post_login(sender_data['email'])

    # Create the poke
    self._poke_user(sender_data['id'], receiver_data['id'])
    resp = self._poke_user(sender_data['id'], receiver_data['id'])

    self.assertFalse(resp['success'])
    self.assertEqual(resp['message_key'], 'already_poked')


  def test_sender_poke_cancel_twice(self):
    [sender_data, receiver_data] = self._create_n_random_users(2)
    self._post_login(sender_data['email'])

    # Create the poke
    self._poke_user(sender_data['id'], receiver_data['id'])

    # Cancel the poke
    self._cancel_poke(sender_data['id'], sender_data['id'], receiver_data['id'])

    # Cancel a second time
    resp = self._cancel_poke(sender_data['id'], sender_data['id'], receiver_data['id'])

    self.assertFalse(resp['success'])
    self.assertEqual(resp['message_key'], 'no_poke_to_cancel')

  def test_sender_poke_cancel_wrong_poke(self):
    [sender_data, receiver_data, third_guy] = self._create_n_random_users(3)
    self._post_login(sender_data['email'])

    # Create the poke
    self._poke_user(sender_data['id'], receiver_data['id'])
    
    # Try to cancel a non-existent poke
    resp = self._cancel_poke(sender_data['id'], receiver_data['id'], third_guy['id'])

    self.assertFalse(resp['success'])
    self.assertEqual(resp['message_key'], 'unaffiliated_poke_cancellation')