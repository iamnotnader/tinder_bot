`import Ember from 'ember'`
`import SimpleData from '../utils/simple-data';`
`import ConstantValues from '../utils/constant-values';`
`import nameGenerator from '../utils/name-generator';`
`import BaseController from './base-controller';`
`import { sortFacebookPhotosByPosition,
          getAllFacebookPhotos } from '../utils/common-functions';`

MainFeedViewController = BaseController.extend(
  needs: ['application', 'home']

  pinnedUsers: (->
    @appGet('usersByCategory.user_likes')
  ).property('controllers.application.usersByCategory.user_likes')

  usersHaveBidOnYou: (->
    @appGet('usersByCategory.have_bid_on_you')
  ).property('controllers.application.usersByCategory.have_bid_on_you')

  usersYouHaveBidOn: (->
    @appGet('usersByCategory.you_have_bid_on')
  ).property('controllers.application.usersByCategory.you_have_bid_on')

  upcomingDates: (->
    upcomingDates = @appGet('usersByCategory.confirmed_upcoming_dates')
    return {} unless upcomingDates?
    ret = {}
    ret.youPaid = []
    ret.theyPaid = []
    for dateObj in upcomingDates
      if dateObj.was_sender
        ret.theyPaid.push(dateObj)
      else
        ret.youPaid.push(dateObj)
    return ret
  ).property('controllers.application.usersByCategory.confirmed_upcoming_dates')

  unpaidDates: (->
    unpaidDates = @appGet('usersByCategory.unconfirmed_upcoming_dates')
    return {} unless unpaidDates?
    ret = {}
    ret.waitingOnThemToPay = []
    ret.youNeedToPay = []
    for dateObj in unpaidDates
      if dateObj.was_sender
        ret.waitingOnThemToPay.push(dateObj)
      else
        ret.youNeedToPay.push(dateObj)
    return ret
  ).property('controllers.application.usersByCategory.unconfirmed_upcoming_dates')

  pastUnreviewedDates: (->
    unpaidDates = @appGet('usersByCategory.past_unreviewed_dates')
    return {} unless unpaidDates?
    ret = {}
    ret.theyPaid = []
    ret.youPaid = []
    for dateObj in unpaidDates
      if dateObj.was_sender
        ret.theyPaid.push(dateObj)
      else
        ret.youPaid.push(dateObj)
    return ret
  ).property('controllers.application.usersByCategory.past_unreviewed_dates')

  youPoked: (->
    youPoked = @appGet('usersByCategory.you_poked')
    return unless youPoked?
    ret = {}
    ret.proposedOffer = []
    ret.noOffer = []
    for pokedUser in youPoked
      if pokedUser?.poke_data?.poke_proposal?
        ret.proposedOffer.push(pokedUser)
      else
        ret.noOffer.push(pokedUser)
    return ret
  ).property('controllers.application.usersByCategory.you_poked')

  pokedYou: (->
    pokedYou = @appGet('usersByCategory.poked_you')
    return [] unless pokedYou?
    ret = []
    for userObj in pokedYou
      if userObj.bid_data?
        continue
      ret.push(userObj)
    return ret
  ).property('controllers.application.usersByCategory.poked_you')

  fieldsSet1: {}
  fieldsSet2: {}
  fieldsSet3: {}

  sharedFields: {
    amountToBid: null
    placeSelected: ''
  }

  actions:
    updateBiddiesAndOffers: ->
      @get('controllers.home').send('updateBiddiesAndOffers', null)

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

`export default MainFeedViewController`
