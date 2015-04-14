"""
This file encapsulates the bidding logic. Broadly speaking, there are three actions
a user can perform. They can:
  - PLACE a bid
  - ACCEPT a bid
  - CANCEL a bid

With every action there is a SENDER (the person initiating the action) and a RECEIVER
(the person the sender is acting on).

With bid placement, the SENDER places a bit ON the RECEIVER.
With bid acceptance, the SENDER accepts a bid placed ON him/her.
With bid cancellation, the SENDER cancels a bid placed ON him/her.

In that sense, someone who SENT a bid, can RECEIVE an acceptance. Similarly, someone who
SEND a bid can RECEIVE a cancellation. 

The rest of the details just boild down to a big state machine that I'm not going
to document here because it's pretty well documented by the code itself. The stuff you
want to start looking at is the endpoints at the BOTTOM of this file. Everything
else is just helper logic, basically.
"""

from flask import request, session, jsonify, Response, current_app
from bson.objectid import ObjectId

from server.constants import *
from server.utils import (error_response, crossdomain, JSONEncoder, get_db,
    make_json_response, get_bids_involved_with, was_receiver, get_bid_state,
    times_already_passed, get_bid_selected_date_time, time_and_place_to_datetime,
    get_most_recent_bid, bid_expired, set_raw_bid_fields, update_bid, needs_to_review,
    get_bid_fields, validate_bid_inputs) 
from server import app
import datetime


####################################################################################
# Helpers
####################################################################################

def _form_bids_involved_with(sender_id):    
    bids = get_bids_involved_with(sender_id)

    encoded_json = JSONEncoder().encode(list(bids))
    current_app.logger.debug('Got bids: \n' + encoded_json)

    return Response(response=encoded_json,
                    status=200,
                    mimetype="application/json")

def _get_bid_fields_to_set(request_dict, sender_id):
    fieldsToSet = {}
    for k, v in request_dict.items():
        if (k == BID_FIELD_NAMES.SENDER_ID or
            k == BID_FIELD_NAMES.RECEIVER_ID):
            fieldsToSet[k] = ObjectId(v)
            continue
        if (k == BID_FIELD_NAMES.BID_AMOUNT):
            fieldsToSet[k] = int(v)
            continue
        fieldsToSet[k] = v
    fieldsToSet[BID_FIELD_NAMES.BID_STATE] = BID_STATES.OUTSTANDING
    fieldsToSet[BID_FIELD_NAMES.SENDER_ID] = ObjectId(sender_id)
    set_raw_bid_fields(fieldsToSet)
    return fieldsToSet

def _form_new_bid(most_recent_bid, fieldsToSet, sender_id, receiver_id):
    get_db().bids.insert(fieldsToSet)
    return make_json_response({'success': True})

def _reviewed_if_necessary(bid_obj):
    if bid_obj[BID_FIELD_NAMES.BID_STATE] != BID_STATES.SENDER_CONFIRMED:
        return True
    if (bid_obj.get(BID_FIELD_NAMES.SENDER_REVIEW) is None or
        bid_obj.get(BID_FIELD_NAMES.RECEIVER_REVIEW) is None
    ):
        return False
    return True

def _bid_if_no_pending_date(most_recent_bid, fieldsToSet, sender_id, receiver_id):
    if bid_expired(most_recent_bid):
        if needs_to_review(most_recent_bid, sender_id):
            return error_response('you_need_to_review')
        elif needs_to_review(most_recent_bid, receiver_id):
            return error_response('waiting_on_review')
        else:
            return _form_new_bid(most_recent_bid, fieldsToSet, sender_id, receiver_id)
    else:
        return error_response('pending_date')

def _modify_bid_state(bid_obj, bid_state):
    get_db().bids.update(
        {'_id': bid_obj['_id']},
        {'$set': {BID_FIELD_NAMES.BID_STATE: bid_state},
         '$push': {BID_FIELD_NAMES.TIMESTAMP_LIST: [bid_state, 
                   datetime.datetime.utcnow()]}
        }
    )

