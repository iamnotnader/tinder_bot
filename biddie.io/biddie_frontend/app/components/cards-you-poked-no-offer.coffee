`import Ember from 'ember'`
`import CardsYourPinComponent from './cards-your-pin'`
`import SimpleData from '../utils/simple-data';`

CardsYouPokedComponent = CardsYourPinComponent.extend(
  actions:
    proposeButtonPressed: ->
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

      SimpleData.postPath('pokes/add_proposal/'+self.get('senderObj.id')+'/', {
        'receiver_id':  self.get('receiverObj.id'),
        'bid_amount': self.get('sharedFields.amountToBid'),
        'times_and_places_list': timesAndPlacesList
        }
      ).then(
        (res) ->
          if res?.success
            console.log('Successfully proposed to user: ' + self.get('receiverObj.first_name'))
            self.sendAction('updateHook')
          else
            console.log('Error unpinning user ' + self.get('receiverObj.first_name') +
                        ' ' + res.message)
            self.sendAction('openModalWithMessage', res.message)
      )
)

`export default CardsYouPokedComponent`