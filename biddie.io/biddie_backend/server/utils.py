from server.constants import ERROR_MESSAGES, ALLOWED_HEADERS, ALLOWED_ORIGINS
from flask import jsonify, Response
from datetime import timedelta
from flask import make_response, request, current_app
from functools import update_wrapper
from bson.objectid import ObjectId
from constants import *
import json
import datetime


def crossdomain(origin=ALLOWED_ORIGINS, methods=None, headers=ALLOWED_HEADERS,
                max_age=21600, attach_to_all=True,
                automatic_options=True):
    if methods is not None:
        methods = ', '.join(sorted(x.upper() for x in methods))
    if headers is not None and not isinstance(headers, basestring):
        headers = ', '.join(x.upper() for x in headers)
    if not isinstance(origin, basestring):
        origin = ', '.join(origin)
    if isinstance(max_age, timedelta):
        max_age = max_age.total_seconds()

    def get_methods():
        if methods is not None:
            return methods

        options_resp = current_app.make_default_options_response()
        return options_resp.headers['allow']

    def decorator(f):
        def wrapped_function(*args, **kwargs):
            if automatic_options and request.method == 'OPTIONS':
                resp = current_app.make_default_options_response()
            else:
                resp = make_response(f(*args, **kwargs))
            if not attach_to_all and request.method != 'OPTIONS':
                return resp

            h = resp.headers

            originFromHeader = request.headers.get('Origin', None)
            if originFromHeader is not None and originFromHeader in origin:
                h['Access-Control-Allow-Origin'] = request.headers['Origin']
            else:
                h['Access-Control-Allow-Origin'] = None
            h['Access-Control-Allow-Methods'] = get_methods()
            h['Access-Control-Max-Age'] = str(max_age)
            h['Access-Control-Allow-Credentials'] = 'true'
            if headers is not None:
                h['Access-Control-Allow-Headers'] = headers
            return resp

        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)
    return decorator


class JSONEncoder(json.JSONEncoder):
    def __init__(self, indent=4):
        super(self.__class__, self).__init__(indent=indent)
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        if isinstance(o, datetime.datetime):
            return str(o)
        return json.JSONEncoder.default(self, o)


def get_long_lat_for_zip(input_zip):
    zipcode = ZCDB[int(input_zip)]
    return [zipcode.longitude, zipcode.latitude]


def error_response(message_key):
  """
  Return an error message.
  """
  data = {
      'success': False,
      'message': ERROR_MESSAGES[message_key],
      'message_key': message_key,
      'id': None,
  }
  return jsonify(data)

def get_db():
    # We have to get the db dynamically so we can inject different ones
    # when running tests.
    return current_app.config['DATABASE'].db

def make_json_response(payload):
    return Response(response=JSONEncoder().encode(payload),
                    status=200,
                    mimetype="application/json")

def get_my_pokes(user_id):
    poke_objs = get_db().pokes.find(
        {'$and': [
            {'$or': [
                {BID_FIELD_NAMES.SENDER_ID: ObjectId(user_id)},
                {BID_FIELD_NAMES.RECEIVER_ID: ObjectId(user_id)}
            ]},
            {BID_FIELD_NAMES.BID_STATE: 
                {'$nin': POKE_CANCEL_STATES}
            }
        ]}
    )
    return poke_objs

def get_bids_involved_with(user_id):
    # TODO(daddy): Get rid of all the likes logic; it's useless.
    states_to_exclude = CANCELLED_BID_STATES + [BID_STATES.SENDER_LIKED]
    bid_objs = get_db().bids.find(
        {'$and': [
            {'$or': [
                {BID_FIELD_NAMES.SENDER_ID: ObjectId(user_id)},
                {BID_FIELD_NAMES.RECEIVER_ID: ObjectId(user_id)}
            ]},
            {BID_FIELD_NAMES.BID_STATE: 
                {'$nin': CANCELLED_BID_STATES}
            }
        ]}
    )

    ret_list = []
    for bid_obj in list(bid_objs):
        # Include expired bids ONLY if they're confirmed (ie past dates)
        if not bid_expired(bid_obj):
            ret_list.append(bid_obj)
        elif bid_obj[BID_FIELD_NAMES.BID_STATE] == BID_STATES.SENDER_CONFIRMED:
            if (bid_obj.get(BID_FIELD_NAMES.SENDER_REVIEW, False) or
                bid_obj.get(BID_FIELD_NAMES.RECEIVER_REVIEW, False)
            ):
                continue
            ret_list.append(bid_obj)
        else:
            continue

    # Check to make sure that there aren't any duplicate id pairs..
    unique_bids = {}
    for bid_obj in list(ret_list):
        sender_id = str(bid_obj[BID_FIELD_NAMES.SENDER_ID])
        receiver_id = str(bid_obj[BID_FIELD_NAMES.RECEIVER_ID])
        if unique_bids.get(sender_id + receiver_id, False):
            raise Exception('Two bids with the same pair of ids were found: %s %s.' %
                (sender_id, receiver_id))
        unique_bids[sender_id+receiver_id] = True
        unique_bids[receiver_id+sender_id] = True

    return ret_list

