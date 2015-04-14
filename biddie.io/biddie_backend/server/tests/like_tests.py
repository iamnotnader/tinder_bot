"""
Exercise and test the /like/ endpoing and everything in the likes.py view.
"""

from flask.ext.pymongo import PyMongo
from bson.objectid import ObjectId
from server.constants import *

import unittest
import server
import json
import datetime
import stripe

# Import this last to override the stripe api key
from server.tests.test_helpers import *

class LikesTestCase(HelperTestCase):
  def _like_user(self, sender_dict, receiver_dict):
    rv = self.app.post('/like/'+sender_dict['id']+'/',
      headers={'Content-Type': 'application/json'},
      data=json.dumps({ BID_FIELD_NAMES.RECEIVER_ID: receiver_dict['id'] })
    )
    return json.loads(rv.data)

  def _get_num_likes(self, sender_dict):
    rv = self.app.get('/num_likes/'+sender_dict['id']+'/')
    return json.loads(rv.data)

  def _get_likes(self, sender_dict):
    rv = self.app.get('/like/'+sender_dict['id']+'/')
    return json.loads(rv.data)

  def _create_three_users(self):
    user_a = self._create_user(name='a')
    self._logout()
    user_b = self._create_user(name='b')
    self._logout()
    user_c = self._create_user(name='c')
    self._logout()
    return user_a, user_b, user_c

  def _like_logout(self, user_a, user_b):
    self._post_login(user_a['email'])
    resp = self._like_user(user_a, user_b)
    self._logout()
    return resp

  def _get_num_likes_logout(self, user_a):
    self._post_login(user_a['email'])
    resp = self._get_num_likes(user_a)
    self._logout()
    return resp

  def test_two_users_like_each_other(self):
    user_a, user_b, user_c = self._create_three_users()
    self._like_logout(user_a, user_b)
    self._like_logout(user_b, user_a)

    resp = self._get_num_likes_logout(user_a)
    self.assertEqual(resp.get('count', -1), 1)

    resp = self._get_num_likes_logout(user_b)
    self.assertEqual(resp.get('count', -1), 1)

  def test_sender_like_sender(self):
    sender_dict, receiver_dict = self._create_sender_receiver()
    resp = self._like_logout(sender_dict, sender_dict)

    bids = self._get_bids_from_db()
    self.assertEqual(len(bids), 0)
    self.assertEqual(resp['message_key'], 'like_yourself')

  def test_one_user_like_one(self):
    user_a, user_b, user_c = self._create_three_users()
    self._like_logout(user_a, user_b)

    bids = self._get_bids_from_db()
    self.assertEqual(len(bids), 1)
    self.assertEqual(bids[0][BID_FIELD_NAMES.BID_STATE],
        BID_STATES.SENDER_LIKED)

    resp = self._get_num_likes_logout(user_a)
    self.assertEqual(resp.get('count', -1), 0)

    resp = self._get_num_likes_logout(user_b)
    self.assertEqual(resp.get('count', -1), 1)

  def test_two_users_like_one(self):
    user_a, user_b, user_c = self._create_three_users()
    self._like_logout(user_a, user_c)
    self._like_logout(user_b, user_c)

    resp = self._get_num_likes_logout(user_c)
    self.assertEqual(resp.get('count', -1), 2)
    resp = self._get_num_likes_logout(user_b)
    self.assertEqual(resp.get('count', -1), 0)
    resp = self._get_num_likes_logout(user_a)
    self.assertEqual(resp.get('count', -1), 0)

  def test_one_user_like_two_get_login(self):
    user_a, user_b, user_c = self._create_three_users()
    self._like_logout(user_a, user_c)
    self._like_logout(user_a, user_b)

    self._post_login('a')
    resp = self._get_login()
    user_likes = resp.get('users_by_category', None).get('user_likes')
    self.assertEqual(len(user_likes), 2)
    self.assertTrue('b' in [u['email'] for u in user_likes])
    self.assertTrue('c' in [u['email'] for u in user_likes])

    user_likes = self._get_likes(user_a)
    self.assertEqual(len(user_likes), 2)
    self.assertTrue('b' in [u['email'] for u in user_likes])
    self.assertTrue('c' in [u['email'] for u in user_likes])    
    self._logout()

    self._post_login('b')
    resp = self._get_login()
    user_likes = resp.get('users_by_category', None).get('user_likes')
    self.assertEqual(len(user_likes), 0)
    user_likes = self._get_likes(user_b)
    self.assertEqual(len(user_likes), 0)
    self._logout()

    self._post_login('c')
    resp = self._get_login()
    user_likes = resp.get('users_by_category', None).get('user_likes')
    self.assertEqual(len(user_likes), 0)

    self._logout()
    self._post_login('b')
    user_likes = self._get_likes(user_b)
    self.assertEqual(len(user_likes), 0)
    self._logout()

  def test_sender_like_sender_bid(self):
    sender_dict, receiver_dict = self._create_sender_receiver()

    self._like_user(sender_dict, receiver_dict)
    self._bid_on_user(sender_dict, receiver_dict)
    self._logout()

    bids = self._get_bids_from_db()
    self.assertEqual(len(bids), 1)
    self.assertEqual(bids[0][BID_FIELD_NAMES.BID_STATE], BID_STATES.OUTSTANDING)
    self.assertEqual(len(bids[0][BID_FIELD_NAMES.TIMESTAMP_LIST]), 1)

  def test_sender_like_sender_cancel(self):
    sender_dict, receiver_dict = self._create_sender_receiver()

    self._like_user(sender_dict, receiver_dict)
    self._cancel_bid(sender_dict, receiver_dict)
    self._logout()

    bids = self._get_bids_from_db()
    self.assertEqual(len(bids), 1)
    self.assertEqual(bids[0][BID_FIELD_NAMES.BID_STATE], BID_STATES.SENDER_UNLIKED)
    self.assertEqual(len(bids[0][BID_FIELD_NAMES.TIMESTAMP_LIST]), 1)

  def test_sender_like_sender_cancel_sender_like(self):
    sender_dict, receiver_dict = self._create_sender_receiver()

    self._like_user(sender_dict, receiver_dict)
    self._cancel_bid(sender_dict, receiver_dict)
    self._like_user(sender_dict, receiver_dict)
    self._logout()

    bids = self._get_bids_from_db()
    self.assertEqual(len(bids), 2)
    self.assertEqual(bids[0][BID_FIELD_NAMES.BID_STATE], BID_STATES.SENDER_LIKED)
    self.assertEqual(bids[1][BID_FIELD_NAMES.BID_STATE], BID_STATES.SENDER_UNLIKED)

  def test_sender_like_sender_cancel_sender_like_sender_bid(self):
    sender_dict, receiver_dict = self._create_sender_receiver()

    self._like_user(sender_dict, receiver_dict)
    self._cancel_bid(sender_dict, receiver_dict)
    self._like_user(sender_dict, receiver_dict)
    self._bid_on_user(sender_dict, receiver_dict)
    self._logout()

    bids = self._get_bids_from_db()
    self.assertEqual(len(bids), 2)
    self.assertEqual(bids[0][BID_FIELD_NAMES.BID_STATE], BID_STATES.OUTSTANDING)
    self.assertEqual(bids[1][BID_FIELD_NAMES.BID_STATE], BID_STATES.SENDER_UNLIKED)

  def test_sender_like_receiver_like_sender_bid(self):
    sender_dict, receiver_dict = self._create_sender_receiver()
    self._like_logout(sender_dict, receiver_dict)
    self._like_logout(receiver_dict, sender_dict)

    self._post_login(sender_dict['email'])
    self._bid_on_user(sender_dict, receiver_dict)
    self._logout()

    bids = self._get_bids_from_db()
    self.assertEqual(len(bids), 3)
    self.assertEqual(bids[0][BID_FIELD_NAMES.BID_STATE], BID_STATES.OUTSTANDING)
    self.assertEqual(bids[1][BID_FIELD_NAMES.BID_STATE], BID_STATES.SENDER_LIKED)
    self.assertEqual(bids[2][BID_FIELD_NAMES.BID_STATE], BID_STATES.SENDER_LIKED)

  def test_sender_like_sender_like(self):
    sender_dict, receiver_dict = self._create_sender_receiver()
    self._like_logout(sender_dict, receiver_dict)
    resp = self._like_logout(sender_dict, receiver_dict)
    self.assertEqual(resp['message_key'], 'already_liked')

    bids = self._get_bids_from_db()
    self.assertEqual(len(bids), 1)
    self.assertEqual(bids[0][BID_FIELD_NAMES.BID_STATE], BID_STATES.SENDER_LIKED)

  def test_sender_like_receiver_accept(self):
    sender_dict, receiver_dict = self._create_sender_receiver()
    self._like_logout(sender_dict, receiver_dict)

    self._post_login(receiver_dict['email'])
    resp = self._accept_bid(receiver_dict, sender_dict, 0)
    self.assertEqual(resp['message_key'], 'nothing_to_accept')


if __name__ == '__main__':
  unittest.main()
