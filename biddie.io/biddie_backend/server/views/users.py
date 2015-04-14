from flask import request, session, \
     jsonify, Response, current_app
from bson.objectid import ObjectId
from random import shuffle

from server.constants import USER_FIELD_NAMES
from server.utils import (error_response, crossdomain, JSONEncoder,
                          get_long_lat_for_zip, get_db,
                          sort_user_photos, get_stats_for_user,
                          add_bid_state_to_users)
from server import app

from datetime import datetime, timedelta
import random


@app.route('/', methods=['GET', 'OPTIONS'])
@crossdomain(methods=['GET'])
def jizz_on_me():
    return jsonify({'FUCK': 'ME!'})


# Note: the POST piece of this endpoint is part of the "login" view
@app.route('/users/<user_id>/', methods=['GET', 'PATCH', 'DELETE', 'OPTIONS'])
@crossdomain()
def modify_user(user_id=None):
    if request.method == 'GET':
        current_app.logger.debug('Getting user with id ' + unicode(user_id))
        user_found = get_db().users.find_one({'_id': ObjectId(user_id)})
        if user_found is None:
            current_app.logger.debug('User not found.')
            return error_response('does_not_exist')
        else:
            user_found['id'] = user_found.pop('_id')
            encoded_json = JSONEncoder().encode(user_found)
            current_app.logger.debug('Found user \n' + encoded_json)
            return Response(response=JSONEncoder().encode(user_found),
                            status=200,
                            mimetype="application/json")

    if request.method == 'PATCH':
        current_app.logger.debug('Patching user.')
        if session.get('user_id', None) != user_id:
            return Response("You cannot modify another user's profile.",
                            status=405)

        current_app.logger.debug('Patching fields \n' +
                                 str(request.get_json()))

        updates_to_make = {}
        for field_name, field_value in request.get_json().items():
            if field_value == '':
                field_value = None
            if field_name == USER_FIELD_NAMES.ZIP_CODE:
                long_lat = get_long_lat_for_zip(field_value)
                # Add a long/lat pair to this user if we get a zip code.
                updates_to_make[USER_FIELD_NAMES.LOCATION] = long_lat
                current_app.logger.debug('Added long/lat ' + str(long_lat) +
                                         ' for zip ' + field_value)
            updates_to_make[field_name] = field_value
        updated_user = get_db().users.find_and_modify(
            query={'_id': ObjectId(user_id)},
            update={'$set': updates_to_make},
            new=True
        )
        updated_user['id'] = updated_user.pop('_id')

        encoded_json = JSONEncoder().encode(updated_user)
        current_app.logger.debug('Patched user: \n' + encoded_json)

        return Response(response=encoded_json,
                        status=200,
                        mimetype="application/json")


def sort_search_results(matching_users):
    def sort_func(user_a, user_b):
        # Make sure online users show up at the top.
        if (user_a.get('is_online') and not user_b.get('is_online')):
            return -1
        elif (user_b.get('is_online') and not user_a.get('is_online')):
            return 1
        else:
            return 0
    matching_users.sort(cmp=sort_func)


# Returns a list of user objects matching given criteria.
# Basically, just filter on whatever fields you want.
#
# If zip_code field is provided, return nearest to zip.
@app.route('/search_with_criteria/', methods=['POST', 'OPTIONS'])
@crossdomain()
def users_search():
    if request.method == 'POST':
        request_dict = request.get_json()

        search_criteria = {}
        photos_required = False
        for field_name, field_value in request_dict.items():
            if field_value == '' or field_value is None:
                continue
            elif field_name == USER_FIELD_NAMES.ZIP_CODE:
                long_lat = get_long_lat_for_zip(field_value)
                # Add a long/lat nearest criterion if we get a zip code.
                loc_query = {
                    '$near': {
                        '$geometry': {
                            'type': "Point", 'coordinates': long_lat}}}
                search_criteria[USER_FIELD_NAMES.LOCATION] = loc_query
            elif field_name == USER_FIELD_NAMES.PHOTOS:
                # Only return users that have at leaast one element.
                search_criteria[field_name + '.1'] = {
                        '$exists': bool(field_value)}
                photos_required = field_value
            else:
                search_criteria[field_name] = field_value

        # Default to female.
        if not search_criteria.get('sex', False):
            search_criteria['sex'] = 'f'

        user_id_to_exclude = ObjectId(session['user_id'])
        search_criteria['_id'] = {'$ne': user_id_to_exclude}
        # TODO(daddy): Don't hardcode 32...
        matching_users = list(get_db().users.find(search_criteria))
        shuffle(matching_users)
        matching_users = matching_users[:32]
        for user in matching_users:
            user['id'] = user.pop('_id')
            user['stats_for_user'] = get_stats_for_user(user['id'])
            sort_user_photos(matching_users)
            last_login_time = user.get(USER_FIELD_NAMES.LAST_LOGIN_TIME, None)
            earliest_acceptable_login = (
                datetime.utcnow() -
                timedelta(minutes=15))

            if (last_login_time is not None):
                last_login_time = last_login_time.replace(tzinfo=None)
                if (last_login_time > earliest_acceptable_login):
                    user['is_online'] = True
            if user.get('is_fake_user'):
                if random.random() < .2:
                    user['is_online'] = True
        if photos_required:
            matching_users = [user_obj
                              for user_obj in matching_users
                              if (user_obj.get('photos', None) is not None and
                                  len(user_obj['photos']) > 0)]

        add_bid_state_to_users(user_id_to_exclude, matching_users)
        matching_users = [
            x for x in matching_users
            if not (x.get('bid_data', False) or x.get('poke_data', False))]

        sort_search_results(matching_users)
        return Response(response=JSONEncoder().encode(matching_users),
                        status=200,
                        mimetype="application/json")


@app.route('/user_list/', methods=['POST', 'OPTIONS'])
@crossdomain()
def user_list():
    if request.method == 'POST':
        # Expect a list of user _id's
        current_app.logger.debug('Getting users')
        request_data = request.get_json()
        user_ids = request_data.get('user_ids', None)
        if user_ids is None or len(user_ids) == 0:
            return Response(response=JSONEncoder().encode({'user_list': []}),
                            status=200,
                            mimetype="application/json")

        user_ids = [{'_id': ObjectId(x)} for x in user_ids]
        matching_users = get_db().users.find(
            {'$or': user_ids}
        )
        matching_users = list(matching_users)
        for user in matching_users:
            user['id'] = user.pop('_id')
            user['stats_for_user'] = get_stats_for_user(user['id'])
        encoded_json = JSONEncoder().encode(matching_users)
        current_app.logger.debug('Got users: \n' + encoded_json)
        return Response(response=encoded_json,
                        status=200,
                        mimetype="application/json")

if __name__ == "__main__":
    current_app.run()
