"""
Exercise and test the /payments/ endpoing and everything in the payments.py view.
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

class PaymentTestCase(HelperTestCase):
    # bid should have customer attached
    # customer should have card attached
    # charging the card should work?

  
  def _sender_bid_receiver_accept_sender_accept(self, sender_dict, receiver_dict):
    self._bid_on_user(sender_dict, receiver_dict)
    self._logout()
    self._post_login('a')
    self._accept_bid(receiver_dict, sender_dict)
    self._logout()
    self._post_login('b')
    self._pay_and_confirm(sender_dict, receiver_dict)

  def test_paid_bid_should_create_customer_and_card(self):
    sender_dict, receiver_dict = self._create_sender_receiver()
    self._sender_bid_receiver_accept_sender_accept(sender_dict, receiver_dict)

    model_dict_b = self._get_login()
    self._logout()
    self._post_login('a')
    model_dict_a = self._get_login()

    self.assertIsNotNone(model_dict_a.get('user'))
    self.assertIsNotNone(model_dict_b.get('user'))
    self.assertIsNone(model_dict_a['user'].get(USER_FIELD_NAMES.CUSTOMER_ID, None))
    self.assertIsNotNone(model_dict_b['user'].get(USER_FIELD_NAMES.CUSTOMER_ID, None))

    all_bids = self._get_bids_from_db()
    self.assertEqual(len(all_bids), 1)
    bid_dict = all_bids[0]
    self.assertIsNotNone(bid_dict.get(BID_FIELD_NAMES.CARD_ID, None))

  def test_bid_card_dedup(self):
    sender_dict, receiver_dict = self._create_sender_receiver()
    self._sender_bid_receiver_accept_sender_accept(sender_dict, receiver_dict)
    self._cancel_bid(sender_dict, receiver_dict)
    self._sender_bid_receiver_accept_sender_accept(sender_dict, receiver_dict)

    all_bids = self._get_bids_from_db()
    self.assertEqual(len(all_bids), 2)
    self.assertEqual(all_bids[0].get(BID_FIELD_NAMES.CARD_ID), all_bids[1].get(BID_FIELD_NAMES.CARD_ID))

if __name__ == '__main__':
  unittest.main()
