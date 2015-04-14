from flask import request, session, jsonify, Response, current_app
from bson.objectid import ObjectId

from server.constants import *
from server.utils import (error_response, crossdomain, JSONEncoder, get_db,
    make_json_response, get_bids_involved_with, was_receiver, get_bid_state,
    times_already_passed, get_bid_selected_date_time, time_and_place_to_datetime,
    get_most_recent_bid, bid_expired, set_raw_bid_fields, update_bid, get_enum_values) 
from server import app
import datetime

def _leave_review(most_recent_bid, request_dict, fields_enum, review_key):
    allowed_keys = get_enum_values(fields_enum) + [BID_FIELD_NAMES.RECEIVER_ID]
    if len(request_dict.keys()) > len(allowed_keys):
        return error_response('too_many_fields')

    fields_to_set = {key: None for key in get_enum_values(fields_enum)}
    for field_key, v in fields_to_set.iteritems():
        if request_dict.get(field_key) is None:
            return error_response('missing_field')
        fields_to_set[field_key] = request_dict[field_key]

    update_bid(most_recent_bid, {review_key: fields_to_set})
    return make_json_response({'success': True})


@app.route('/leave_review/<sender_id>/', methods=['GET', 'POST', 'DELETE', 'OPTIONS'])
@crossdomain()
def leave_review(sender_id):
    # TODO(daddy): Test session authentication.
    if session.get('user_id', None) != sender_id:
        current_app.logger.debug('Session token expired; aborting!')
        return error_response('user_bid_access')

    if sender_id is None:
        current_app.logger.debug('Bidder id was None.')
        return error_response('bad_sender_id')

    if request.method == 'POST':
        current_app.logger.debug('Received bid!')
        request_dict = request.get_json()
        receiver_id = request_dict[BID_FIELD_NAMES.RECEIVER_ID]

        most_recent_bid = get_most_recent_bid(sender_id, receiver_id, exclude_pins=True)
        is_reviewable_date = (
            most_recent_bid is not None and
            most_recent_bid['bid_state'] == BID_STATES.SENDER_CONFIRMED and
            bid_expired(most_recent_bid)
        )
        if not is_reviewable_date:
            return error_response('invalid_review')

        was_sender = True

        if most_recent_bid[BID_FIELD_NAMES.SENDER_ID] == ObjectId(receiver_id):
            was_sender = False

        if was_sender:
            return _leave_review(most_recent_bid, request_dict, SENDER_REVIEW_FIELDS,
                BID_FIELD_NAMES.SENDER_REVIEW)
        else:
            return _leave_review(most_recent_bid, request_dict, RECEIVER_REVIEW_FIELDS,
                BID_FIELD_NAMES.RECEIVER_REVIEW)




