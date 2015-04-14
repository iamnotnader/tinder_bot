from flask import request, session, jsonify, Response, current_app
import bcrypt

from server.utils import (error_response, crossdomain,
                          JSONEncoder, get_users_and_bids)
from server.views.users import get_db

from server import app
from bson.objectid import ObjectId
from server.constants import USER_FIELD_NAMES
from datetime import datetime


def _check_pw(pw, hashed_pw):
    return bcrypt.checkpw(pw, hashed_pw)


def _hash_pw(pw):
    return bcrypt.hashpw(pw, bcrypt.gensalt())


@app.route('/login/', methods=['GET', 'POST', 'DELETE', 'OPTIONS'])
@crossdomain(methods=['GET', 'POST', 'DELETE'])
def login():
    if request.method == 'GET':
        user_id = session.get('user_id', None)
        if user_id is None:
            return jsonify({'success': False, 'id': None})

        get_db().users.find_and_modify(
            query={'_id': ObjectId(user_id)},
            update={'$set': {
                USER_FIELD_NAMES.LAST_LOGIN_TIME:
                datetime.utcnow()}},
        )

        # Return the user with all their bids.
        user_info = get_users_and_bids(user_id)
        encoded_json = JSONEncoder().encode(user_info)
        current_app.logger.debug('User info fetched: \n' + encoded_json)

        return Response(response=encoded_json,
                        status=200,
                        mimetype="application/json")

    if request.method == 'POST':
        request_data = request.get_json()
        email = request_data['email']
        password = request_data['password']

        current_app.logger.debug('Attempting to log in user ' +
                                 'with email+password ' +
                                 email + ' ' + password)

        user_found = get_db().users.find_one({'email': email})
        if user_found is None:
            current_app.logger.debug('User does not exist.')
            return error_response('does_not_exist')
        elif not _check_pw(password, user_found.get('password')):
            current_app.logger.debug('Incorrect password.')
            return error_response('invalid')

        user_found['id'] = user_found.pop('_id')
        session['user_id'] = unicode(user_found['id'])

        user_info = get_users_and_bids(user_found['id'])

        encoded_json = JSONEncoder().encode(user_info)
        current_app.logger.debug('Logged in user \n' + encoded_json)

        return Response(response=encoded_json,
                        status=200,
                        mimetype="application/json")

    if request.method == 'DELETE':
        if session.get('user_id', None) is not None:
            del session['user_id']
        return jsonify({'success': True, 'id': None})


@app.route('/users/', methods=['POST', 'OPTIONS'])
@crossdomain()
def create_user():
    if request.method == 'POST':
        current_app.logger.debug('Creating user')
        request_data = request.get_json()
        email = request_data['email']
        password = request_data['password']

        # Check if a user with this email already exists.
        # If not, try to create her.
        old_user = get_db().users.find_and_modify(
            query={'email': email},
            update={
                '$setOnInsert': {
                    'password': _hash_pw(password),
                    'on_waitlist': False}},
            new=False,
            upsert=True
        )

        # If the user does exist, return.
        if old_user is not None:
            current_app.logger.debug('User already exists.')
            return error_response('user_exists')

        new_user = get_db().users.find_one({'email': email})
        new_user['id'] = new_user.pop('_id')

        # Also set the session cookie so the user will be logged in.
        session['user_id'] = unicode(new_user.get('id'))

        encoded_json = JSONEncoder().encode(new_user)
        current_app.logger.debug('Created user: \n' + encoded_json)

        return Response(response=encoded_json,
                        status=200,
                        mimetype="application/json")
