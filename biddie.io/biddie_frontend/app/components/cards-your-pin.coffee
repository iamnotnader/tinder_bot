`import Ember from 'ember'`
`import SimpleData from '../utils/simple-data';`

BID_BOX_PLACEHOLDER = "$0 up to $9999"

CardsYourPinComponent = Ember.Component.extend(
  classNames: "cards-your-pin__outer-div"
  receiverObj: null
  updateHook: null
  openModalWithMessage: null

  showDateTimePickers: false

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
          (@get('isValidFieldsSet')(@get('fieldsSet1')) or 
           @get('isValidFieldsSet')(@get('fieldsSet2')) or 
           @get('isValidFieldsSet')(@get('fieldsSet3')))
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
        self.sendAction('openModalWithMessage', 'You missed a field in your bid!')
        return

      # Send all the bid information
      timesAndPlacesList = []
      if @get('isValidFieldsSet')(@get('fieldsSet1'))
        @get('fieldsSet1')['place_name'] = @get('sharedFields.placeSelected')
        timesAndPlacesList.push(@get('fieldsSet1'))
      if @get('isValidFieldsSet')(@get('fieldsSet2'))
        @get('fieldsSet2')['place_name'] = @get('sharedFields.placeSelected')
        timesAndPlacesList.push(@get('fieldsSet2'))
      if @get('isValidFieldsSet')(@get('fieldsSet3'))
        @get('fieldsSet3')['place_name'] = @get('sharedFields.placeSelected')
        timesAndPlacesList.push(@get('fieldsSet3'))

      SimpleData.postBid(
        self.get('senderObj.id'),
        self.get('receiverObj.id'),
        self.get('sharedFields.amountToBid'),
        timesAndPlacesList
      ).then(
        (res) ->
          if res?.success
            console.log('Successfully bid on user: ' + self.get('receiverObj.first_name'))
            self.sendAction('updateHook')
          else
            console.log('Error bidding on user ' + self.get('receiverObj.first_name') +
                        ' ' + res.message)
            self.sendAction('openModalWithMessage', res.message)
      )

    unpinButtonPressed: ->
      self = this
      SimpleData.cancelBid(
        self.get('senderObj.id'),
        self.get('receiverObj.id')
      ).then(
        (res) ->
          if res?.success
            console.log('Successfully unpinned user: ' + self.get('receiverObj.first_name'))
            self.sendAction('updateHook')
          else
            console.log('Error unpinning user ' + self.get('receiverObj.first_name') +
                        ' ' + res.message)
            self.sendAction('openModalWithMessage', res.message)
        (err) -> 
          console.log('Error unpinning user ' + self.get('receiverObj.first_name') +
                      ' ' + res.message)
          self.sendAction('openModalWithMessage', res.message)
      )
)

`export default CardsYourPinComponent`