def was_receiver(bid_obj, user_id):
    return bid_obj[BID_FIELD_NAMES.RECEIVER_ID] == ObjectId(user_id)

def was_sender(bid_obj, user_id):
    return bid_obj[BID_FIELD_NAMES.SENDER_ID] == ObjectId(user_id)

def get_bid_state(bid_obj):
    return bid_obj[BID_FIELD_NAMES.BID_STATE]

def time_and_place_to_datetime(time_and_place):
    return datetime.datetime.utcfromtimestamp(
        time_and_place[BID_FIELD_NAMES.SECONDS_SINCE_EPOCH])

def times_already_passed(times_and_places_list):
    all_times_passed = True
    for time_and_place in times_and_places_list:
        if time_and_place_to_datetime(time_and_place) > datetime.datetime.utcnow():
            all_times_passed = False
            break
    return all_times_passed

def get_bid_selected_date_time(bid_obj):
    times_and_places_list = bid_obj.get(BID_FIELD_NAMES.TIMES_AND_PLACES_LIST, None)
    accepted_time_and_place_index = int(
        bid_obj.get(BID_FIELD_NAMES.ACCEPTED_TIME_AND_PLACE_INDEX, -1))
    if times_and_places_list is None or accepted_time_and_place_index == -1:
        return None

    s = times_and_places_list[accepted_time_and_place_index]
    return time_and_place_to_datetime(s)

def sort_user_photos(list_of_users):
    for user in list_of_users:
        if user.get('photos', None) is None:
            continue
        user['photos'] = (
            filter(lambda x: x.get('photo_position', None) is not None,
                   user['photos'])
        )
        user['photos'].sort(key=lambda x: x['photo_position'])

def _get_user_by_id(user_id):
    user_found = get_db().users.find_one({'_id': ObjectId(user_id)})
    if user_found is None:
        return None
    user_found['id'] = user_found.pop('_id')
    return user_found

def get_list_of_users_from_db(list_of_user_ids):
    if len(list_of_user_ids) == 0:
        return []
    list_of_users = list(get_db().users.find(
        { '$or': [{'_id': ObjectId(id_val)} for id_val in list_of_user_ids] })
    )
    for user_obj in list_of_users:
        user_obj['id'] = user_obj.pop('_id')
    sort_user_photos(list_of_users)
    return list_of_users

def needs_to_review(bid_obj, your_id):
    if (bid_obj.get(BID_FIELD_NAMES.SENDER_ID) == ObjectId(your_id) and
        bid_obj.get(BID_FIELD_NAMES.SENDER_REVIEW) is None
    ):
        return True
    elif (bid_obj.get(BID_FIELD_NAMES.RECEIVER_ID) == ObjectId(your_id) and
          bid_obj.get(BID_FIELD_NAMES.RECEIVER_REVIEW) is None
    ):
        return True
    else:
        return False

