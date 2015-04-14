from flask import request, session, jsonify, Response, current_app
from bson.objectid import ObjectId

from server.constants import *
from server.utils import (error_response, crossdomain, JSONEncoder, get_db,
    make_json_response, get_bids_involved_with, was_receiver, get_bid_state,
    times_already_passed, get_bid_selected_date_time, time_and_place_to_datetime,
    get_most_recent_bid, bid_expired, get_user_likes, get_most_recent_bid,
    set_raw_bid_fields) 
from server import app
import datetime

@app.route('/like/<sender_id>/', methods=['GET', 'POST', 'DELETE', 'OPTIONS'])
@crossdomain()
def like_user(sender_id):
    # TODO(daddy): Test session authentication.
    if session.get('user_id', None) != sender_id:
        current_app.logger.debug('Session token expired; aborting!')
        return error_response('user_bid_access')

    if sender_id is None:
        current_app.logger.debug('Bidder id was None.')
        return error_response('bad_sender_id')

    if request.method == 'GET':
        user_likes = get_user_likes(sender_id)
        encoded_json = JSONEncoder().encode(user_likes)
        return Response(response=encoded_json,
                        status=200,
                        mimetype="application/json")

    if request.method == 'POST':
        # Add a like from sender to receiver
        current_app.logger.debug('Like posted from ' + sender_id)
        request_dict = request.get_json()
        
        receiver_id = request_dict.get(BID_FIELD_NAMES.RECEIVER_ID, None)
        if receiver_id is None:
          return error_response['no_user_to_like']
        elif sender_id == receiver_id:
            current_app.logger.debug('receiver id was same as sender id on like.')
            return error_response('like_yourself')

        most_recent_bid = get_most_recent_bid(sender_id, receiver_id)
        fields_to_insert = {
            BID_FIELD_NAMES.SENDER_ID: ObjectId(sender_id),
            BID_FIELD_NAMES.RECEIVER_ID: ObjectId(receiver_id),
            BID_FIELD_NAMES.BID_STATE: BID_STATES.SENDER_LIKED
        }
        set_raw_bid_fields(fields_to_insert)
        if (most_recent_bid is None or bid_expired(most_recent_bid) or
            (get_bid_state(most_recent_bid) == BID_STATES.SENDER_LIKED
             and most_recent_bid[BID_FIELD_NAMES.SENDER_ID] != ObjectId(sender_id))
        ):
            get_db().bids.insert(fields_to_insert)
        elif (get_bid_state(most_recent_bid) == BID_STATES.SENDER_LIKED):
            return error_response('already_liked')
        elif get_bid_state(most_recent_bid) != BID_STATES.SENDER_LIKED:
            return error_response('cant_like_bid_on_user')

        current_app.logger.debug('Got likes.')
        encoded_json = JSONEncoder().encode({'success': True})
        return Response(response=encoded_json,
                        status=200,
                        mimetype="application/json")

@app.route('/num_likes/<sender_id>/', methods=['GET', 'OPTIONS'])
@crossdomain()
def num_likes(sender_id):
    # TODO(daddy): Test session authentication.
    if session.get('user_id', None) != sender_id:
        current_app.logger.debug('Session token expired; aborting!')
        return error_response('user_bid_access')

    if sender_id is None:
        current_app.logger.debug('Bidder id was None.')
        return error_response('bad_sender_id')

    if request.method == 'GET':
        # Get all the likes for the sender.
        current_app.logger.debug('Getting number of likes for user ' + sender_id)
        # TODO(daddy): Have an intern make this efficient.
        other_likes = get_db().bids.find({BID_FIELD_NAMES.RECEIVER_ID: ObjectId(sender_id),
            BID_FIELD_NAMES.BID_STATE: BID_STATES.SENDER_LIKED})

        encoded_json = JSONEncoder().encode({'count': len(list(other_likes))})
        return Response(response=encoded_json,
                        status=200,
                        mimetype="application/json")