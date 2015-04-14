`import Ember from 'ember'`
`import SimpleData from '../utils/simple-data';`
`import { sortFacebookPhotosByPosition, getAllFacebookPhotos } from '../utils/common-functions';`

PicRearrangerComponent = Ember.Component.extend({
  allPhotos: null
  user: null
  closeCallback: null

  actions:
    uploadFromFacebook: ->
      self = this
      getAllFacebookPhotos(self, 'allPhotos')
      Ember.$('.onboarding-flow-comp__rearrange-container')
      .animate({'margin-left': "+=300%", 'margin-right': "-=300%"}, {duration: 1000, queue: false, complete: ->
        $(this).parent().addClass('display-none')})
      Ember.$('.onboarding-flow-comp__facebook-picker-container').parent().removeClass('display-none')
      Ember.$('.onboarding-flow-comp__facebook-picker-container')
        .animate({'margin-left': "+=300%", 'margin-right': "-=300%"}, {duration: 1000, queue: false})

    backFromProfileInfoView: ->
      Ember.$('.onboarding-flow-comp__rearrange-container').parent().removeClass('display-none')
      Ember.$('.onboarding-flow-comp__rearrange-container')
        .animate({'margin-left': "+=300%", 'margin-right': "-=300%"}, {duration: 1000, queue: false})
      Ember.$('.onboarding-flow-comp__user-info-container')
      .animate({'margin-left': "+=300%", 'margin-right': "-=300%"}, {duration: 1000, queue: false, complete: ->
        $(this).parent().addClass('display-none')})

    doneUploadingFacebook: ->
      Ember.$('.onboarding-flow-comp__rearrange-container').parent().removeClass('display-none')
      Ember.$('.onboarding-flow-comp__rearrange-container')
        .animate({'margin-left': "-=300%", 'margin-right': "+=300%"}, {duration: 1000, queue: false})
      Ember.$('.onboarding-flow-comp__facebook-picker-container')
      .animate({'margin-left': "-=300%", 'margin-right': "+=300%"}, {duration: 1000, queue: false, complete: ->
        $(this).parent().addClass('display-none')})

    doneRearrangingPics: ->
      Ember.$('.onboarding-flow-comp__rearrange-container')
      .animate({'margin-left': "-=300%", 'margin-right': "+=300%"}, {duration: 1000, queue: false, complete: ->
        $(this).parent().addClass('display-none')})
      Ember.$('.onboarding-flow-comp__user-info-container').parent().removeClass('display-none')
      Ember.$('.onboarding-flow-comp__user-info-container')
        .animate({'margin-left': "-=300%", 'margin-right': "+=300%"}, {duration: 1000, queue: false})

    sendCloseCallback: ->
      self = this
      window.scrollTo(0, 0)
      Ember.$('.onboarding-flow-comp__user-info-container')
      .animate({'margin-left': "-=300%", 'margin-right': "+=300%"}, {duration: 1000, queue: true, complete: (
        -> 
          self.sendAction('closeCallback')
      )})
})

`export default PicRearrangerComponent`
