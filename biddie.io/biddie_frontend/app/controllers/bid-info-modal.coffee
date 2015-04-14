`import Ember from 'ember'`
`import SimpleData from '../utils/simple-data';`

BID_BOX_PLACEHOLDER = "$0 up to $9999"

BidInfoModalController = Ember.Controller.extend(
  needs: ['home']

  bidBoxPlaceholder: BID_BOX_PLACEHOLDER

  fieldsSet1: null
  fieldsSet2: null
  fieldsSet3: null

  amountToBid: null

  bidIsValid: (->
    amountToBid = @get('amountToBid')
    unless amountToBid?
      return false
    if(/^(\-|\+)?([0-9]+|Infinity)$/.test(amountToBid) and
       not isNaN(parseInt(amountToBid))
    )
      return true
    return false
  ).property('amountToBid')

  wipeInvalidBids: (->
    if @get('amountToBid') is ''
      return
    unless @get('bidIsValid')
      unless isNaN(parseInt(@get('amountToBid')))
        @set('amountToBid', parseInt(@get('amountToBid')).toString())
      else
        @set('amountToBid', '')
  ).observes('amountToBid')

  bidNotReady: (->
    unless ((@get('fieldsSet1')? or @get('fieldsSet2') or
             @get('fieldsSet3')?) and
            @get('bidIsValid'))
      return true
    return false
  ).property('fieldsSet1', 'fieldsSet2', 'fieldsSet3',
             'bidIsValid')

  actions:
    close: ->
      return this.send('closeModal')

    bidBoxFocused: ->
      @set('bidBoxPlaceholder', '')

    bidBoxUnfocused: ->
      @set('bidBoxPlaceholder', BID_BOX_PLACEHOLDER)

    bidButtonPressed: ->
      self = this
      # Send all the bid information
      timesAndPlacesList = []
      if @get('fieldsSet1')?
        timesAndPlacesList.push(@get('fieldsSet1'))
      if @get('fieldsSet2')?
        timesAndPlacesList.push(@get('fieldsSet2'))
      if @get('fieldsSet3')?
        timesAndPlacesList.push(@get('fieldsSet3'))

      SimpleData.postBid(
        self.get('model.senderObj.id'),
        self.get('model.receiverObj.id'),
        self.get('amountToBid'),
        timesAndPlacesList
      ).then(
        (res) ->
          self.get('controllers.home').send('updateBiddiesAndOffers', null)
      )

      self.send('close')
)

`export default BidInfoModalController`