def _modify_bid_state_and_selected_time(bid_obj, bid_state, time_and_place):
    get_db().bids.update(
        {'_id': bid_obj['_id']},
        {'$set': 
            {BID_FIELD_NAMES.BID_STATE: bid_state,
             BID_FIELD_NAMES.ACCEPTED_TIME_AND_PLACE_INDEX: time_and_place},
         '$push': {BID_FIELD_NAMES.TIMESTAMP_LIST: [bid_state,
                   datetime.datetime.utcnow()]}
        }
    )

def _check_if_bid_paid(bid_obj):
    return bid_obj.get(BID_FIELD_NAMES.CARD_ID, None) is not None

####################################################################################
# PLACE bid
####################################################################################

def _form_receiver_bid_response(most_recent_bid, fieldsToSet, sender_id, receiver_id):
    bid_state = get_bid_state(most_recent_bid)
    if bid_state == BID_STATES.SENDER_LIKED:
        return _form_new_bid(most_recent_bid, fieldsToSet, sender_id, receiver_id)
    if bid_state == BID_STATES.OUTSTANDING:
        return error_response('outstanding_offer')
    elif bid_state == BID_STATES.RECEIVER_REJECTED:
        # They've rejected in the past but it looks like they've changed their minds.
        # Insert an outstanding bid for them.
        return _form_new_bid(most_recent_bid, fieldsToSet, sender_id, receiver_id)
    elif bid_state == BID_STATES.RECEIVER_ACCEPTED:
        return error_response('cant_bid_after_accepted')
    elif bid_state == BID_STATES.SENDER_CONFIRMED:
        return _bid_if_no_pending_date(most_recent_bid, fieldsToSet,
                                       sender_id, receiver_id)
    else:
        return error_response('weird_bid_state')

def _form_sender_bid_response(most_recent_bid, fieldsToSet, sender_id, receiver_id):
    bid_state = get_bid_state(most_recent_bid)
    if bid_state == BID_STATES.SENDER_LIKED:
        # Set bid state to outstanding and add the date+time info.
        update_bid(most_recent_bid, fieldsToSet)
        _modify_bid_state(most_recent_bid, BID_STATES.OUTSTANDING)
        return make_json_response({'success': True})
    if bid_state == BID_STATES.OUTSTANDING:
        # Just update the current bid.
        update_bid(most_recent_bid, fieldsToSet)
        return make_json_response({'success': True})
    elif bid_state == BID_STATES.RECEIVER_REJECTED:
        return error_response('cannot_bid_after_rejection')
    elif bid_state == BID_STATES.RECEIVER_ACCEPTED:
        return error_response('cannot_bid_receiver_accepted')
    elif bid_state == BID_STATES.SENDER_CONFIRMED:
        return _bid_if_no_pending_date(most_recent_bid, fieldsToSet,
                                       sender_id, receiver_id)
    else:
        return error_response('weird_bid_state')


####################################################################################
# ACCEPT bid
####################################################################################

def _form_receiver_accept_response(most_recent_bid, sender_id, receiver_id,
                                   accepted_time_and_place_index):
    bid_state = get_bid_state(most_recent_bid)
    if bid_state in (BID_STATES.RECEIVER_REJECTED,
        BID_STATES.RECEIVER_ACCEPTED, BID_STATES.SENDER_CONFIRMED, BID_STATES.SENDER_LIKED
    ):
        return error_response('nothing_to_accept')

    times_and_places_list = most_recent_bid[BID_FIELD_NAMES.TIMES_AND_PLACES_LIST]
    if (accepted_time_and_place_index is None or
        accepted_time_and_place_index > 
        len(times_and_places_list)
    ):
        return error_response('invalid_index')
    bid_date_time = time_and_place_to_datetime(
        times_and_places_list[accepted_time_and_place_index])
    if bid_date_time is None:
        return error_response('weird_bid_with_invalid_date')
    elif bid_date_time < datetime.datetime.utcnow():
        return error_response('date_passed')

    if bid_state == BID_STATES.OUTSTANDING:
        _modify_bid_state_and_selected_time(most_recent_bid, BID_STATES.RECEIVER_ACCEPTED,
            accepted_time_and_place_index)

        return make_json_response({'success': True})
    else:
        current_app.logger.error('Unusual bid state encountered: ' + str(bid_state))
        return error_response('weird_bid_state')

