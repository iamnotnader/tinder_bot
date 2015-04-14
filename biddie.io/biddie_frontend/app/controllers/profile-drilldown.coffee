`import Ember from 'ember';`
`import BaseController from './base-controller';`
`import SimpleData from '../utils/simple-data';`
`import ConstantValues from '../utils/constant-values';`


ProfileDrilldownController = BaseController.extend(
  needs: ['application', 'home']
  sharedFields: {
    fieldsSet1: {}
    fieldsSet2: {}
    fieldsSet3: {}
  }
  # selectedUserObj, userIndex, and userList all come from the model.

  # This is a hack to call a function in our component from our
  # controller, which is something you generally shouldn't do in ember.
  # Sigh... When either of these is set to true, they trigger the next/previous
  # photo to be shown respectively.
  nextPhotoBool: false
  prevPhotoBool: false

  # TODO(daddy): Need to implement this shit in the backend and get the values
  # here.
  numDates: (->
    @get('selectedUserObj')?.stats_for_user?.num_dates
  ).property('selectedUserObj')

  verySatisfiedNum: (->
    @get('selectedUserObj')?.stats_for_user?.very_satisfied
  ).property('selectedUserObj')

  unsatisfiedDateNum: (->
    @get('selectedUserObj')?.stats_for_user?.unsatisfied_date
  ).property('selectedUserObj')

  noShowNum: (->
    @get('selectedUserObj')?.stats_for_user?.no_show
  ).property('selectedUserObj')

  noPayNum: (->
    @get('selectedUserObj')?.stats_for_user?.no_pay
  ).property('selectedUserObj')

  veryComfortableNum: (->
    @get('selectedUserObj')?.stats_for_user?.very_comfortable
  ).property('selectedUserObj')

  uncomfortableDateNum: (->
    @get('selectedUserObj')?.stats_for_user?.uncomforable_date
  ).property('selectedUserObj')

  differentFromPicsNum: (->
    @get('selectedUserObj')?.stats_for_user?.looked_worse_than_pics
  ).property('selectedUserObj')

  heightFeet: (->
    return 0 unless @get('selectedUserObj.height_inches')
    return Math.floor(@get('selectedUserObj.height_inches') / 12)
  ).property('selectedUserObj')
  heightInches: (->
    return 0 unless @get('selectedUserObj.height_inches')
    return Math.floor(@get('selectedUserObj.height_inches') % 12)
  ).property('selectedUserObj')
  userOrientation: (->
    return unless @get('selectedUserObj.orientation')
    ConstantValues.textOrientationChoices[@get('selectedUserObj.orientation')]
  ).property('selectedUserObj')
  userSex: (->
    return unless @get('selectedUserObj.sex')
    ConstantValues.textSexChoices[@get('selectedUserObj.sex')]
  ).property('selectedUserObj')
  userEthnicity: (->
    return unless @get('selectedUserObj.ethnicity')
    ConstantValues.textEthnicityChoices[@get('selectedUserObj.ethnicity')]
  ).property('selectedUserObj')
  userIvyLeague: (->
    return unless @get('selectedUserObj.ivy_league')
    if @get('selectedUserObj.ivy_league')
      return 'yes'
    else
      return 'no'
  ).property('selectedUserObj')

  actions:
    nextProfileButtonPressed: ->
      userIndex = @get('userIndex')
      userList = @get('userList')
      return unless userIndex? and userList?
      newUserIndex = (userIndex + 1) % userList.length
      @set('selectedUserObj', userList[newUserIndex])
      @set('userIndex', newUserIndex)

    prevProfileButtonPressed: ->
      userIndex = @get('userIndex')
      userList = @get('userList')
      return unless userIndex? and userList?
      newUserIndex = (userIndex + userList.length - 1) % userList.length
      @set('selectedUserObj', userList[newUserIndex])
      @set('userIndex', newUserIndex)

    nextPhotoButtonPressed: ->
      @set('nextPhotoBool', true)

    prevPhotoButtonPressed: ->
      @set('prevPhotoBool', true)

    profileDrilldownAskButtonPressed: (eventType) ->
      self = this
      sharedFields = @get('sharedFields')
      senderObj = self.appGet('user')
      receiverObj = @get('selectedUserObj')
      updateHook = 'updateBiddiesAndOffers'
      openModelModal = 'openModelModal'
      self.send('openModelModal', 'bid-ask-modal',
          {sharedFields, senderObj, receiverObj, updateHook, openModelModal, eventType},
          'bid-ask-modal'
      )

    profileDrilldownBidButtonPressed: (eventType) ->
      self = this
      sharedFields = @get('sharedFields')
      senderObj = self.appGet('user')
      receiverObj = @get('selectedUserObj')
      updateHook = 'updateBiddiesAndOffers'
      openModelModal = 'openModelModal'
      self.send('openModelModal', 'bid-ask-modal',
          {sharedFields, senderObj, receiverObj, updateHook, openModelModal, eventType},
          'bid-ask-modal'
      )

    profileDrilldownCancelBidButtonPressed: ->
      self = this
      SimpleData.cancelBid(
        self.appGet('user.id'),
        self.get('selectedUserObj.id')
      ).then(
        (res) ->
          if res.success
            self.controllerFor('home').send('updateBiddiesAndOffers', null)
            self.set('selectedUserObj.bid_data', null)
          else
            console.log('ERROR: ' + res.message)
        (err) -> 
          console.log('Error deleting bid: ' + err.statusText)
      )

    profileDrilldownCancelAskButtonPressed: ->
      self = this
      SimpleData.postPath('pokes/cancel/'+self.appGet('user.id')+'/', {
        sender_id: self.appGet('user.id'),
        receiver_id: self.get('selectedUserObj.id')
      })
      .then(
        (res) ->
          if res?.success
            self.controllerFor('home').send('updateBiddiesAndOffers', null)
            self.set('selectedUserObj.poke_data',  null)
          else
            console.log('Error unasking on user ' +
                self.get('selectedUserObj.first_name') + ' ' + res.message)
      )

    close: () ->
      return this.send('closeModal', 'profile-drilldown')

)

`export default ProfileDrilldownController`