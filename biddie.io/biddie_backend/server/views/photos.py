from flask import request, session, flash, jsonify, Response
from bson.objectid import ObjectId

from server.constants import *
from server.utils import error_response, crossdomain, JSONEncoder, get_db
from server import app


@app.route('/user_photos/<user_id>/', methods=['GET', 'PATCH', 'POST', 'OPTIONS'])
@crossdomain()
def upload_all_photos(user_id=None):
    # Return all the user's photos
    if request.method == 'GET':
        user_found = get_db().users.find_one({'_id': ObjectId(user_id)})
        if user_found is None:
            return error_response('does_not_exist')
        elif user_found.get('photos') is None:
            return Response(response=JSONEncoder().encode([]),
                            status=200,
                            mimetype="application/json")
        else:
            return Response(response=JSONEncoder().encode(user_found.get('photos')),
                            status=200,
                            mimetype="application/json")


    # Merge a set of partially new photos with the user's existing photos.
    if request.method == 'PATCH':
        if session.get('user_id', None) != user_id:
            return Response("You cannot modify another user's photos.",
                            status=405)

        photos_to_upload = request.get_json()['photo_list']

        user_found = get_db().users.find_one({'_id': ObjectId(user_id)})
        if user_found is None:
            return error_response('does_not_exist')

        user_photos = user_found.get('photos')
        if user_photos is None:
            user_photos = []
        user_photodict = dict([(photo['source_url'], i) for i, photo in enumerate(user_photos)])

        new_photos = []
        for photo in photos_to_upload:
            this_source = photo['source_url']
            if this_source not in user_photodict:
                # Completely new photos get appended to the end
                new_photos.append(photo)
            else:
                # Photo we have from before gets its fields updated
                user_photos[user_photodict[this_source]] = photo

        user_photos.extend(new_photos)
        user_photos.sort(key=lambda x: x['photo_position'])

        updated_user = get_db().users.find_and_modify(
            query={'_id': ObjectId(user_id)},
            update={'$set': {'photos': user_photos}},
            new=True
        )
        updated_user['id'] = updated_user.pop('_id')

        return Response(response=JSONEncoder().encode(updated_user),
                        status=200,
                        mimetype="application/json")


    # Completely wipe out all the old photos and replace them with new ones without
    # giving a fuck.
    if request.method == 'POST':
        if session.get('user_id', None) != user_id:
            return Response("You cannot modify another user's photos.",
                            status=405)

        photos_to_upload = request.get_json()['photo_list']

        user_found = get_db().users.find_one({'_id': ObjectId(user_id)})
        if user_found is None:
            return error_response('does_not_exist')

        updated_user = get_db().users.find_and_modify(
            query={'_id': ObjectId(user_id)},
            update={'$set': {'photos': photos_to_upload}},
            new=True
        )
        updated_user['id'] = updated_user.pop('_id')

        return Response(response=JSONEncoder().encode(updated_user),
                        status=200,
                        mimetype="application/json")


# Allows you to upload and modify individual photos.
@app.route('/photo/<user_id>/', methods=['POST', 'DELETE', 'OPTIONS'])
@crossdomain()
def upload_single_photo(user_id=None):
    if request.method == 'POST':
        if session.get('user_id', None) != user_id:
            return Response("You cannot modify another user's photos.",
                            status=405)

        photo_to_upload = request.get_json()['photo']

        user_found = get_db().users.find_one({'_id': ObjectId(user_id)})
        if user_found is None:
            return error_response('does_not_exist')

        # TODO(daddy): Uh.. I think this is a race condition...
        user_photos = user_found.get('photos')
        if user_photos is None:
            user_photos = []
        photo_found = False
        for i, photo in enumerate(user_photos):
            if photo['source_url'] == photo_to_upload['source_url']:
                user_photos[i] = photo_to_upload
                photo_found = True
                break
        if not photo_found:
            user_photos.append(photo_to_upload)

        user_photos.sort(key=lambda x: x['photo_position'])

        updated_user = get_db().users.find_and_modify(
            query={'_id': ObjectId(user_id)},
            update={'$set': {'photos': user_photos}},
            new=True
        )
        updated_user['id'] = updated_user.pop('_id')

        return Response(response=JSONEncoder().encode(updated_user),
                        status=200,
                        mimetype="application/json")
