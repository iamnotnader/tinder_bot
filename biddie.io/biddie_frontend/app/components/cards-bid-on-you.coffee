`import Ember from 'ember'`
`import SimpleData from '../utils/simple-data';`

CardsBidOnYouComponent = Ember.Component.extend(
  classNames: "cards-your-pin__outer-div"
  receiverObj: null
  updateHook: null
  openModalWithMessage: null

  timesAndPlaces: (->
    timesAndPlaces = @get('receiverObj.bid_data.times_and_places_list')
    return unless timesAndPlaces?
    listToReturn = []
    for timeAndPlace, index in timesAndPlaces
      [year, month, day, weekday] = timeAndPlace.selectedDate.split('-')
      minute = timeAndPlace.selectedMinute
      if minute < 10
        minute = '0' + minute

      listToReturn.push({
        hour: timeAndPlace.selectedHour
        minute
        amOrPm: timeAndPlace.selectedAmOrPm
        duration: timeAndPlace.selectedDuration
        year
        month
        day
        weekday
        index
      })
    listToReturn
  ).property('receiverObj.bid_data.times_and_places_list')

  actions:
    cancelBidButtonPressed: ->
      self = this
      SimpleData.cancelBid(
        self.get('senderObj.id'),
        self.get('receiverObj.id')
      ).then(
        (res) ->
          if res?.success
            console.log('Successfully rejecting user: ' + self.get('receiverObj.first_name'))
            self.sendAction('updateHook')
          else
            console.log('Error rejecting user ' + self.get('receiverObj.first_name') +
                        ' ' + res.message)
            self.sendAction('openModalWithMessage', res.message)
        (err) -> 
          console.log('Error rejecting user ' + self.get('receiverObj.first_name') +
                      ' ' + res.message)
          self.sendAction('openModalWithMessage', res.message)
      )

    # TODO(daddy): Move all this logic into components when we implement cards
    acceptOfferButtonPressed: (index) ->
      self = this
      SimpleData.acceptBid(
        self.get('senderObj.id'),
        self.get('receiverObj.id'),
        index
      ).then(
        (res) ->
          if res?.success
            console.log('Successfully rejecting user: ' + self.get('receiverObj.first_name'))
            self.sendAction('updateHook')
          else
            console.log('Error rejecting user ' + self.get('receiverObj.first_name') +
                        ' ' + res.message)
            self.sendAction('openModalWithMessage', res.message)
        (err) ->
          console.log('Error deleting bid: ' + err.statusText)
          self.sendAction('openModalWithMessage', res.message)
      )
)

`export default CardsBidOnYouComponent`
