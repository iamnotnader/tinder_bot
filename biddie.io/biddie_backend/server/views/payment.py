"""
Accept a payment on the frontend to be processed.
"""

from flask import request, session, jsonify, Response
from bson.objectid import ObjectId

from server.constants import *
from server.utils import (error_response, crossdomain, JSONEncoder, get_db,
    make_json_response, get_bids_involved_with, was_receiver, get_bid_state,
    times_already_passed, get_bid_selected_date_time, time_and_place_to_datetime,
    get_most_recent_bid, get_bid_state, bid_expired, validate_session)
from server import app
import datetime
import stripe
from server.views.bids import accept_bid

# Set your secret key: remember to change this to your live secret key in production
# See your keys here https://dashboard.stripe.com/account
# TODO(daddy): Get a real API key.
stripe.api_key = "sk_test_BQokikJOvBiI2HlWgH4olfQ2"

def _get_bid_fields(request_dict):
    receiver_id = request_dict.get(BID_FIELD_NAMES.RECEIVER_ID, None)
    payment_token = request_dict.get('payment_token', None)
    return (receiver_id, payment_token)

def _validate_payment_inputs(user_found, receiver_id, payment_token):
    if (receiver_id is None or payment_token is None or
        user_found is None):
        return error_response('bad_payment_data')
    return None

def _validate_most_recent_bid(bid_obj):
    if (bid_obj is None):
        return error_response('bid_obj_none')
    elif get_bid_state(bid_obj) != BID_STATES.RECEIVER_ACCEPTED:
        return error_response('cannot_pay_for_unaccepted_bid')
    elif bid_expired(bid_obj):
        return error_response('cannot_pay_for_expired_date')
    elif bid_obj.get(BID_FIELD_NAMES.BID_AMOUNT, None) is None:
        return error_response['most_recent_bid_has_no_amount']
    return None

def _update_user_customer_id(user_obj, customer_id):
    get_db().users.update(
        { '_id': ObjectId(user_obj['_id']) },
        { '$set': {USER_FIELD_NAMES.CUSTOMER_ID: customer_id} }
    )
    user_obj[USER_FIELD_NAMES.CUSTOMER_ID] = customer_id

def _add_card_id_to_bid(bid_obj, card_obj):
    get_db().bids.update(
        { '_id': ObjectId(bid_obj['_id']) },
        { '$set': {BID_FIELD_NAMES.CARD_ID: card_obj['id']} }
    )
    bid_obj[BID_FIELD_NAMES.CARD_ID] = card_obj['id']

def _get_or_create_card(customer_obj, payment_token):
    new_card_fingerprint = (
        stripe.Token.retrieve(payment_token['id'])['card']['fingerprint'])
    for card in customer_obj.sources.data:
        if card['fingerprint'] == new_card_fingerprint:
            return card
    return customer_obj.sources.create(card=payment_token['id'])

def _add_credit_card_for_user_if_necessary(
    user_obj, bid_obj, bid_amount_cents, payment_token):
    # Do the stripey things.
    # Create or get the customer we're going to attach the card to.
    customer_id = user_obj.get(USER_FIELD_NAMES.CUSTOMER_ID, None)
    if customer_id is None:
        customer_obj = stripe.Customer.create(
            email=payment_token.get('email', 'no email')
        )
        if customer_obj is None:
            # TODO(daddy): Throw the right kind of exception here.
            raise Exception('Customer object should not be None')
        customer_id = customer_obj.id
        _update_user_customer_id(user_obj, customer_id)
    else:
        customer_obj = stripe.Customer.retrieve(customer_id)
    
    # At this point we have a hardcore customer_id so create the card.
    new_card = _get_or_create_card(customer_obj, payment_token)
    _add_card_id_to_bid(bid_obj, new_card)

@app.route('/pay_and_confirm/<sender_id>/', methods=['POST', 'DELETE', 'OPTIONS'])
@crossdomain()
def handle_pay_and_confirm(sender_id):
    possible_resp = validate_session(session, sender_id)
    if possible_resp is not None:
        return possible_resp

    if request.method == 'POST':
        request_dict = request.get_json()

        (receiver_id, payment_token) = _get_bid_fields(request_dict)
        user_found = get_db().users.find_one({'_id': ObjectId(sender_id)})

        # Validate the inputs.
        possible_resp = _validate_payment_inputs(user_found, receiver_id,
                                                 payment_token)
        if possible_resp is not None:
            return possible_resp

        # Validate that there is a confirmation to pay for.
        most_recent_bid = get_most_recent_bid(sender_id, receiver_id)
        possible_resp = _validate_most_recent_bid(most_recent_bid)
        if possible_resp is not None:
            return possible_resp

        bid_amount_cents = most_recent_bid[BID_FIELD_NAMES.BID_AMOUNT]*100
        _add_credit_card_for_user_if_necessary(
            user_found, most_recent_bid, bid_amount_cents, payment_token)

        return accept_bid(sender_id)

        





        
