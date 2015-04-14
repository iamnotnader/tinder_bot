`import Ember from 'ember';`
`import BaseController from './base-controller';`
`import SimpleData from '../utils/simple-data';`
`import ConstantValues from '../utils/constant-values';`

BID_BOX_PLACEHOLDER = "0 up to 9999"

ProfileDrilldownController = BaseController.extend(
  needs: ['application', 'home']

  eventIsBid: (->
    return @get('eventType') is 'bid'
  ).property('eventType')

  eventIsAsk: (->
    return @get('eventType') is 'ask'
  ).property('eventType')

  eventIsModifyBid: (->
    return @get('eventType') is 'modifyBid'
  ).property('eventType')

  eventIsModifyAsk: (->
    return @get('eventType') is 'modifyAsk'
  ).property('eventType')

  firstFieldIsValid: (->
    return @get('sharedFields.fieldsSet1.seconds_since_epoch')?
  ).property('isValidFieldsSet', 'sharedFields.fieldsSet1.seconds_since_epoch')

  bidBoxPlaceholder: BID_BOX_PLACEHOLDER

  bidIsValid: (->
    amountToBid = @get('sharedFields.amountToBid')
    unless amountToBid?
      return false
    if(/^(\-|\+)?([0-9]+|Infinity)$/.test(amountToBid) and
       not isNaN(parseInt(amountToBid))
    )
      return true
    return false
  ).property('sharedFields.amountToBid')

  placeIsValid: (->
    return (@get('sharedFields.placeSelected')? and
            @get('sharedFields.placeSelected') isnt '')
  ).property('sharedFields.placeSelected')

  wipeInvalidBids: (->
    if @get('sharedFields.amountToBid') is ''
      return
    unless @get('bidIsValid')
      unless isNaN(parseInt(@get('sharedFields.amountToBid')))
        @set('sharedFields.amountToBid',
             parseInt(@get('sharedFields.amountToBid')).toString()
        )
      else
        @set('sharedFields.amountToBid', '')
  ).observes('sharedFields.amountToBid')

  isValidHour: (fieldsSet) =>
      selectedHour = fieldsSet?.selectedHour
      unless selectedHour?
        return false
      selectedHour = parseInt(selectedHour)
      if (selectedHour? and (not isNaN(selectedHour)) and
          selectedHour >= 1 and selectedHour <= 12)
        return true
      return false

  isValidFieldsSet: (->
    (fieldsSet) =>
      return (@get('isValidHour')(fieldsSet) and @get('isValidMinute')(fieldsSet) and
        fieldsSet.seconds_since_epoch? and fieldsSet.seconds_since_epoch > 0)
  ).property()

  isValidMinute: (fieldsSet) =>
    selectedMinute = fieldsSet?.selectedMinute
    unless selectedMinute?
      return false
    selectedMinute = parseInt(selectedMinute)
    if (selectedMinute? and (not isNaN(selectedMinute)) and
        selectedMinute >= 0 and selectedMinute <= 59)
      return true

  bidIsReady: (->
    =>
      unless (@get('bidIsValid') and @get('placeIsValid') and
          (@get('isValidFieldsSet')(@get('sharedFields.fieldsSet1')) or 
           @get('isValidFieldsSet')(@get('sharedFields.fieldsSet2')) or 
           @get('isValidFieldsSet')(@get('sharedFields.fieldsSet3')))
      )
        return false
      return true
  ).property()

  actions:
    bidBoxFocused: ->
      @set('bidBoxPlaceholder', '')

    bidBoxUnfocused: ->
      @set('bidBoxPlaceholder', BID_BOX_PLACEHOLDER)

    addDatesAndTimes: ->
      @set('showDateTimePickers', true)

    bidButtonPressed: ->
      self = this
      unless @get('bidIsReady')()
        self.send('openModalWithMessage', 'You missed a field in your bid!')
        return

      # Send all the bid information
      timesAndPlacesList = []
      if @get('isValidFieldsSet')(@get('sharedFields.fieldsSet1'))
        @get('sharedFields.fieldsSet1')['place_name'] = @get('sharedFields.placeSelected')
        timesAndPlacesList.push(@get('sharedFields.fieldsSet1'))
      if @get('isValidFieldsSet')(@get('sharedFields.fieldsSet2'))
        @get('sharedFields.fieldsSet2')['place_name'] = @get('sharedFields.placeSelected')
        timesAndPlacesList.push(@get('sharedFields.fieldsSet2'))
      if @get('isValidFieldsSet')(@get('sharedFields.fieldsSet3'))
        @get('sharedFields.fieldsSet3')['place_name'] = @get('sharedFields.placeSelected')
        timesAndPlacesList.push(@get('sharedFields.fieldsSet3'))

      SimpleData.postBid(
        self.get('senderObj.id'),
        self.get('receiverObj.id'),
        self.get('sharedFields.amountToBid'),
        timesAndPlacesList
      ).then(
        (res) ->
          if res?.success
            console.log('Successfully bid on user: ' + self.get('receiverObj.first_name'))
            self.controllerFor('home').send('updateBiddiesAndOffers', null)
            if self.get('receiverObj.bid_data')?
              self.set('receiverObj.bid_data.bid_state', 'outstanding')
            else
              self.set('receiverObj.bid_data',
                {
                  sender_id: self.get('senderObj.id'),
                  receiver_id: self.get('receiverObj.id'), 
                  bid_state: 'outstanding'
                }
              )
            self.send('close')
          else
            console.log('Error bidding on user ' +
                self.get('receiverObj.first_name') + ' ' + res.message)
            self.send('openModalWithMessage', res.message)
      )

    askButtonPressed: ->
      self = this
      unless @get('bidIsReady')()
        self.send('openModalWithMessage', 'You missed a field in your bid!')
        return

      # Send all the bid information
      timesAndPlacesList = []
      if @get('isValidFieldsSet')(@get('sharedFields.fieldsSet1'))
        @get('sharedFields.fieldsSet1')['place_name'] = @get('sharedFields.placeSelected')
        timesAndPlacesList.push(@get('sharedFields.fieldsSet1'))
      if @get('isValidFieldsSet')(@get('sharedFields.fieldsSet2'))
        @get('sharedFields.fieldsSet2')['place_name'] = @get('sharedFields.placeSelected')
        timesAndPlacesList.push(@get('sharedFields.fieldsSet2'))
      if @get('isValidFieldsSet')(@get('sharedFields.fieldsSet3'))
        @get('sharedFields.fieldsSet3')['place_name'] = @get('sharedFields.placeSelected')
        timesAndPlacesList.push(@get('sharedFields.fieldsSet3'))

      SimpleData.postPath('pokes/add_proposal/'+self.get('senderObj.id')+'/', {
        'receiver_id':  self.get('receiverObj.id'),
        'bid_amount': self.get('sharedFields.amountToBid'),
        'times_and_places_list': timesAndPlacesList
        }
      ).then(
        (res) ->
          if res?.success
            console.log('Successfully bid on user: ' + self.get('receiverObj.first_name'))
            self.controllerFor('home').send('updateBiddiesAndOffers', null)
            if self.get('receiverObj.poke_data')?
              self.set('receiverObj.poke_data.bid_state', 'poke_outstanding')
            else
              self.set('receiverObj.poke_data',
                {
                  sender_id: self.get('senderObj.id'),
                  receiver_id: self.get('receiverObj.id'), 
                  bid_state: 'poke_outstanding'
                }
              )
            self.send('close')
          else
            console.log('Error bidding on user ' +
                self.get('receiverObj.first_name') + ' ' + res.message)
            self.send('openModalWithMessage', res.message)
      )

    noClose: ->
      console.log('noClose called.')
      # TODO(daddy): Disgusting hack to prevent action from bubbling
      # and modal from closing. For some reason returning true didn't work..
      @set('dontclose', true)
      return false

    close: () ->
      console.log('close called.')
      # TODO(daddy): Disgusting hack to prevent action from bubbling
      # and modal from closing. For some reason returning true didn't work..
      unless @get('dontclose')
        return this.send('closeModal', 'bid-ask-modal')
      else
        @set('dontclose', false)

)

`export default ProfileDrilldownController`