def _form_sender_accept_response(most_recent_bid, sender_id, receiver_id):
    bid_state = get_bid_state(most_recent_bid)
    if bid_state in (BID_STATES.OUTSTANDING, BID_STATES.RECEIVER_REJECTED,
        BID_STATES.SENDER_CONFIRMED, BID_STATES.SENDER_LIKED
    ):
        return error_response('nothing_to_accept')

    bid_paid = _check_if_bid_paid(most_recent_bid)
    if not bid_paid:
        return error_response('unpaid_bid_confirmation')

    if bid_state == BID_STATES.RECEIVER_ACCEPTED:
        bid_date_time = get_bid_selected_date_time(most_recent_bid)
        if bid_date_time is None:
            return error_response('weird_accept_with_no_date')
        elif bid_date_time < datetime.datetime.utcnow():
            return error_response('date_passed')

        _modify_bid_state(most_recent_bid, BID_STATES.SENDER_CONFIRMED)
        return make_json_response({'success': True})


####################################################################################
# CANCEL bid
####################################################################################

def _form_receiver_cancel_response(most_recent_bid, receiver_id, sender_id):
    bid_state = get_bid_state(most_recent_bid)
    if bid_state == BID_STATES.SENDER_LIKED:
        return error_response('nothing_to_cancel')
    elif bid_state == BID_STATES.OUTSTANDING:
        _modify_bid_state(most_recent_bid, BID_STATES.RECEIVER_REJECTED)
        return make_json_response({'success': True})
    elif bid_state == BID_STATES.RECEIVER_REJECTED:
        return error_response('cannot_reject_twice')
    elif bid_state == BID_STATES.RECEIVER_ACCEPTED:
        # A receiver can change her mind anytime before the offer is confirmed. After
        # the offer is confirmed, however, it's game over.
        _modify_bid_state(most_recent_bid, BID_STATES.RECEIVER_REJECTED)
        return make_json_response({'success': True})
    elif bid_state == BID_STATES.SENDER_CONFIRMED:
        _modify_bid_state(most_recent_bid, BID_STATES.RECEIVER_CANCELLED_AFTER_CONFIRMED)
        return make_json_response({'success': True})
    else:
        current_app.logger.error('Unusual bid state encountered: ' + str(bid_state))
        return error_response('weird_bid_state')

def _form_sender_cancel_response(most_recent_bid, receiver_id, sender_id):
    bid_state = get_bid_state(most_recent_bid)
    if bid_state == BID_STATES.SENDER_LIKED:
        _modify_bid_state(most_recent_bid, BID_STATES.SENDER_UNLIKED)
        return make_json_response({'success': True})
    elif bid_state == BID_STATES.OUTSTANDING:
        _modify_bid_state(most_recent_bid, BID_STATES.SENDER_CANCELLED_BEFORE_ACCEPTED)
        return make_json_response({'success': True})
    elif bid_state == BID_STATES.RECEIVER_REJECTED:
        return error_response('cannot_cancel_rejected_offer')
    elif bid_state == BID_STATES.RECEIVER_ACCEPTED:
        _modify_bid_state(most_recent_bid, BID_STATES.SENDER_CANCELLED_AFTER_ACCEPTED)
        return make_json_response({'success': True})
    elif bid_state == BID_STATES.SENDER_CONFIRMED:
        _modify_bid_state(most_recent_bid, BID_STATES.SENDER_CANCELLED_AFTER_CONFIRMED)
        return make_json_response({'success': True})
    else:
        current_app.logger.error('Unusual bid state encountered: ' + str(bid_state))
        return error_response('weird_bid_state')


####################################################################################
# Endpoints:
#   - PLACE bid
#   - ACCEPT bid
#   - CANCEL bid
####################################################################################

