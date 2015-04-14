`import Ember from 'ember'`
`import SimpleData from '../utils/simple-data';`

sortFacebookPhotosByPosition = (self, photosKey) ->
    sortedFacebookPhotos = self.get(photosKey).slice()
    sortedFacebookPhotos.sort((a, b) ->
        return Number.POSITIVE_INFINITY unless a.photo_position? and a.photo_position isnt -1
        return Number.NEGATIVE_INFINITY unless b.photo_position? and b.photo_position isnt -1
        return a.photo_position - b.photo_position
    )
    self.set(photosKey, sortedFacebookPhotos)

_handlePhotos = (self, photos) ->
  # TODO(daddy): Avoid creating repeats of photos. Check to see if they already
  # exist before posting them and stuff.
  userId = self.get('user.id')
  unless userId?
    @send('openModelModal', 'alert-modal', {title: "Problem downloading PHOTOS from facebook."})

  # TODO(daddy): Make this promises.all() style.
  simplePhotos = []
  for photo in photos.data
    simplePhotos.push(
      facebook_id: photo.id
      source_url: photo.source
      photo_position: null
    )
  SimpleData.patchAllPhotos(userId, simplePhotos)
  .then((user) ->
    Ember.run(->self.set('user.photos', user.photos))
  )

_fetchFacebookStuff = (self)->
  FB.login(
    (res) ->
      if (res.authResponse)
        FB.api('/me', (basicResponse) ->
          #self.sendAction('handleBasicInfo', basicResponse)
          #console.log('Basic info scraped.')
        );
        FB.api('/me/photos', (photoResponse) ->
          _handlePhotos(self, photoResponse)
          console.log('Photos scraped.')
        );

        console.log('good auth')
      else
        console.log('ERROR: Received facebook response with no authResponse.')
    {scope: 'public_profile,email,user_photos,user_friends'}
  )

getAllFacebookPhotos = (self, photoKey) ->
  selectedPhotos = self.get(photoKey)?.filter((x) -> x.photo_position?)
  unless selectedPhotos?
    _fetchFacebookStuff(self)
  if selectedPhotos?
    for photo, i in selectedPhotos
      photo.photo_position = i+1
    sortFacebookPhotosByPosition(self, photoKey)

`export var sortFacebookPhotosByPosition`
`export var getAllFacebookPhotos`