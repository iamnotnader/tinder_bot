`import Ember from 'ember'`
`import SimpleData from '../utils/simple-data';`

UserPreviewCompComponent = Ember.Component.extend(
  sharedFields: null

  youBidOnThisUser: (->
    main_user_is_sender = false
    if @get('userObj.bid_data')?.sender_id is @get('mainUser.id')
      main_user_is_sender = true

    if main_user_is_sender and @get('userObj.bid_data')?.bid_state is 'outstanding'
      return true
    return false
  ).property('userObj.bid_data.bid_state')

  youAskedThisUser: (->
    # Bids take priority over pokes.
    if @get('userObj.bid_data')?
      return false
    main_user_is_sender = false
    if @get('userObj.poke_data')?.sender_id is @get('mainUser.id')
      main_user_is_sender = true

    if main_user_is_sender and @get('userObj.poke_data')?.bid_state is 'poke_outstanding'
      return true
    return false
  ).property('userObj.poke_data.bid_state')

  userIsUntouched: (->
    if @get('userObj.bid_data')? or @get('youBidOnThisUser') or @get('youAskedThisUser')
      return false
    return true
  ).property('userObj.bid_data', 'youBidOnThisUser', 'youAskedThisUser')

  showUserInSearch: (->
    if @get('userObj.bid_data')? and not (@get('youBidOnThisUser') or @get('youAskedThisUser'))
      return false
    return true
  ).property('userObj.bid_data', 'youBidOnThisUser', 'youAskedThisUser')

  numDates: (->
    @get('userObj')?.stats_for_user?.num_dates
  ).property('userObj')

  verySatisfiedNum: (->
    @get('userObj')?.stats_for_user?.very_satisfied
  ).property('userObj')

  unsatisfiedDateNum: (->
    @get('userObj')?.stats_for_user?.unsatisfied_date
  ).property('userObj')

  noShowNum: (->
    @get('userObj')?.stats_for_user?.no_show
  ).property('userObj')

  noPayNum: (->
    @get('userObj')?.stats_for_user?.no_pay
  ).property('userObj')

  veryComfortableNum: (->
    @get('userObj')?.stats_for_user?.very_comfortable
  ).property('userObj')

  uncomfortableDateNum: (->
    @get('userObj')?.stats_for_user?.uncomforable_date
  ).property('userObj')

  differentFromPicsNum: (->
    @get('userObj')?.stats_for_user?.looked_worse_than_pics
  ).property('userObj')

  suggestedBidAmount: (->
    return Math.floor(Math.random()*10)*50+50
  ).property()

  isOnline: (->
    @get('userObj')?.is_online
  ).property('userObj')

  didInsertElement: ->
    self = this
    userObj = self.get('userObj')
    self.$().hover(
      ->
        unless (userObj?.is_pinned or
          self.$('.user-preview-comp__summary-stat-container').hasClass('hide-on-hover')
        )
          self.$('.user-preview-comp__summary-stat-container').toggleClass('hide-on-hover')
          self.$('.user-preview-comp__buttons-container').toggleClass('hide-on-hover')
      , ->
        unless (userObj?.is_pinned or 
          self.$('.user-preview-comp__buttons-container').hasClass('hide-on-hover')
        )
          self.$('.user-preview-comp__buttons-container').toggleClass('hide-on-hover')
          self.$('.user-preview-comp__summary-stat-container').toggleClass('hide-on-hover')
    )
    if self.get('userObj.is_pinned')
      self.$('.user-preview-comp__buttons-container').toggleClass('hide-on-hover')
      self.$('.user-preview-comp__summary-stat-container').toggleClass('hide-on-hover')

  actions:
    picClicked: ->
      this.sendAction('picClickHandler', @get('userObj'), @get('userIndex'), @get('userList'))

    updateAfterBid: ->
      self.sendAction('updateHook', null)

    userPreviewBidOrAskButtonPressed: (eventType)->
      self = this
      sharedFields = @get('sharedFields')
      senderObj = @get('mainUser')
      receiverObj = @get('userObj')
      updateHook = @get('updateHook')
      openModelModal = @get('openModelModal')
      self.sendAction('openModelModal', 'bid-ask-modal',
          {sharedFields, senderObj, receiverObj, updateHook, openModelModal, eventType},
          'bid-ask-modal'
      )

    userPreviewCancelBidButtonPressed: ->
      self = this
      SimpleData.cancelBid(
        self.get('mainUser.id'),
        self.get('userObj.id')
      ).then(
        (res) ->
          if res.success
            self.sendAction('updateHook', null)
            self.set('userObj.bid_data', null)
          else
            console.log('ERROR: ' + res.message)
        (err) -> 
          console.log('Error deleting bid: ' + err.statusText)
      )

    userPreviewCancelAskButtonPressed: ->
      self = this
      SimpleData.postPath('pokes/cancel/'+self.get('mainUser.id')+'/', {
        sender_id: self.get('mainUser.id')
        receiver_id:  self.get('userObj.id')
      })
      .then(
        (res) ->
          if res?.success
            self.sendAction('updateHook', null)
            self.set('userObj.poke_data',  null)
            self.send('close')
          else
            console.log('Error bidding on user ' +
                self.get('userObj.first_name') + ' ' + res.message)
      )

)

`export default UserPreviewCompComponent`
