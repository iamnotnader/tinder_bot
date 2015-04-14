"""
Exercise and test the /bids/ endpoing and everything in the bids.py view.
"""

from flask.ext.pymongo import PyMongo
from bson.objectid import ObjectId
from server.constants import *
from server.tests.test_helpers import *
from server.utils import *

import unittest
import server
import json
import datetime


class BidsTestCase(HelperTestCase):
  def test_single_user_search_results(self):
    self._create_user(name='a')

    # Make sure the search results are empty.
    search_response = self._basic_search(must_have_photos=False)
    self.assertEqual(len(search_response), 0,
      'No users should be returned in search results when there is only one user.')

  def test_search_two_users(self):
    self._create_user(name='a')
    self._logout()
    self._create_user(name='b')

    search_response = self._basic_search(must_have_photos=True)
    self.assertEqual(len(search_response), 0,
      'Search results should be empty if we only want users with photos.')

    search_response = self._basic_search(must_have_photos=False)
    self.assertEqual(len(search_response), 1,
      'Should see user "a" when we search for users with+without photos.')

  def test_photo_upload_sorting(self):
    sender_dict = self._create_user(name='b')

    # Post a few photos for user b
    self._post_three_photos(sender_dict)

    # Make sure the posted photos are persisted and returned in the right order.
    photos_response = self._get_photos_for_user(sender_dict)
    photo_positions = [x['photo_position'] for x in photos_response]
    self.assertEqual(photo_positions, [1, 2, 3],
      'Photos should persist and be sorted by position.')

  def test_sender_bid_on_sender(self):
    sender_dict, receiver_dict = self._create_sender_receiver()

    resp = self._bid_on_user(sender_dict, sender_dict)

    bids = self._get_bids_from_db()
    self.assertEqual(len(bids), 0)
    self.assertEqual(resp['message_key'], 'bid_on_yourself')

  def test_sender_bid_sender_bid(self):
    sender_dict, receiver_dict = self._create_sender_receiver()

    self._bid_on_user(sender_dict, receiver_dict)
    self._bid_on_user(sender_dict, receiver_dict, amount="69")

    # Bid amount should update.
    updated_bids = self._get_bids_from_db()
    bid_amount = updated_bids[0].get(BID_FIELD_NAMES.BID_AMOUNT, None)
    self.assertEqual(bid_amount, 69,
      msg="Bid amount should update.")

  def test_simple_user_bid(self):
    sender_dict, receiver_dict = self._create_sender_receiver()

    # Make b bid on a.
    self._bid_on_user(sender_dict, receiver_dict)

    # Ensure everything updated properly.
    updated_bids = self._get_bids_from_db()
    self.assertEqual(len(updated_bids), 1, 
      msg="User should show up in biddie list after being bid on.")
    bid_state = updated_bids[0].get('bid_state', None)
    self.assertEqual(bid_state, BID_STATES.OUTSTANDING,
      msg="Bid state should be 'outstanding' after initial bid.")

  def test_sender_bid_sender_cancel(self):
    sender_dict, receiver_dict = self._create_sender_receiver()

    self._bid_on_user(sender_dict, receiver_dict)

    # Make b cancel the bid.
    self._cancel_bid(sender_dict, receiver_dict)
    updated_bids = self._get_bids_from_db()

    self.assertEqual(len(updated_bids), 1,
      msg="There should be exactly one cancelled bid.")

    self.assertEqual(
      updated_bids[0].get('bid_state'),
      BID_STATES.SENDER_CANCELLED_BEFORE_ACCEPTED,
      msg="Bid state should be 'sender_cancelled_after_accepted' after initial bid."
    )

  def test_sender_bid_sender_cancel_timestamps(self):
    sender_dict, receiver_dict = self._create_sender_receiver()
    self._bid_on_user(sender_dict, receiver_dict)

    # Make b cancel the bid.
    self._cancel_bid(sender_dict, receiver_dict)
    updated_bids = self._get_bids_from_db()

    self.assertEqual(len(updated_bids[0][BID_FIELD_NAMES.TIMESTAMP_LIST]), 1,
      msg="There should be a timestamp on the updated bid.")
    self.assertEqual(updated_bids[0][BID_FIELD_NAMES.TIMESTAMP_LIST][0][0],
      BID_STATES.SENDER_CANCELLED_BEFORE_ACCEPTED,
      msg="There state should be properly set on the timestamp.")

  def test_sender_bid_sender_cancel_sender_bid(self):
    sender_dict, receiver_dict = self._create_sender_receiver()

    self._bid_on_user(sender_dict, receiver_dict)
    self._cancel_bid(sender_dict, receiver_dict)
    self._bid_on_user(sender_dict, receiver_dict)

    # Ensure everything updated properly.
    updated_bids = self._get_bids_from_db()
    self.assertEqual(len(updated_bids), 2, 
      msg="User should show up in biddie list after being bid on.")
    self.assertEqual(
      updated_bids[0].get(BID_FIELD_NAMES.BID_STATE, None),
      BID_STATES.OUTSTANDING,
      msg="Bid state should be 'outstanding' after initial bid.")
    self.assertEqual(
      updated_bids[1].get(BID_FIELD_NAMES.BID_STATE, None),
      BID_STATES.SENDER_CANCELLED_BEFORE_ACCEPTED,
      msg="Bid state should be 'outstanding' after initial bid.")

  def test_sender_bid_receiver_reject(self):
    sender_dict, receiver_dict = self._create_sender_receiver()
    self._bid_on_user(sender_dict, receiver_dict)
    self._post_login(name='a')

    # At this point we are logged in as a, and we have an offer on us.
    self._cancel_bid(receiver_dict, sender_dict)

    updated_bids = self._get_bids_from_db()
    self.assertEqual(len(updated_bids), 1, 
      msg="Should have exactly one rejected bid.")
    self.assertEqual(
      updated_bids[0].get(BID_FIELD_NAMES.BID_STATE, None),
      BID_STATES.RECEIVER_REJECTED,
      msg="Bid state should be receiver_rejected."
    )

  def test_sender_bid_receiver_reject_timestamps(self):
    sender_dict, receiver_dict = self._create_sender_receiver()
    self._bid_on_user(sender_dict, receiver_dict)
    self._post_login(name='a')

    # At this point we are logged in as a, and we have an offer on us.
    self._cancel_bid(receiver_dict, sender_dict)

    updated_bids = self._get_bids_from_db()
    self.assertEqual(len(updated_bids[0][BID_FIELD_NAMES.TIMESTAMP_LIST]), 1,
      msg="There should be a timestamp on the updated bid.")
    self.assertEqual(updated_bids[0][BID_FIELD_NAMES.TIMESTAMP_LIST][0][0],
      BID_STATES.RECEIVER_REJECTED,
      msg="There state should be set properly on the timestamp.")

  def test_sender_bid_sender_cancel_sender_bid_receiver_reject(self):
    sender_dict, receiver_dict = self._create_sender_receiver()

    self._bid_on_user(sender_dict, receiver_dict)
    self._cancel_bid(sender_dict, receiver_dict)
    self._bid_on_user(sender_dict, receiver_dict)
    self._logout()

    self._post_login(name='a')

    # At this point we are logged in as a, and we have an offer on us.
    self._cancel_bid(receiver_dict, sender_dict)

    updated_bids = self._get_bids_from_db()

    self.assertEqual(len(updated_bids), 2,
      msg="Should have exactly two bids-- first rejected, second cancelled.")
    self.assertEqual(
      updated_bids[0].get(BID_FIELD_NAMES.BID_STATE, None),
      BID_STATES.RECEIVER_REJECTED,
      msg="Bid state should be receiver_rejected."
    )
    self.assertEqual(
      updated_bids[1].get(BID_FIELD_NAMES.BID_STATE, None),
      BID_STATES.SENDER_CANCELLED_BEFORE_ACCEPTED,
      msg="Bid state should be receiver_rejected."
    )

  def test_sender_bid_receiver_bid(self):
    sender_dict, receiver_dict = self._create_sender_receiver()
    self._bid_on_user(sender_dict, receiver_dict)
    self._logout()
    self._post_login(name='a')
    resp = self._bid_on_user(receiver_dict, sender_dict)
    self.assertEqual(resp['message'], ERROR_MESSAGES['outstanding_offer'], 
      msg="Receiver should not be able to bid on sender with outstanding bid.")

  def test_sender_bid_receiver_reject_receiver_bid(self):
    sender_dict, receiver_dict = self._create_sender_receiver()

    self._bid_on_user(sender_dict, receiver_dict)
    self._logout()
    self._post_login(name='a')
    self._cancel_bid(receiver_dict, sender_dict)
    self._bid_on_user(receiver_dict, sender_dict)
    
    bids = self._get_bids_from_db()
    self.assertEqual(len(bids), 2, 
      msg="There should be a rejected bid and an outstanding bid.")
    self.assertEqual(str(bids[0].get(BID_FIELD_NAMES.SENDER_ID, None)), receiver_dict['id'])
    self.assertEqual(str(bids[1].get(BID_FIELD_NAMES.SENDER_ID, None)), sender_dict['id'])

    self.assertEqual(bids[0].get(BID_FIELD_NAMES.BID_STATE, None), BID_STATES.OUTSTANDING)
    self.assertEqual(bids[1].get(BID_FIELD_NAMES.BID_STATE, None), BID_STATES.RECEIVER_REJECTED)

  def test_receiver_accept(self):
    sender_dict = self._create_user(name='b')
    self._logout()
    receiver_dict = self._create_user(name='a')

    resp = self._accept_bid(receiver_dict, sender_dict)
    self.assertEqual(resp['message'], ERROR_MESSAGES['nothing_to_accept'], 
      msg="There shouldn't be anything to accept.")

  def test_sender_bid_receiver_accept(self):
    sender_dict, receiver_dict = self._create_sender_receiver()

    self._bid_on_user(sender_dict, receiver_dict)
    self._logout()
    self._post_login(name='a')
    self._accept_bid(receiver_dict, sender_dict)

    bids = self._get_bids_from_db()
    self.assertEqual(len(bids), 1, 
      msg="There should be a single accepted bid.")
    self.assertEqual(bids[0].get(BID_FIELD_NAMES.BID_STATE, None), BID_STATES.RECEIVER_ACCEPTED)

  def test_sender_bid_receiver_reject_receiver_accept(self):
    sender_dict, receiver_dict = self._create_sender_receiver()

    self._bid_on_user(sender_dict, receiver_dict)
    self._logout()
    self._post_login(name=receiver_dict['email'])
    self._cancel_bid(receiver_dict, sender_dict)
    resp = self._accept_bid(receiver_dict, sender_dict)

    resp = self._accept_bid(receiver_dict, sender_dict)
    self.assertEqual(resp['message'], ERROR_MESSAGES['nothing_to_accept'], 
      msg="There shouldn't be anything to accept.")

  def test_sender_bid_receiver_accept_receiver_bid(self):
    sender_dict, receiver_dict = self._create_sender_receiver()

    self._bid_on_user(sender_dict, receiver_dict)
    self._logout()
    self._post_login(name='a')
    self._accept_bid(receiver_dict, sender_dict)
    resp = self._bid_on_user(receiver_dict, sender_dict)
    self.assertEqual(resp['message'], ERROR_MESSAGES['cant_bid_after_accepted'], 
      msg="There shouldn't be anything to accept.")

  def test_sender_bid_receiver_accept_receiver_reject(self):
    sender_dict, receiver_dict = self._create_sender_receiver()

    self._bid_on_user(sender_dict, receiver_dict)
    self._logout()
    self._post_login(name='a')
    self._accept_bid(receiver_dict, sender_dict)
    self._cancel_bid(receiver_dict, sender_dict)
    bids = self._get_bids_from_db()
    self.assertEqual(len(bids), 1, 
      msg="There should be a single rejected bid.")
    self.assertEqual(bids[0].get(BID_FIELD_NAMES.BID_STATE, None), BID_STATES.RECEIVER_REJECTED)

  def test_sender_bid_receiver_accept_receiver_reject_timestamps(self):
    sender_dict, receiver_dict = self._create_sender_receiver()

    self._bid_on_user(sender_dict, receiver_dict)
    self._logout()
    self._post_login(name='a')
    self._accept_bid(receiver_dict, sender_dict)
    self._cancel_bid(receiver_dict, sender_dict)

    updated_bids = self._get_bids_from_db()
    self.assertEqual(len(updated_bids[0][BID_FIELD_NAMES.TIMESTAMP_LIST]), 2,
      msg="There should be a timestamp on the updated bid.")
    self.assertEqual(updated_bids[0][BID_FIELD_NAMES.TIMESTAMP_LIST][0][0],
      BID_STATES.RECEIVER_ACCEPTED,
      msg="There state should be set properly on the timestamp.")
    self.assertEqual(updated_bids[0][BID_FIELD_NAMES.TIMESTAMP_LIST][1][0],
      BID_STATES.RECEIVER_REJECTED,
      msg="There state should be set properly on the timestamp.")

  def test_sender_bid_receiver_accept_sender_bid(self):
    sender_dict, receiver_dict = self._create_sender_receiver()

    self._bid_on_user(sender_dict, receiver_dict)
    self._logout()
    self._post_login(name='a')
    self._accept_bid(receiver_dict, sender_dict)

    self._logout()
    self._post_login(name='b')
    resp = self._bid_on_user(sender_dict, receiver_dict)
    self.assertEqual(resp['message'], ERROR_MESSAGES['cannot_bid_receiver_accepted'], 
      msg="There shouldn't be anything to accept.")

  def test_sender_bid_receiver_reject_sender_accept(self):
    sender_dict, receiver_dict = self._create_sender_receiver()

    # b bids on a and logs out.
    self._bid_on_user(sender_dict, receiver_dict)
    self._logout()

    # a logs in and REJECTs b's offer then logs out.
    self._post_login(name='a')
    self._cancel_bid(receiver_dict, sender_dict)
    self._logout()

    # b logs in and confirms the offer.
    self._post_login(name='b')
    resp = self._pay_and_confirm(sender_dict, receiver_dict)

    self.assertEqual(resp['message'], ERROR_MESSAGES['cannot_pay_for_unaccepted_bid'], 
      msg="There shouldn't be anything to accept.")

  def test_sender_bid_receiver_reject_sender_bid(self):
    sender_dict, receiver_dict = self._create_sender_receiver()

    # b bids on a and logs out.
    self._bid_on_user(sender_dict, receiver_dict)
    self._logout()

    # a logs in and REJECTs b's offer then logs out.
    self._post_login(name='a')
    self._cancel_bid(receiver_dict, sender_dict)
    self._logout()

    # b logs in and confirms the offer.
    self._post_login(name='b')
    resp = self._bid_on_user(sender_dict, receiver_dict)
    self.assertEqual(resp['message'], ERROR_MESSAGES['cannot_bid_after_rejection'], 
      msg="There shouldn't be anything to accept.")

    updated_bids = self._get_bids_from_db()
    self.assertEqual(len(updated_bids), 1,
      msg="Should have exactly one rejected bid.")
    self.assertEqual(
      updated_bids[0].get(BID_FIELD_NAMES.BID_STATE, None),
      BID_STATES.RECEIVER_REJECTED,
      msg="Bid state should be receiver_rejected."
    )

  def _sender_bid_receiver_accept_sender_accept_with_payment_change_date(self, sender_dict, receiver_dict, day_delta):
    # b bids on a and logs out.
    self._bid_on_user(sender_dict, receiver_dict)
    self._logout()

    # a logs in and accepts b's offer then logs out.
    self._post_login(name='a')
    self._accept_bid(receiver_dict, sender_dict)
    self._logout()

    # b logs in and confirms the offer.
    self._post_login(name='b')
    self._pay_and_confirm(sender_dict, receiver_dict)
    self._logout()

    # Change the time on the bid
    new_time = datetime.datetime.utcnow() + datetime.timedelta(days=day_delta)
    self._adjust_time_selected(sender_dict, receiver_dict, new_time)

  def test_sender_bid_receiver_accept_sender_accept_with_payment(self):
    sender_dict, receiver_dict = self._create_sender_receiver()

    self._sender_bid_receiver_accept_sender_accept_with_payment_change_date(sender_dict, receiver_dict, 1)

    bids = self._get_bids_from_db()
    self.assertEqual(len(bids), 1, 
      msg="There should be a single accepted bid.")
    self.assertEqual(bids[0].get(BID_FIELD_NAMES.BID_STATE, None), BID_STATES.SENDER_CONFIRMED)

  def test_sender_bid_receiver_accept_sender_accept_timestamps(self):
    sender_dict, receiver_dict = self._create_sender_receiver()
    self._sender_bid_receiver_accept_sender_accept_with_payment_change_date(sender_dict, receiver_dict, 1)

    updated_bids = self._get_bids_from_db()
    self.assertEqual(len(updated_bids[0][BID_FIELD_NAMES.TIMESTAMP_LIST]), 2,
      msg="There should be a timestamp on the updated bid.")
    self.assertEqual(updated_bids[0][BID_FIELD_NAMES.TIMESTAMP_LIST][0][0],
      BID_STATES.RECEIVER_ACCEPTED,
      msg="There state should be properly set on the timestamp.")
    self.assertEqual(updated_bids[0][BID_FIELD_NAMES.TIMESTAMP_LIST][1][0],
      BID_STATES.SENDER_CONFIRMED,
      msg="There state should be properly set on the timestamp.")

  def test_sender_bid_receiver_accept_sender_accept_receiver_cancel(self):
    sender_dict, receiver_dict = self._create_sender_receiver()
    self._sender_bid_receiver_accept_sender_accept_with_payment_change_date(sender_dict, receiver_dict, 1)

    self._post_login(name='a')
    self._cancel_bid(receiver_dict, sender_dict)

    bids = self._get_bids_from_db()
    self.assertEqual(len(bids), 1,
      msg="There should be a sender_confirmed bid and an outstanding bid.")
    self.assertEqual(bids[0].get(BID_FIELD_NAMES.BID_STATE, None), BID_STATES.RECEIVER_CANCELLED_AFTER_CONFIRMED)

  def test_sender_bid_receiver_accept_sender_accept_sender_cancel(self):
    sender_dict, receiver_dict = self._create_sender_receiver()
    self._sender_bid_receiver_accept_sender_accept_with_payment_change_date(sender_dict, receiver_dict, 1)
    self._cancel_bid(sender_dict, receiver_dict)

    bids = self._get_bids_from_db()
    self.assertEqual(len(bids), 1,
      msg="There should be a sender_confirmed bid and a cancelled bid.")
    self.assertEqual(bids[0].get(BID_FIELD_NAMES.BID_STATE, None), BID_STATES.SENDER_CANCELLED_AFTER_CONFIRMED)

  def test_sender_bid_receiver_accept_sender_accept_sender_cancel_timestamps(self):
    sender_dict, receiver_dict = self._create_sender_receiver()
    self._sender_bid_receiver_accept_sender_accept_with_payment_change_date(sender_dict, receiver_dict, 1)
    self._cancel_bid(sender_dict, receiver_dict)

    updated_bids = self._get_bids_from_db()

    self.assertEqual(len(updated_bids[0][BID_FIELD_NAMES.TIMESTAMP_LIST]), 3,
      msg="There should be a timestamp on the updated bid.")

    self.assertEqual(updated_bids[0][BID_FIELD_NAMES.TIMESTAMP_LIST][0][0],
      BID_STATES.RECEIVER_ACCEPTED,
      msg="There state should be properly set on the timestamp.")
    self.assertEqual(updated_bids[0][BID_FIELD_NAMES.TIMESTAMP_LIST][1][0],
      BID_STATES.SENDER_CONFIRMED,
      msg="There state should be properly set on the timestamp.")
    self.assertEqual(updated_bids[0][BID_FIELD_NAMES.TIMESTAMP_LIST][2][0],
      BID_STATES.SENDER_CANCELLED_AFTER_CONFIRMED,
      msg="There state should be properly set on the timestamp.")

  def test_sender_bid_receiver_accept_sender_accept_receiver_cancel_timestamps(self):
    sender_dict, receiver_dict = self._create_sender_receiver()
    self._sender_bid_receiver_accept_sender_accept_with_payment_change_date(sender_dict, receiver_dict, 1)

    self._post_login(name='a')
    self._cancel_bid(receiver_dict, sender_dict)

    updated_bids = self._get_bids_from_db()

    self.assertEqual(len(updated_bids[0][BID_FIELD_NAMES.TIMESTAMP_LIST]), 3,
      msg="There should be a timestamp on the updated bid.")
    self.assertEqual(updated_bids[0][BID_FIELD_NAMES.TIMESTAMP_LIST][0][0],
      BID_STATES.RECEIVER_ACCEPTED,
      msg="There state should be properly set on the timestamp.")
    self.assertEqual(updated_bids[0][BID_FIELD_NAMES.TIMESTAMP_LIST][1][0],
      BID_STATES.SENDER_CONFIRMED,
      msg="There state should be properly set on the timestamp.")
    self.assertEqual(updated_bids[0][BID_FIELD_NAMES.TIMESTAMP_LIST][2][0],
      BID_STATES.RECEIVER_CANCELLED_AFTER_CONFIRMED,
      msg="There state should be properly set on the timestamp.")

  def test_sender_bid_receiver_accept_sender_accept_receiver_bid_before_date(self):
    sender_dict, receiver_dict = self._create_sender_receiver()
    self._sender_bid_receiver_accept_sender_accept_with_payment_change_date(sender_dict, receiver_dict, 1)

    # Bid should fail because of pending date.
    self._post_login(name='a')
    resp = self._bid_on_user(receiver_dict, sender_dict)

    self.assertEqual(resp['message'], ERROR_MESSAGES['pending_date'], 
      msg="Bid should fail if there's pending date.")

  def test_sender_bid_receiver_accept_sender_accept_sender_bid_before_date(self):
    sender_dict, receiver_dict = self._create_sender_receiver()
    self._sender_bid_receiver_accept_sender_accept_with_payment_change_date(sender_dict, receiver_dict, 1)

    # Bid should fail because of pending date.
    self._post_login(name='b')
    resp = self._bid_on_user(sender_dict, receiver_dict)

    self.assertEqual(resp['message'], ERROR_MESSAGES['pending_date'], 
      msg="Bid should fail if there's pending date.")

  def test_sender_bid_date_passed(self):
    sender_dict, receiver_dict = self._create_sender_receiver()
    resp = self._bid_on_user(sender_dict, receiver_dict,
      input_date=(datetime.datetime.utcnow() - datetime.timedelta(days=1)))

    self.assertEqual(resp['message'], ERROR_MESSAGES['date_passed'], 
      msg="Bid should fail if there's pending date.")

  def test_sender_bid_date_passed_receiver_accept(self):
    sender_dict, receiver_dict = self._create_sender_receiver()
    self._bid_on_user(sender_dict, receiver_dict)
    self._logout()
    self._adjust_time_selected(sender_dict, receiver_dict,
      input_date=datetime.datetime.utcnow() - datetime.timedelta(days=1))
    self._post_login('a')
    resp = self._accept_bid(receiver_dict, sender_dict)

    self.assertEqual(resp['message'], ERROR_MESSAGES['date_passed'], 
      msg="Bid should fail if the date has passed")

  def test_sender_bid_receiver_accept_date_passed(self):
    sender_dict, receiver_dict = self._create_sender_receiver()
    self._bid_on_user(sender_dict, receiver_dict)
    self._logout()
    self._post_login('a')
    self._accept_bid(receiver_dict, sender_dict)
    self._adjust_time_selected(sender_dict, receiver_dict,
      input_date=datetime.datetime.utcnow() - datetime.timedelta(days=1))

    self._logout()
    self._post_login('b')
    resp = self._bid_on_user(sender_dict, receiver_dict)

    self.assertIsNone(resp.get('message', None), 
      msg="Bid should succeed if the date has passed")

  def test_sender_bid_receiver_accept_sender_accept_with_payment_date_passed(self):
    sender_dict, receiver_dict = self._create_sender_receiver()
    self._bid_on_user(sender_dict, receiver_dict)
    self._logout()

    self._post_login('a')
    self._accept_bid(receiver_dict, sender_dict)
    self._logout()

    self._adjust_time_selected(sender_dict, receiver_dict,
      input_date=datetime.datetime.utcnow() - datetime.timedelta(days=1))

    self._post_login('b')
    resp = self._pay_and_confirm(sender_dict, receiver_dict)

    self.assertEqual(resp['message'], ERROR_MESSAGES['cannot_pay_for_expired_date'], 
      msg="Bid should fail if the date has passed")

  def test_get_bids_four_users(self):
    # Create three users.
    user_a, user_b, user_c, user_d = self._create_four_users()
    self._post_login('a')
    self._bid_on_user(user_a, user_b)
    self._bid_on_user(user_a, user_c)
    self._logout()
    self._post_login('d')
    self._bid_on_user(user_d, user_a)
    self._post_login('a')

    resp = json.loads(self.app.get('/bids/'+user_a['id']+'/').data)
    self.assertEqual(len(resp), 3,
      msg="There should be three bids on a")

  def test_bid_expired(self):
    expired_outstanding_bid = {
      BID_FIELD_NAMES.BID_STATE: BID_STATES.OUTSTANDING,
      BID_FIELD_NAMES.TIMES_AND_PLACES_LIST: [
        {BID_FIELD_NAMES.SECONDS_SINCE_EPOCH: self.seconds_since_utc_epoch(
            datetime.datetime.utcnow() - datetime.timedelta(days=1))},
        {BID_FIELD_NAMES.SECONDS_SINCE_EPOCH: self.seconds_since_utc_epoch(
            datetime.datetime.utcnow() - datetime.timedelta(days=2))}
      ]
    }
    expired_accepted_bid = {
      BID_FIELD_NAMES.BID_STATE: BID_STATES.RECEIVER_ACCEPTED,
      BID_FIELD_NAMES.TIMES_AND_PLACES_LIST: [
        {BID_FIELD_NAMES.SECONDS_SINCE_EPOCH: self.seconds_since_utc_epoch(
            datetime.datetime.utcnow() - datetime.timedelta(days=1))},
        {BID_FIELD_NAMES.SECONDS_SINCE_EPOCH: self.seconds_since_utc_epoch(
            datetime.datetime.utcnow() + datetime.timedelta(days=1))},
      ],
      BID_FIELD_NAMES.ACCEPTED_TIME_AND_PLACE_INDEX: 0
    }
    unexpired_outstanding_bid = {
      BID_FIELD_NAMES.BID_STATE: BID_STATES.OUTSTANDING,
      BID_FIELD_NAMES.TIMES_AND_PLACES_LIST: [
        {BID_FIELD_NAMES.SECONDS_SINCE_EPOCH: self.seconds_since_utc_epoch(
            datetime.datetime.utcnow() - datetime.timedelta(days=1))},
        {BID_FIELD_NAMES.SECONDS_SINCE_EPOCH: self.seconds_since_utc_epoch(
            datetime.datetime.utcnow() + datetime.timedelta(days=1))},
      ]
    }
    unexpired_accepted_bid = {
      BID_FIELD_NAMES.BID_STATE: BID_STATES.OUTSTANDING,
      BID_FIELD_NAMES.TIMES_AND_PLACES_LIST: [
        {BID_FIELD_NAMES.SECONDS_SINCE_EPOCH: self.seconds_since_utc_epoch(
            datetime.datetime.utcnow() - datetime.timedelta(days=1))},
        {BID_FIELD_NAMES.SECONDS_SINCE_EPOCH: self.seconds_since_utc_epoch(
            datetime.datetime.utcnow() + datetime.timedelta(days=1))},
      ],
      BID_FIELD_NAMES.ACCEPTED_TIME_AND_PLACE_INDEX: 1
    }
    self.assertEqual(bid_expired(expired_outstanding_bid), True)
    self.assertEqual(bid_expired(expired_accepted_bid), True)
    self.assertEqual(bid_expired(unexpired_outstanding_bid), False)
    self.assertEqual(bid_expired(unexpired_accepted_bid), False)

if __name__ == '__main__':
  unittest.main()