def _append_bid_to_proper_group(bid_obj, user_id, grouped_bids):
    sender_liked = get_bid_state(bid_obj) == BID_STATES.SENDER_LIKED
    bid_outstanding = get_bid_state(bid_obj) == BID_STATES.OUTSTANDING
    sender_confirmed = get_bid_state(bid_obj) == BID_STATES.SENDER_CONFIRMED
    receiver_accepted = get_bid_state(bid_obj) == BID_STATES.RECEIVER_ACCEPTED
    poke_outstanding = get_bid_state(bid_obj) == POKE_STATES.POKE_OUTSTANDING
    date_has_passed = False
    if receiver_accepted or sender_confirmed:
        date_has_passed = get_bid_selected_date_time(bid_obj) < datetime.datetime.utcnow()

    if (was_sender(bid_obj, user_id) and sender_liked):
        grouped_bids[BID_GROUP_KEYS.USER_LIKES].append(bid_obj)
    elif (was_sender(bid_obj, user_id) and bid_outstanding):
        grouped_bids[BID_GROUP_KEYS.YOU_HAVE_BID_ON].append(bid_obj)
    elif (was_receiver(bid_obj, user_id) and bid_outstanding):
        grouped_bids[BID_GROUP_KEYS.HAVE_BID_ON_YOU].append(bid_obj)
    elif (not date_has_passed) and sender_confirmed:
        grouped_bids[BID_GROUP_KEYS.CONFIRMED_UPCOMING_DATES].append(bid_obj)
    elif (not date_has_passed) and receiver_accepted:
        grouped_bids[BID_GROUP_KEYS.UNCONFIRMED_UPCOMING_DATES].append(bid_obj)
    elif date_has_passed and sender_confirmed:
        if needs_to_review(bid_obj, user_id):
            grouped_bids[BID_GROUP_KEYS.PAST_UNREVIEWED_DATES].append(bid_obj)
        else:
            grouped_bids[BID_GROUP_KEYS.PAST_REVIEWED_DATES].append(bid_obj)
    elif poke_outstanding:
        if was_sender(bid_obj, user_id):
            grouped_bids[BID_GROUP_KEYS.YOU_POKED].append(bid_obj)
        else:
            grouped_bids[BID_GROUP_KEYS.POKED_YOU].append(bid_obj)

def _get_user_ids_from_grouped_bids(user_id, grouped_bids):
    user_ids_to_get = []
    user_id = ObjectId(user_id)
    for bid_group_name, bid_group in grouped_bids.iteritems():
        for bid_obj in bid_group:
            sender_id = bid_obj[BID_FIELD_NAMES.SENDER_ID]
            receiver_id = bid_obj[BID_FIELD_NAMES.RECEIVER_ID]
            if user_id != receiver_id:
                user_ids_to_get.append(receiver_id)
            elif user_id != sender_id:
                user_ids_to_get.append(sender_id)
            else:
                current_app.logger.debug('Someone liked or bid on themselves..')
                current_app.logger.debug(
                    'sender_id: %s, receiver_id: %s, bid_group_name: %s ' %
                    (str(sender_id), str(receiver_id), str(bid_group_name))
                )
                pass

    return user_ids_to_get

def _is_poke(bid_obj):
    return get_bid_state(bid_obj) in get_enum_values(POKE_STATES)

def _is_pin(bid_obj):
    return get_bid_state(bid_obj) == BID_STATES.SENDER_LIKED

def _reconcile_user_objects_with_bid_groups(list_of_users, grouped_bids):
    users_by_id = {user_obj['id']: user_obj for user_obj in list_of_users}
    grouped_users = {key: [] for key, val in grouped_bids.iteritems()}
    for bid_group_name, bid_group in grouped_bids.iteritems():
        for bid_obj in bid_group:
            sender_id = bid_obj[BID_FIELD_NAMES.SENDER_ID]
            receiver_id = bid_obj[BID_FIELD_NAMES.RECEIVER_ID]
            if receiver_id in users_by_id:
                # TODO(daddy): This is a hack so we don't have to do any computation
                # in the frontend. Should think of something more elegant than this...
                if _is_poke(bid_obj) and not users_by_id.get(receiver_id, {}).get('bid_data', False):
                    users_by_id[receiver_id]['poke_data'] = bid_obj
                elif _is_pin(bid_obj) and not users_by_id.get(receiver_id, {}).get('bid_data', False):
                    users_by_id[receiver_id]['pin_data'] = bid_obj
                else:
                    users_by_id[receiver_id]['poke_data'] = None
                    users_by_id[receiver_id]['pin_data'] = None
                    users_by_id[receiver_id]['was_sender'] = False
                    users_by_id[receiver_id]['bid_data'] = bid_obj
                grouped_users[bid_group_name].append(users_by_id[receiver_id])
            elif sender_id in users_by_id:
                # TODO(daddy): This is a hack so we don't have to do any computation
                # in the frontend. SHould think of something more elegant than this...
                if _is_poke(bid_obj) and not users_by_id.get(sender_id, {}).get('bid_data', False):
                    users_by_id[sender_id]['poke_data'] = bid_obj
                elif _is_pin(bid_obj) and not users_by_id.get(sender_id, {}).get('bid_data', False):
                    users_by_id[receiver_id]['pin_data'] = bid_obj
                else:
                    users_by_id[sender_id]['poke_data'] = None
                    users_by_id[sender_id]['pin_data'] = None
                    users_by_id[sender_id]['was_sender'] = True
                    users_by_id[sender_id]['bid_data'] = bid_obj
                grouped_users[bid_group_name].append(users_by_id[sender_id])
    return grouped_users

