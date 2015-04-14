from flask import request, session, jsonify, Response, current_app
from bson.objectid import ObjectId

from server.constants import *
from server.utils import (error_response, crossdomain, get_db,
    make_json_response, get_bid_fields, update_poke, validate_bid_inputs)
from server import app
import datetime


# TODO(daddy): refactor this into get_most_recent_bid in utils.py
def _get_most_recent_poke(sender_id, receiver_id):
    uncancelled_pokes = get_db().pokes.find(
        {'$and': [
            {BID_FIELD_NAMES.SENDER_ID: ObjectId(sender_id),
             BID_FIELD_NAMES.RECEIVER_ID: ObjectId(receiver_id)
            },
            {BID_FIELD_NAMES.BID_STATE: 
                {'$nin': POKE_CANCEL_STATES}
            }
        ]}
    )
    # Sort the uncancelled pokes by creation time (most recent first).
    recent_pokes = list(uncancelled_pokes.sort([
        (BID_FIELD_NAMES.TIME_BID_CREATED_AT, -1)
    ]))

    if len(recent_pokes) > 0:
        return recent_pokes[0]
    else:
        return None

def _create_new_poke(sender_id, receiver_id):
    get_db().pokes.insert(
        {BID_FIELD_NAMES.SENDER_ID: ObjectId(sender_id),
         BID_FIELD_NAMES.RECEIVER_ID: ObjectId(receiver_id),
         BID_FIELD_NAMES.BID_STATE: POKE_STATES.POKE_OUTSTANDING}
    )

def _modify_poke_state(poke_obj, new_state):
    get_db().pokes.update(
        {'_id': poke_obj['_id']},
        {'$set': {BID_FIELD_NAMES.BID_STATE: new_state},
         '$push': {BID_FIELD_NAMES.TIMESTAMP_LIST: [new_state, 
                   datetime.datetime.utcnow()]}
        }
    )

# Expects:
# - receiver_id
@app.route('/pokes/create/<sender_id>/', methods=['GET', 'POST', 'DELETE', 'OPTIONS'])
@crossdomain()
def create_poke(sender_id):
    if session.get('user_id', None) != sender_id:
        current_app.logger.debug('Session token expired; aborting!')
        return error_response('user_bid_access')

    if sender_id is None:
        current_app.logger.debug('Sender id was None.')
        return error_response('bad_sender_id')

    if request.method == 'POST':
        current_app.logger.debug('Received poke!')
        request_dict = request.get_json()
        receiver_id = request_dict[BID_FIELD_NAMES.RECEIVER_ID]

        most_recent_poke = _get_most_recent_poke(sender_id, receiver_id)

        if most_recent_poke is None:
            _create_new_poke(sender_id, receiver_id)
            return make_json_response({'success': True})
        else:
            return error_response('already_poked')


# Expects:
# - poke_sender_id
# - poke_receiver_id
@app.route('/pokes/cancel/<sender_id>/', methods=['GET', 'POST', 'DELETE', 'OPTIONS'])
@crossdomain()
def cancel_poke(sender_id):
    if session.get('user_id', None) != sender_id:
        current_app.logger.debug('Session token expired; aborting!')
        return error_response('user_bid_access')

    if sender_id is None:
        current_app.logger.debug('Sender id was None.')
        return error_response('bad_sender_id')

    if request.method == 'POST':
        current_app.logger.debug('Received poke!')
        request_dict = request.get_json()
        poke_receiver_id = request_dict[BID_FIELD_NAMES.RECEIVER_ID]
        poke_sender_id = request_dict[BID_FIELD_NAMES.SENDER_ID]

        canceller_was_poker = False
        if poke_sender_id != sender_id and poke_receiver_id != sender_id:
            return error_response('unaffiliated_poke_cancellation')
        elif poke_sender_id == sender_id:
            canceller_was_poker = True

        most_recent_poke = _get_most_recent_poke(poke_sender_id, poke_receiver_id)

        if most_recent_poke is None:
            return error_response('no_poke_to_cancel')
        else:
            if canceller_was_poker:
                _modify_poke_state(most_recent_poke, POKE_STATES.POKE_CANCELLED_BY_POKER)
                return make_json_response({'success': True})
            else:
                _modify_poke_state(most_recent_poke, POKE_STATES.POKE_REJECTED_BY_OTHER)
                return make_json_response({'success': True})

# Expects:
# - poke_receiver_id
#
# TODO(daddy): Write a test for this endpoint.
@app.route('/pokes/add_proposal/<sender_id>/', methods=['GET', 'POST', 'DELETE', 'OPTIONS'])
@crossdomain()
def propose_bid(sender_id):
    if session.get('user_id', None) != sender_id:
        current_app.logger.debug('Session token expired; aborting!')
        return error_response('user_bid_access')

    if sender_id is None:
        current_app.logger.debug('Sender id was None.')
        return error_response('bad_sender_id')

    if request.method == 'POST':
        current_app.logger.debug('Received poke!')
        request_dict = request.get_json()

        (times_and_places_list, bid_amount, receiver_id) = get_bid_fields(request_dict)

        possible_resp = validate_bid_inputs(times_and_places_list, bid_amount,
                                             sender_id, receiver_id) 
        if possible_resp is not None:
            return possible_resp

        most_recent_poke = _get_most_recent_poke(sender_id, receiver_id)
        if most_recent_poke is None:
            # Create the poke with an offer attached.
            _create_new_poke(sender_id, receiver_id)
            most_recent_poke = _get_most_recent_poke(sender_id, receiver_id)
            update_poke(most_recent_poke, {
                BID_FIELD_NAMES.POKE_PROPOSAL: {
                    BID_FIELD_NAMES.TIMES_AND_PLACES_LIST: times_and_places_list,
                    BID_FIELD_NAMES.BID_AMOUNT: bid_amount,
                }
            })
        else:
            update_poke(most_recent_poke, {
                BID_FIELD_NAMES.POKE_PROPOSAL: {
                    BID_FIELD_NAMES.TIMES_AND_PLACES_LIST: times_and_places_list,
                    BID_FIELD_NAMES.BID_AMOUNT: bid_amount,
                }
            })
        return make_json_response({'success': True})
