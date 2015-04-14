`import Ember from 'ember'`
`import ENV from 'biddie-frontend/config/environment';`


SimpleData =
  userCache: {}
  photoCache: {}

  # Common utilities
  getPath: (path) ->
    BASE_URL = ENV.APP.API_HOST + '/' + ENV.APP.API_NAMESPACE
    Ember.$.ajax(
      url: BASE_URL+path,
      type: "GET",
      xhrFields: {
        withCredentials: true
      },
      crossDomain: true
    )

  postPath: (path, postData) ->
    BASE_URL = ENV.APP.API_HOST + '/' + ENV.APP.API_NAMESPACE
    Ember.$.ajax(
      url: BASE_URL+path
      type: "POST",
      contentType: 'application/json',
      dataType: 'json',
      data: JSON.stringify(postData),
      xhrFields: {
        withCredentials: true
      },
      crossDomain: true
    )

  deletePath: (path, deleteData, async=true) ->
    BASE_URL = ENV.APP.API_HOST + '/' + ENV.APP.API_NAMESPACE
    Ember.$.ajax(
      url: BASE_URL+path
      type: "DELETE"
      contentType: 'application/json',
      dataType: 'json',
      data: JSON.stringify(deleteData),
      xhrFields: { withCredentials: true }
      crossDomain: true
      async: async
    )

  patchPath: (path, patchData) ->
    BASE_URL = ENV.APP.API_HOST + '/' + ENV.APP.API_NAMESPACE
    Ember.$.ajax(
      url: BASE_URL+path
      type: "PATCH",
      contentType: 'application/json',
      dataType: 'json',
      data: JSON.stringify(patchData),
      xhrFields: { withCredentials: true }
      crossDomain: true
    )


  # User functions
  # TODO(daddy): implement postUser? It's already there on the backend..
  getUserWithId: (id, force=false) ->
    userCache = @userCache
    unless id?
      console.log('getUserWithId with UNDEFINED id')
      return

    if id of userCache and not force
      userCache[id].was_cached = true
      return new Ember.RSVP.Promise((resolve, reject) -> resolve(userCache[id]))

    # This should be a simple get request. Return an obj.
    @getPath('users/'+id+'/')
    .then(
      (userRes) ->
        if userRes.id?
          userCache[id] = userRes
          return userRes
        else
          return null
      (err) ->
        console.log('Error fetching user with id: ' + id + ' ' + err.statusText)
        return null
    )

  patchUser: (id, fieldsToPatch) ->
    unless id?
      console.log('patchUser with UNDEFINED id')
      return

    userCache = @userCache
    @patchPath('users/'+id+'/', fieldsToPatch)
    .then((userRes) ->
      if userRes.id?
        # Return the user that we just patched.
        userCache[userRes.id] = userRes
        return userRes
      else
        console.log('Error patching user with id: ' + id + ' ' + err.statusText)
        return null
    )


  # Photo functions
  postPhoto: (user_id, photo) ->
    unless user_id?
      console.log('ppostPhoto with UNDEFINED id')
      return

    userCache = @userCache
    # Creating a photo makes the profile it's attached to dirty.
    delete userCache[user_id]

    @postPath('photo/'+user_id+'/', {photo})
    .then((userRes) ->
      if userRes.id?
        userCache[user_id] = userRes
        return userRes
      else
        console.log('Error creating photo for user with id: ' + user_id + ' ' + err.statusText)
        return null
    )

  postAllPhotos: (user_id, photoList) ->
    unless user_id?
      console.log('postAllPhotos with UNDEFINED id')
      return

    userCache = @userCache

    @postPath('user_photos/'+user_id+'/', {photo_list: photoList})
    .then((userRes) ->
      if userRes.id?
        userCache[userRes.id] = userRes
        return userRes
      else
        console.log('Error patching photo for user with id: ' + user_id + ' ' + err.statusText)
        return null
    )

  patchAllPhotos: (user_id, photoList) ->
    unless user_id?
      console.log('getAllPhotos with UNDEFINED id')
      return

    userCache = @userCache

    @patchPath('user_photos/'+user_id+'/', {photo_list: photoList})
    .then((userRes) ->
      if userRes.id?
        userCache[userRes.id] = userRes
        return userRes
      else
        console.log('Error patching photo with id: ' + id + ' ' + err.statusText)
        return null
    )

  getAllPhotos: (user_id) ->
    # We don't update the cache for this.
    @getPath('user_photos/'+user_id+'/')

  searchWithCriteria: (criteria) ->
    @postPath('search_with_criteria/', criteria)

  postBid: (sender_id, receiver_id, bid_amount, times_and_places_list) ->
    @postPath('bids/'+sender_id+'/', {
      receiver_id
      bid_amount
      times_and_places_list
    })

  getBids: (sender_id) ->
    @getPath('bids/'+sender_id+'/')

  getUserList: (user_ids) ->
    @postPath('user_list/', {
      user_ids
    })

  cancelBid: (sender_id, receiver_id) ->
    @postPath('bids/cancel/'+sender_id+'/', {
      receiver_id
    })

  acceptBid: (sender_id, receiver_id, accepted_time_and_place_index) ->
    @postPath('bids/accept/'+sender_id+'/', {
      receiver_id
      accepted_time_and_place_index
    })

  payMe: (sender_id, receiver_id, payment_token) ->
    @postPath('pay_and_confirm/'+sender_id+'/', {
      receiver_id
      payment_token
    })

  likeUser: (sender_id, receiver_id) ->
    @postPath('like/'+sender_id+'/', {
      receiver_id
    })

  fetchUserWithCredentials: (email, password, errorCallback, successCallback) ->
      if email? and password?
        @postPath('login/', {email, password})
        .then(
          (res) ->
            unless res.user?.id?
              if res.message? 
                title = res.message
              else
                title = 'Whoops! Something really weird happened.'
              errorCallback(title)
              return
            successCallback(res)
          (err) ->
            console.log('Error hitting login action: ' + err.statusText)
        )
      else
        # If we don't have an email address or password, we're banking on the
        # browser's cookie being set.
        @getPath('login/')
        .then(
          (res) ->
            if (res.user?.id?)
              successCallback(res)
            else
              errorCallback(res)
              console.log('User is not logged in.')
              return null
          (err) ->
            errorCallback()
            console.log('Error fetching model application: ' + err.statusText)
            return null
        )

  createUser: (email, password, errorCallback, successCallback) ->
    @postPath('users/', {'email': email, 'password': password})
    .then(
      (res) ->
        unless res.id?
          if res.message? 
            title = res.message
          else
            title = 'Whoops! Something really weird happened.'
          errorCallback(title)
          return
        successCallback(res)
      (err) ->
        console.log('Error hitting signup action: ' + err.statusText)
    )

`export default SimpleData`