def _get_users_for_bid_groups(user_id, grouped_bids):
    user_ids_to_get = _get_user_ids_from_grouped_bids(user_id, grouped_bids)
    list_of_users = get_list_of_users_from_db(user_ids_to_get)
    sort_user_photos(list_of_users)
    grouped_users = _reconcile_user_objects_with_bid_groups(list_of_users, grouped_bids)
    return grouped_users

def _get_categorized_bids(user_id, user_bids):
    grouped_bids = {group_key: [] for group_key in BID_GROUP_KEY_LIST}
    for bid_obj in user_bids:
        _append_bid_to_proper_group(bid_obj, user_id, grouped_bids)

    return grouped_bids

def get_user_likes(user_id):
    likes = get_db().bids.find({BID_FIELD_NAMES.SENDER_ID: ObjectId(user_id),
        BID_FIELD_NAMES.BID_STATE: BID_STATES.SENDER_LIKED})
    user_ids_he_likes = [u[BID_FIELD_NAMES.RECEIVER_ID] for u in list(likes)]
    return get_list_of_users_from_db(user_ids_he_likes)

def get_users_and_bids(user_id):
    current_app.logger.debug('Getting user with id ' + unicode(user_id))
    user_found = _get_user_by_id(user_id)
    if user_found is None:
        return None

    user_bids = get_bids_involved_with(user_id)
    bids_by_category = _get_categorized_bids(user_id, user_bids)
    users_by_category = _get_users_for_bid_groups(user_id, bids_by_category)

    return {'user': user_found, 'bids_by_category': bids_by_category,
            'users_by_category': users_by_category, 'stats_for_user': get_stats_for_user(user_id)}
  

def get_most_recent_bid(sender_id, receiver_id, exclude_pins=False):
    # Filter out cancelled bids
    states_to_exclude = CANCELLED_BID_STATES
    if exclude_pins:
        states_to_exclude += [BID_STATES.SENDER_LIKED]
    uncancelled_bids = get_db().bids.find(
        {'$and': [
            {'$or': [
                {BID_FIELD_NAMES.SENDER_ID: ObjectId(sender_id),
                 BID_FIELD_NAMES.RECEIVER_ID: ObjectId(receiver_id)}, 
                {BID_FIELD_NAMES.SENDER_ID: ObjectId(receiver_id),
                 BID_FIELD_NAMES.RECEIVER_ID: ObjectId(sender_id)}
            ]},
            {BID_FIELD_NAMES.BID_STATE: 
                {'$nin': states_to_exclude}
            }
        ]}
    )
    # Sort the uncancelled bids by creation time (most recent first).
    recent_bids = list(uncancelled_bids.sort([
        (BID_FIELD_NAMES.TIME_BID_CREATED_AT, -1)
    ]))

    if len(recent_bids) > 0:
        return recent_bids[0]
    else:
        return None

def bid_expired(bid_obj):
    bid_outstanding = get_bid_state(bid_obj) == BID_STATES.OUTSTANDING
    sender_confirmed = get_bid_state(bid_obj) == BID_STATES.SENDER_CONFIRMED
    receiver_accepted = get_bid_state(bid_obj) == BID_STATES.RECEIVER_ACCEPTED
    if bid_outstanding:
        return times_already_passed(bid_obj[BID_FIELD_NAMES.TIMES_AND_PLACES_LIST])
    elif sender_confirmed or receiver_accepted:
        bid_date = get_bid_selected_date_time(bid_obj)
        if bid_date is None:
            current_app.logger.error('Encountered accepted bid with no selected date: ' +
                str(bid_obj))
            return True

        if bid_date < datetime.datetime.utcnow():
            # The date has passed so this bid is expired.
            return True
        else:
            return False

