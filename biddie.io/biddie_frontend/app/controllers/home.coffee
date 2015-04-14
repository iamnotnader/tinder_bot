`import Ember from 'ember';`
`import SimpleData from '../utils/simple-data';`
`import ConstantValues from '../utils/constant-values';`
`import BaseController from './base-controller';`

REFRESH_TIME_MS = 1000

BLUE = "rgb(158, 192, 255)"
PURPLE = "rgb(228, 228, 255)"
GREY = "#fcfcfc"
PINK = "#FFF0F7"

HomeController = BaseController.extend(
  sharedFields: {
      fieldsSet1: {}
      fieldsSet2: {}
      fieldsSet3: {}
      timeChoices: null
  }

  test: (->
    self = this
    func = ->
      self.send('updateBiddiesAndOffers', REFRESH_TIME_MS)
    window.scrollTo(0,0)
    setTimeout(func, REFRESH_TIME_MS)
  ).on('init')

  userResults: []
  selectedPhotoIndex: null

  sexChoices: (-> return ConstantValues.sexChoices()).property()
  sexSearchChoices: (->
    sexChoices = @get('sexChoices').slice(0)
    sexChoices[0] = {label: 'any sex', id: '-'}
    return sexChoices
  ).property()

  orientationChoices: (-> ConstantValues.orientationChoices()).property()
  orientationSearchChoices: (->
    orientationChoices = @get('orientationChoices').slice(0)
    orientationChoices[0] = {label: 'any orientation', id: '-'}
    return orientationChoices
  ).property()

  selectedSearchSex: '-'
  selectedSearchOrientation: '-'

  oldInterval: null

  searchZipCode: ''

  # TODO(daddy): add mustHavePhotos checkbox
  mustHavePhotos: true

  showSearch: true
  showFeedX: false
  showHistoryX: false

  onboardingPics: true
  onboardingProfileInfo: false
  onboardingStatusUpdated: (->
    # We need this as a hack becauseo nboardingPics does not update properly
    # when it's a property for some reason.
    @set('onboardingPics', not @appGet('user.has_onboarded'))
  ).observes('controllers.application.user.has_onboarded')

  # TODO(daddy): This code is duplicated in main-feed-view because 
  # I suck.
  homeUnpaidDates: (->
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

  numYouPokedNoOffer: (->
    youPoked = @appGet('usersByCategory.you_poked')
    return 0 unless youPoked?
    ret = {}
    ret.proposedOffer = []
    ret.noOffer = []
    for pokedUser in youPoked
      if pokedUser?.poke_data?.poke_proposal?
        ret.proposedOffer.push(pokedUser)
      else
        ret.noOffer.push(pokedUser)
    return ret.noOffer.length
  ).property('controllers.application.usersByCategory.you_poked')

  numUsersInFeed: (->
    unpaidDates = @get('homeUnpaidDates.youNeedToPay')?.length ? 0
    unreviewedDates = @appGet('usersByCategory.past_unreviewed_dates')?.length ? 0
    numYouPokedNoOffer = @get('numYouPokedNoOffer')
    numPokedYou = @appGet('usersByCategory.poked_you')?.length ? 0
    numPins = @appGet('usersByCategory.user_likes')?.length ? 0
    numHaveBidOnYou = @appGet('usersByCategory.have_bid_on_you')?.length ? 0

    numUsersRaw = (numPins + numHaveBidOnYou + unpaidDates + unreviewedDates +
      numYouPokedNoOffer + numPokedYou)
    if numUsersRaw > 0
      return numUsersRaw
    else
      return 0
  ).property('controllers.application.usersByCategory', 'homeUnpaidDates',
             'numYouPokedNoOffer', 'numPokedYou')

  numNotificationsToShow: (->
    self = this
    numUsersInFeed = self.get('numUsersInFeed') ? 0
    numNotificationsSeen = self.appGet('user.num_notifications') ? 0
    if numUsersInFeed > numNotificationsSeen
      return numUsersInFeed - numNotificationsSeen
    else if numUsersInFeed < numNotificationsSeen
      SimpleData.patchUser(self.appGet('user.id'), {num_notifications: numUsersInFeed})
      .then((new_user) ->
        self.appSet('user.num_notifications', new_user.num_notifications)
      )
    return ''
  ).property('numUsersInFeed', 'controllers.application.user.num_notifications')

  actions:
    searchWithCriteria: ->
      self = this
      zip_code = self.get('searchZipCode')
      unless zip_code?.length is 5
        zip_code = null

      sex = self.get('selectedSearchSex')
      if sex is '-'
        sex = null

      orientation = self.get('selectedSearchOrientation')
      if orientation is '-'
        orientation = null        

      mustHavePhotos = self.get('mustHavePhotos')

      SimpleData.searchWithCriteria({zip_code, sex, orientation, photos: mustHavePhotos})
      .then(
        (res) ->
          for userResult in res
            userResult.photos = userResult.photos.filter(
              (x) -> x.photo_position?
            ).sort(
              (a,b) -> a.photo_position - b.photo_position
            )
          Ember.run(-> self.set('userResults', res))
      )

    selectUser: (selectedUserObj, userIndex, userList) ->
      # TODO(daddy): Make this open a modal or route with the FULL user's 
      # profile info.
      self = this
      self.send('openModelModal', 'profile-drilldown', {userIndex, selectedUserObj, userList},
            'profile-drilldown')
      console.log('TODO(daddy): Make clicking open full user profile.')

    bidButtonPressed: (userResultObj, userResultList, userIndex) ->
      self = this
      console.log(userResultObj + ' ' + userResultList + ' ' + userIndex)
      this.send('openModelModal', 'bid-info-modal', {
        senderObj: self.appGet('user')
        receiverObj: userResultObj
        userResultList
        otherUserIndex: userIndex
      })

    unlikeButtonPressed: (userResultObj, userResultList, userIndex) ->
      this.send('cancelBidButtonPressed', userResultObj, userResultList, userIndex)

    pinButtonPressed: (userObj) ->
      self = this
      pinButtonSelector = ('.home__single-result-container[user-id="' +
                           userObj.id+'"] .home-search__pin-button')
      if userObj.is_pinned
        Ember.$(pinButtonSelector)
          .css("background-color", GREY)
        this.send('cancelBidButtonPressed', userObj)

        userObj.is_pinned = false
      else
        Ember.$(pinButtonSelector)
          .css("background-color", PINK)

        SimpleData.likeUser(self.appGet('user.id'), userObj.id)
        .then(
          (res) ->
            self.send('updateBiddiesAndOffers', null)
            if res.success
              console.log('Like was successful for id: ' + userObj?.id)
            else
              console.log('Like failed (' + res.message_key + '): ' + res.message)
              self.send('openModalWithMessage', res.message, res.message_key)
          (err) -> console.log('PROBLEM LIKING USER with id' + userObj?.id +
                               ': ' + err.statusText)
        )
        userObj.is_pinned = true
      return false

    pokeButtonPressed: (userObj) ->
      self = this
      pokeButtonSelector = ('.home__single-result-container[user-id="' +
                            userObj.id + '"] .home-search__poke-button')
      if userObj.is_poked
        Ember.$(pokeButtonSelector)
          .css("background-color", GREY)

        SimpleData.postPath('pokes/cancel/'+self.appGet('user.id')+'/', {
          'sender_id': self.appGet('user.id')
          'receiver_id': userObj.id
        })
        .then(
          (res) ->
            self.send('updateBiddiesAndOffers', null)
            if res.success
              console.log('Like was successful for id: ' + userObj?.id)
            else
              console.log('Like failed (' + res.message_key + '): ' + res.message)
              self.send('openModalWithMessage', res.message, res.message_key)
          (err) -> console.log('PROBLEM LIKING USER with id' + userObj?.id +
                               ': ' + err.statusText)
        )
        userObj.is_poked = false
      else
        Ember.$(pokeButtonSelector)
          .css("background-color", BLUE)

        SimpleData.postPath('pokes/create/'+self.appGet('user.id')+'/', {
          'receiver_id': userObj.id
        })
        .then(
          (res) ->
            self.send('updateBiddiesAndOffers', null)
            if res.success
              console.log('Like was successful for id: ' + userObj?.id)
            else
              console.log('Like failed (' + res.message_key + '): ' + res.message)
              self.send('openModalWithMessage', res.message, res.message_key)
          (err) -> console.log('PROBLEM LIKING USER with id' + userObj?.id +
                               ': ' + err.statusText)
        )
        userObj.is_poked = true
      return false

    # Onboarding modal shit
    closeOnboardingPics: ->
      self = this
      Ember.$('.app__modal-content-container').fadeOut()
      Ember.$('.app__modal-overlay').fadeOut({complete:
        ->
          self.set('onboardingPics', false)
      })

    # Tab shit (to be deleted)
    searchButtonPressed: ->
      self = this
      self.set('showSearch', true)
      self.set('showFeedX', false)
      self.set('showHistoryX', false)
      $(window).scrollTop(0)

    feedXButtonPressed: ->
      self = this
      self.set('showSearch', false)
      self.set('showFeedX', true)
      self.set('showHistoryX', false)

      numUsersInFeed = self.get('numUsersInFeed') ? 0
      SimpleData.patchUser(self.appGet('user.id'), {num_notifications: numUsersInFeed})
      .then((new_user) ->
        self.set('user.num_notifications', new_user.num_notifications)
      )
      $(window).scrollTop(0)

    historyXButtonPressed: ->
      self = this
      self.set('showSearch', false)
      self.set('showFeedX', false)
      self.set('showHistoryX', true)
      $(window).scrollTop(0)

    # TODO(daddy): Move all this logic into components when we implement cards
    acceptButtonPressed: (senderObj) ->
      self = this
      SimpleData.acceptBid(
        self.appGet('user').id,
        senderObj.id,
        0 # TODO(daddy): Let them CHOOSE the time and place index..
      ).then(
        (res) ->
          self.send('updateBiddiesAndOffers', null)
        (err) -> 
          console.log('Error deleting bid: ' + err.statusText)
      )

    # TODO(daddy): Move all this logic into components when we implement cards
    rejectButtonPressed: (senderObj) ->
      self = this
      SimpleData.cancelBid(
        self.appGet('user').id,
        senderObj.id
      ).then(
        (res) ->
          self.send('updateBiddiesAndOffers', null)
        (err) -> 
          console.log('Error deleting bid: ' + err.statusText)
      )

    # TODO(daddy): Move all this logic into components when we implement cards
    modifyBidButtonPressed: (receiverObj) ->
      self = this
      this.send('openModelModal', 'bid-info-modal', {
        senderObj: self.appGet('user')
        receiverObj: receiverObj
      })

    # TODO(daddy): Move all this logic into components when we implement cards
    cancelBidButtonPressed: (receiverObj) ->
      self = this
      SimpleData.cancelBid(
        self.appGet('user').id,
        receiverObj.id
      ).then(
        (res) ->
          self.send('updateBiddiesAndOffers', null)
        (err) -> 
          console.log('Error deleting bid: ' + err.statusText)
      )

    updateBiddiesAndOffers: (reschedule_ms) ->
      self = this
      func = ->
        self.send('updateBiddiesAndOffers', reschedule_ms)

      SimpleData.getPath('login/')
      .then(
        (res) ->
          if (res.user?.id?)
            Ember.run(->
              self.appSet('bidsByCategory', res.bids_by_category)
              self.appSet('usersByCategory', res.users_by_category)
              self.appSet('allBids', res.all_bids)
            )
          else
            console.log('User is not logged in.')
          if reschedule_ms?
            setTimeout(func, reschedule_ms)
        (err) ->
          console.log('Error fetching model home: ' + err.statusText)
          return null
      )
)

`export default HomeController`
