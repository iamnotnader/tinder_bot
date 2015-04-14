`import Ember from 'ember'`
`import SimpleData from '../utils/simple-data';`
`import ConstantValues from '../utils/constant-values';`
`import nameGenerator from '../utils/name-generator';`
`import BaseController from './base-controller';`
`import { sortFacebookPhotosByPosition,
          getAllFacebookPhotos } from '../utils/common-functions';`

THROTTLE_MS = 1000

ProfileController = BaseController.extend(
  inAboutSection: true
  inPhotoRearrangeSection: false
  inFacebookPhotoUploadSection: false

  inPhotosSection: (->
    return @get('inPhotoRearrangeSection') or @get('inFacebookPhotoUploadSection')
  ).property('inPhotoRearrangeSection', 'inFacebookPhotoUploadSection')

  actions:
    aboutButtonPressed: ->
      @set('inAboutSection', true)
      @set('inPhotoRearrangeSection', false)
      @set('inFacebookPhotoUploadSection', false)

    photosButtonPressed: ->
      @set('inAboutSection', false)
      @set('inPhotoRearrangeSection', true)
      @set('inFacebookPhotoUploadSection', false)

    uploadFromFacebook: ->
      @set('inAboutSection', false)
      @set('inPhotoRearrangeSection', false)
      @set('inFacebookPhotoUploadSection', true)
      self = this
      getAllFacebookPhotos(self, 'controllers.application.user.photos')     

    doneUploadingFacebook: ->
      @set('inAboutSection', false)
      @set('inPhotoRearrangeSection', true)
      @set('inFacebookPhotoUploadSection', false)
)

`export default ProfileController`