def validate_session(session, user_id):
    if session.get('user_id', None) != user_id:
        current_app.logger.debug('Session token expired; aborting!')
        return error_response('user_bid_access')
    if user_id is None:
        current_app.logger.debug('Bidder id was None.')
        return error_response('bad_sender_id')
    return None

def set_raw_bid_fields(bid_obj):
    bid_obj[BID_FIELD_NAMES.TIME_BID_CREATED_AT] = datetime.datetime.utcnow()
    bid_obj[BID_FIELD_NAMES.TIMESTAMP_LIST] = []

def update_bid(bid_obj, fieldsToSet):
    get_db().bids.update(
        {'_id': bid_obj['_id']},
        {'$set': fieldsToSet}
    )
    return make_json_response(fieldsToSet)

def update_poke(poke_obj, fieldsToSet):
    get_db().pokes.update(
        {'_id': poke_obj['_id']},
        {'$set': fieldsToSet}
    )
    return make_json_response(fieldsToSet)

def get_enum_values(enum_object):
    return [x[1] for x in enum_object.__dict__.iteritems()
            if not x[0].startswith('__')]

def get_bid_fields(request_dict):
    times_and_places_list = (
        request_dict.get(BID_FIELD_NAMES.TIMES_AND_PLACES_LIST, []))
    bid_amount = int(request_dict.get(BID_FIELD_NAMES.BID_AMOUNT, -1))
    receiver_id = request_dict.get(BID_FIELD_NAMES.RECEIVER_ID, None)
    return (times_and_places_list, bid_amount, receiver_id)

def validate_bid_inputs(times_and_places_list, bid_amount, sender_id, receiver_id):
    if (times_and_places_list is None or
        len(times_and_places_list) == 0
    ):
        current_app.logger.debug('Bid contained no times+places.')
        return error_response('bad_bid_times')
    elif bid_amount == -1:
        current_app.logger.debug('Bid amount was None.')
        return error_response('bid_was_none')
    elif bid_amount < 0 or bid_amount > MAX_BID_AMOUNT:
        current_app.logger.debug('Bad bid rejected: ' + bid_amount)
        return error_response('bad_bid_amount')
    elif receiver_id is None:
        current_app.logger.debug('receiver id was None.')
        return error_response('bad_receiver_id')
    elif sender_id == receiver_id:
        current_app.logger.debug('receiver id was same as sender id on bid action.')
        return error_response('bid_on_yourself')
    elif times_already_passed(times_and_places_list):
        current_app.logger.debug('This date time has already passed')
        return error_response('date_passed')

    return None