@app.route('/bids/<sender_id>/', methods=['GET', 'POST', 'DELETE', 'OPTIONS'])
@crossdomain()
def bid_on_user(sender_id):
    # TODO(daddy): Test session authentication.
    if session.get('user_id', None) != sender_id:
        current_app.logger.debug('Session token expired; aborting!')
        return error_response('user_bid_access')

    if sender_id is None:
        current_app.logger.debug('Bidder id was None.')
        return error_response('bad_sender_id')

    if request.method == 'GET':
        current_app.logger.debug('Getting bids for user ' + sender_id)
        return _form_bids_involved_with(sender_id)

    # TODO(daddy): first make sure that sender_id doesn't have more than
    # 5 outstanding bids..
    if request.method == 'POST':
        current_app.logger.debug('Received bid!')
        request_dict = request.get_json()
    
        (times_and_places_list, bid_amount, receiver_id) = get_bid_fields(request_dict)

        possible_resp = validate_bid_inputs(times_and_places_list, bid_amount,
                                             sender_id, receiver_id)
        if possible_resp is not None:
            return possible_resp

        fieldsToSet = _get_bid_fields_to_set(request_dict, sender_id)

        most_recent_bid = get_most_recent_bid(sender_id, receiver_id)

        if (most_recent_bid is None or
            (bid_expired(most_recent_bid) and _reviewed_if_necessary(most_recent_bid))
        ):
            return _form_new_bid(
                most_recent_bid, fieldsToSet, sender_id, receiver_id)
        elif was_receiver(most_recent_bid, sender_id):
            return _form_receiver_bid_response(
                most_recent_bid, fieldsToSet, sender_id, receiver_id)
        else:
            return _form_sender_bid_response(
                most_recent_bid, fieldsToSet, sender_id, receiver_id)

@app.route('/bids/accept/<sender_id>/', methods=['POST', 'OPTIONS'])
@crossdomain()
def accept_bid(sender_id):
    if session.get('user_id', None) != sender_id:
        current_app.logger.debug('Session token expired; aborting!')
        return error_response('user_bid_access')

    if sender_id is None:
        current_app.logger.debug('Bidder id was None.')
        return error_response('bad_sender_id')

    if request.method == 'POST':
        current_app.logger.debug('Accepting bid.')
        request_dict = request.get_json()

        receiver_id = request_dict.get(BID_FIELD_NAMES.RECEIVER_ID, None)

        if (sender_id is None or receiver_id is None):
            return error_response('bad_accept_request')

        most_recent_bid = get_most_recent_bid(receiver_id, sender_id)

        if most_recent_bid is None:
            return error_response('nothing_to_accept')
        elif bid_expired(most_recent_bid):
            return error_response('date_passed')
        elif (was_receiver(most_recent_bid, sender_id)):
            accepted_time_and_place_index = (
                request_dict.get(BID_FIELD_NAMES.ACCEPTED_TIME_AND_PLACE_INDEX, None))
            return _form_receiver_accept_response(most_recent_bid, sender_id, receiver_id,
                                                  accepted_time_and_place_index)
        else:
            return _form_sender_accept_response(most_recent_bid, sender_id, receiver_id)

@app.route('/bids/cancel/<sender_id>/', methods=['POST', 'OPTIONS'])
@crossdomain()
def cancel_bid(sender_id):
    if session.get('user_id', None) != sender_id:
        current_app.logger.debug('Session token expired; aborting!')
        return error_response('user_bid_access')

    if sender_id is None:
        current_app.logger.debug('Bidder id was None.')
        return error_response('bad_sender_id')

    if request.method == 'POST':
        current_app.logger.debug('Canceling bid.')
        request_dict = request.get_json()

        receiver_id = request_dict.get(BID_FIELD_NAMES.RECEIVER_ID, None)

        if sender_id is None or receiver_id is None:
            return error_response('bad_receiver_id')

        most_recent_bid = get_most_recent_bid(receiver_id, sender_id)

        if most_recent_bid is None:
            return error_response('nothing_to_cancel')
        elif bid_expired(most_recent_bid):
            return error_response('date_passed')
        elif (was_receiver(most_recent_bid, sender_id)):
            return _form_receiver_cancel_response(most_recent_bid, sender_id, receiver_id)
        else:
            return _form_sender_cancel_response(most_recent_bid, sender_id, receiver_id)