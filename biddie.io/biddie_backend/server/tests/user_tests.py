"""
Exercise and test the /users/ endpoing and everything in the users.py view.
"""

from flask.ext.pymongo import PyMongo
from bson.objectid import ObjectId
from server.constants import *
from server.tests.test_helpers import *

import unittest
import server
import json
import datetime


class UsersTestCase(HelperTestCase):
  def test_create_user_then_patch(self):
    receiver_dict = self._create_user(name='a')

    # Patch user's name.
    self._patch_user_first_name(receiver_dict, name='Masha')

    # Get all the data for user.
    model_dict = self._get_login()
    self.assertIsNotNone(model_dict.get('user'),
      msg="User should be retrievable after signup.")

    self.assertEqual(model_dict.get('user').get('first_name', ''), 'Masha',
      msg="Patched user fields should persist.")

  def test_create_user_logout(self):
    # Log user a in.
    self._create_user(name='a')

    # Log user a out.
    logout_response = self._logout()
    self.assertTrue(logout_response.get('success', False),
      msg="Logout should return success: true.")

    login_response = self._get_login()
    self.assertFalse(login_response.get('success', True),
      msg="Checking logged-in status should return success: False after logout.")

  def test_double_create_same_user(self):
    self._create_user(name='a')

    # Try to re-create user a.
    receiver_dict = self._create_user(name='a')
    self.assertIsNone(receiver_dict.get('id', ''),
      msg="User sign-up for pre-existing user should return null id.")

  def test_not_logged_in(self):
    # Initial login attempt should fail.
    login_response = self._get_login()
    self.assertFalse(login_response.get('success', True),
      msg="Nonexistent user login should return false.")

  def test_basic_create_user(self):
    receiver_dict = self._create_user(name='a')
    self.assertIsNotNone(receiver_dict.get('id', None),
      msg="User sign-up should return non-null id.")

  def test_create_user_logout_login(self):
    self._create_user(name='a')
    self._logout()

    login_response = self._post_login(name='a')
    self.assertIsNotNone(login_response.get('user', None), 
      msg="Logging in user that exists should return user in response.")

  def test_sender_bid(self):
    sender_dict, receiver_dict = self._create_sender_receiver()
    self._bid_on_user(sender_dict, receiver_dict)

    model_dict_b = self._get_login()
    bids_by_category = model_dict_b['bids_by_category']
    self.assertEqual(len(bids_by_category.get(
        BID_GROUP_KEYS.YOU_HAVE_BID_ON, [])), 1)
    users_by_category = model_dict_b['users_by_category']
    self.assertEqual(len(users_by_category.get(
        BID_GROUP_KEYS.YOU_HAVE_BID_ON, [])), 1)

    self._logout()
    self._post_login('a')
    model_dict_a = self._get_login()
    bids_by_category = model_dict_a['bids_by_category']
    self.assertEqual(len(bids_by_category.get(
        BID_GROUP_KEYS.HAVE_BID_ON_YOU, [])), 1)
    users_by_category = model_dict_a['users_by_category']
    self.assertEqual(len(users_by_category.get(
        BID_GROUP_KEYS.HAVE_BID_ON_YOU, [])), 1)

  def test_sender_bid_receiver_accept(self):
    sender_dict, receiver_dict = self._create_sender_receiver()
    self._bid_on_user(sender_dict, receiver_dict)
    self._logout()
    self._post_login('a')
    self._accept_bid(receiver_dict, sender_dict)

    model_dict_a = self._get_login()
    self._logout()
    self._post_login('b')
    model_dict_b = self._get_login()

    bids_by_category = model_dict_b['bids_by_category']
    self.assertEqual(len(bids_by_category.get(
        BID_GROUP_KEYS.UNCONFIRMED_UPCOMING_DATES, [])), 1)
    users_by_category = model_dict_b['users_by_category']
    self.assertEqual(len(users_by_category.get(
        BID_GROUP_KEYS.UNCONFIRMED_UPCOMING_DATES, [])), 1)

    bids_by_category = model_dict_a['bids_by_category']
    self.assertEqual(len(bids_by_category.get(
        BID_GROUP_KEYS.UNCONFIRMED_UPCOMING_DATES, [])), 1)
    users_by_category = model_dict_a['users_by_category']
    self.assertEqual(len(users_by_category.get(
        BID_GROUP_KEYS.UNCONFIRMED_UPCOMING_DATES, [])), 1)

  def test_sender_bid_receiver_accept_sender_accept(self):
    sender_dict, receiver_dict = self._create_sender_receiver()
    self._bid_on_user(sender_dict, receiver_dict)
    self._logout()
    self._post_login('a')
    self._accept_bid(receiver_dict, sender_dict)
    self._logout()
    self._post_login('b')
    self._pay_and_confirm(sender_dict, receiver_dict)

    model_dict_b = self._get_login()
    self._logout()
    self._post_login('a')
    model_dict_a = self._get_login()

    bids_by_category = model_dict_b['bids_by_category']
    self.assertEqual(len(bids_by_category.get(
        BID_GROUP_KEYS.CONFIRMED_UPCOMING_DATES, [])), 1)
    users_by_category = model_dict_b['users_by_category']
    self.assertEqual(len(users_by_category.get(
        BID_GROUP_KEYS.CONFIRMED_UPCOMING_DATES, [])), 1)


    bids_by_category = model_dict_a['bids_by_category']
    self.assertEqual(len(bids_by_category.get(
        BID_GROUP_KEYS.CONFIRMED_UPCOMING_DATES, [])), 1)
    users_by_category = model_dict_a['users_by_category']
    self.assertEqual(len(users_by_category.get(
        BID_GROUP_KEYS.CONFIRMED_UPCOMING_DATES, [])), 1)

  def test_sender_bid_receiver_accept_sender_accept_date_passed(self):
    sender_dict, receiver_dict = self._create_sender_receiver()
    self._bid_on_user(sender_dict, receiver_dict)
    self._logout()
    self._post_login('a')
    self._accept_bid(receiver_dict, sender_dict)
    self._logout()
    self._post_login('b')
    self._pay_and_confirm(sender_dict, receiver_dict)

    self._adjust_time_selected(sender_dict, receiver_dict,
        datetime.datetime.utcnow()-datetime.timedelta(days=1))

    model_dict_b = self._get_login()
    self._logout()
    self._post_login('a')
    model_dict_a = self._get_login()

    bids_by_category = model_dict_b['bids_by_category']
    self.assertEqual(len(bids_by_category.get(
        BID_GROUP_KEYS.PAST_UNREVIEWED_DATES, [])), 1)
    users_by_category = model_dict_b['users_by_category']
    self.assertEqual(len(users_by_category.get(
        BID_GROUP_KEYS.PAST_UNREVIEWED_DATES, [])), 1)

    bids_by_category = model_dict_a['bids_by_category']
    self.assertEqual(len(bids_by_category.get(
        BID_GROUP_KEYS.PAST_UNREVIEWED_DATES, [])), 1)
    users_by_category = model_dict_a['users_by_category']
    self.assertEqual(len(users_by_category.get(
        BID_GROUP_KEYS.PAST_UNREVIEWED_DATES, [])), 1)

  def test_grouping_outstanding_bids_four_users(self):
    # Create three users.
    user_a, user_b, user_c, user_d = self._create_four_users()
    self._post_login('a')
    self._bid_on_user(user_a, user_b)
    self._bid_on_user(user_a, user_c)
    self._logout()
    self._post_login('d')
    self._bid_on_user(user_d, user_a)
    self._post_login('a')

    model_dict_a = self._get_login()
    bids_by_category = model_dict_a['bids_by_category']
    self.assertEqual(len(bids_by_category.get(
        BID_GROUP_KEYS.HAVE_BID_ON_YOU, [])), 1)
    self.assertEqual(len(bids_by_category.get(
        BID_GROUP_KEYS.YOU_HAVE_BID_ON, [])), 2)
    users_by_category = model_dict_a['users_by_category']
    self.assertEqual(len(users_by_category.get(
        BID_GROUP_KEYS.HAVE_BID_ON_YOU, [])), 1)
    self.assertEqual(len(users_by_category.get(
        BID_GROUP_KEYS.YOU_HAVE_BID_ON, [])), 2)

  def test_grouping_unconfirmed_bids_four_users(self):
    # Create three users.
    user_a, user_b, user_c, user_d = self._create_four_users()
    self._post_login('a')
    self._bid_on_user(user_a, user_b)
    self._bid_on_user(user_a, user_c)
    self._logout()
    self._post_login('d')
    self._bid_on_user(user_d, user_a)
    self._post_login('a')
    self._accept_bid(user_a, user_d)

    model_dict_a = self._get_login()
    self._logout()
    self._post_login('d')
    model_dict_d = self._get_login()

    bids_by_category = model_dict_a['bids_by_category']
    self.assertEqual(len(bids_by_category.get(
        BID_GROUP_KEYS.UNCONFIRMED_UPCOMING_DATES, [])), 1)
    self.assertEqual(len(bids_by_category.get(
        BID_GROUP_KEYS.YOU_HAVE_BID_ON, [])), 2)
    users_by_category = model_dict_a['users_by_category']
    self.assertEqual(len(users_by_category.get(
        BID_GROUP_KEYS.UNCONFIRMED_UPCOMING_DATES, [])), 1)
    self.assertEqual(len(users_by_category.get(
        BID_GROUP_KEYS.YOU_HAVE_BID_ON, [])), 2)

    bids_by_category = model_dict_d['bids_by_category']
    self.assertEqual(len(bids_by_category.get(
        BID_GROUP_KEYS.UNCONFIRMED_UPCOMING_DATES, [])), 1)
    users_by_category = model_dict_d['users_by_category']
    self.assertEqual(len(users_by_category.get(
        BID_GROUP_KEYS.UNCONFIRMED_UPCOMING_DATES, [])), 1)

  def test_grouping_confirmed_bids_four_users(self):
    # Create three users.
    user_a, user_b, user_c, user_d = self._create_four_users()
    self._post_login('a')
    self._bid_on_user(user_a, user_b)
    self._bid_on_user(user_a, user_c)
    self._logout()
    self._post_login('d')
    self._bid_on_user(user_d, user_a)
    self._post_login('a')
    self._accept_bid(user_a, user_d)
    self._logout()
    self._post_login('d')
    self._pay_and_confirm(user_d, user_a)

    model_dict_d = self._get_login()
    self._logout()
    self._post_login('a')
    model_dict_a = self._get_login()

    bids_by_category = model_dict_d['bids_by_category']
    self.assertEqual(len(bids_by_category.get(
        BID_GROUP_KEYS.CONFIRMED_UPCOMING_DATES, [])), 1)
    users_by_category = model_dict_d['users_by_category']
    self.assertEqual(len(users_by_category.get(
        BID_GROUP_KEYS.CONFIRMED_UPCOMING_DATES, [])), 1)

    bids_by_category = model_dict_a['bids_by_category']
    self.assertEqual(len(bids_by_category.get(
        BID_GROUP_KEYS.CONFIRMED_UPCOMING_DATES, [])), 1)
    self.assertEqual(len(bids_by_category.get(
        BID_GROUP_KEYS.YOU_HAVE_BID_ON, [])), 2)
    users_by_category = model_dict_a['users_by_category']
    self.assertEqual(len(users_by_category.get(
        BID_GROUP_KEYS.CONFIRMED_UPCOMING_DATES, [])), 1)
    self.assertEqual(len(users_by_category.get(
        BID_GROUP_KEYS.YOU_HAVE_BID_ON, [])), 2)

if __name__ == '__main__':
  unittest.main()