def get_stats_for_user(user_id):
    # TODO(daddy): THIS HAS NO AUTOMATED TESTS!
    # I just tested it manually in conjunction with seed_random_reviews.js ... 
    sr = BID_FIELD_NAMES.SENDER_REVIEW
    user_was_receiver = get_db().bids.find(
      {
        BID_FIELD_NAMES.RECEIVER_ID: ObjectId(user_id),
        BID_FIELD_NAMES.BID_STATE: BID_STATES.SENDER_CONFIRMED,
        BID_FIELD_NAMES.SENDER_REVIEW: {'$exists': True}
      },
      {
        sr + '.' + SENDER_REVIEW_FIELDS.RECEIVER_RATING: 1,
        sr + '.' + SENDER_REVIEW_FIELDS.RECEIVER_SHOWED_UP: 1,
        sr + '.' + SENDER_REVIEW_FIELDS.LOOKED_WORSE_THAN_PICS: 1,
         '_id': 0
       }
    );

    rr = BID_FIELD_NAMES.RECEIVER_REVIEW
    user_was_sender = get_db().bids.find(
      {
        BID_FIELD_NAMES.SENDER_ID: ObjectId(user_id),
        BID_FIELD_NAMES.BID_STATE: BID_STATES.SENDER_CONFIRMED,
        BID_FIELD_NAMES.RECEIVER_REVIEW: {'$exists': True},
        BID_FIELD_NAMES.SENDER_REVIEW: {'$exists': True},
      },
      {
        rr + '.' + RECEIVER_REVIEW_FIELDS.LOOKED_WORSE_THAN_PICS: 1,
        rr + '.' + RECEIVER_REVIEW_FIELDS.COMFORT_RATING: 1,
        rr + '.' + RECEIVER_REVIEW_FIELDS.DID_SHOW_UP: 1,
        sr + '.' + SENDER_REVIEW_FIELDS.WOULD_LIKE_TO_PAY: 1,
        '_id': 0
      }
    );
    
    stats_fields = {}
    for stat_key in get_enum_values(STATS_FIELDS):
        stats_fields[stat_key] = 0

    total_dates = 0
    for bid_obj in user_was_receiver:
        total_dates += 1
        if bid_obj[sr][SENDER_REVIEW_FIELDS.RECEIVER_SHOWED_UP]:
            # Rating only counts if person admits to showing up.
            if bid_obj[sr][SENDER_REVIEW_FIELDS.RECEIVER_RATING] == 0:
                stats_fields[STATS_FIELDS.UNSATISFIED_DATE] += 1
            elif bid_obj[sr][SENDER_REVIEW_FIELDS.RECEIVER_RATING] == 1:
                # We don't provide a summarry stat for just being satisfied-- yet.
                pass
            elif bid_obj[sr][SENDER_REVIEW_FIELDS.RECEIVER_RATING] == 2:
                stats_fields[STATS_FIELDS.VERY_SATISFIED] += 1

            if bid_obj[sr][SENDER_REVIEW_FIELDS.LOOKED_WORSE_THAN_PICS]:
                stats_fields[STATS_FIELDS.LOOKED_WORSE_THAN_PICS] += 1
        else:
            stats_fields[STATS_FIELDS.NO_SHOW] += 1

    for bid_obj in user_was_sender:
        total_dates += 1
        if bid_obj[rr][RECEIVER_REVIEW_FIELDS.DID_SHOW_UP]:
            # Rating only counts if person admits to showing up.
            if bid_obj[rr][RECEIVER_REVIEW_FIELDS.COMFORT_RATING] == 0:
                stats_fields[STATS_FIELDS.UNCOMFORTABLE_DATE] += 1
            elif bid_obj[rr][RECEIVER_REVIEW_FIELDS.COMFORT_RATING] == 1:
                # We don't provide a summarry stat for just being satisfied-- yet.
                pass
            elif bid_obj[rr][RECEIVER_REVIEW_FIELDS.COMFORT_RATING] == 2:
                stats_fields[STATS_FIELDS.VERY_COMFORTABLE] += 1

            if (not bid_obj[sr][SENDER_REVIEW_FIELDS.WOULD_LIKE_TO_PAY]):
                # The receiver said she showed up but the sender didnt't pay, so mark
                # this as a no-pay for the sender.
                stats_fields[STATS_FIELDS.NO_PAY] += 1

            if bid_obj[rr][RECEIVER_REVIEW_FIELDS.LOOKED_WORSE_THAN_PICS]:
                stats_fields[STATS_FIELDS.LOOKED_WORSE_THAN_PICS] += 1

    stats_fields[STATS_FIELDS.NUM_DATES] = total_dates
    return stats_fields

def add_bid_state_to_users(user_id, user_list):
    user_found = _get_user_by_id(user_id)
    user_bids = get_bids_involved_with(user_id)

    bids_by_user_id = {}
    for bid_obj in user_bids:
        sender_id = bid_obj[BID_FIELD_NAMES.SENDER_ID]
        receiver_id = bid_obj[BID_FIELD_NAMES.RECEIVER_ID]
        if sender_id == user_id:
            bids_by_user_id[receiver_id] = bid_obj
        else:
            bids_by_user_id[sender_id] = bid_obj

    for user_obj in user_list:
        user_obj['bid_data'] = bids_by_user_id.get(user_obj['id'], None)

    # After we set the date state for real bids, we set the pokes.
    user_pokes = get_my_pokes(user_id)
    pokes_by_user_id = {}
    for poke_obj in user_pokes:
        sender_id = poke_obj[BID_FIELD_NAMES.SENDER_ID]
        receiver_id = poke_obj[BID_FIELD_NAMES.RECEIVER_ID]
        if sender_id == user_id:
            pokes_by_user_id[receiver_id] = poke_obj
        else:
            pokes_by_user_id[sender_id] = poke_obj

    for user_obj in user_list:
        user_obj['poke_data'] = pokes_by_user_id.get(user_obj['id'], None)


