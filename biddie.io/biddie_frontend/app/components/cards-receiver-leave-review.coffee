`import Ember from 'ember'`
`import CardsBidOnYouComponent from './cards-bid-on-you'`
`import SimpleData from '../utils/simple-data';`

CardsReceiverLeaveReviewComponent = CardsBidOnYouComponent.extend(
  didShowUp: null
  howComfortableWasDate: null
  didDateLookWorseThanPics: null  

  questionTextList: [
    "Did you show up to the date?"
    "How comfortable did your date make you feel?"
    "Did your date look significantly worse than their pictures?"
    "Your answers will not affect your compensation or your reputation on the site 
     in any way, and we don't reveal your responses to your date-- so be honest!"
  ]

  actions:
    submitButtonPressed: ->
      self = this
      didShowUp = self.get('didShowUp')
      howComfortableWasDate = self.get('howComfortableWasDate')
      didDateLookWorseThanPics = self.get('didDateLookWorseThanPics')
      questionTextList = self.get('questionTextList')

      unless (didShowUp? and howComfortableWasDate? and
          didDateLookWorseThanPics? and questionTextList?
      )
        console.log('Forgot to answer a questoin!')
        self.sendAction('openModalWithMessage', 'You forgot to answer a questoin!')
        return

      SimpleData.postPath('leave_review/'+self.get('senderObj.id')+'/', {
        'receiver_id': self.get('receiverObj.id')
        'did_show_up': didShowUp
        'comfort_rating': howComfortableWasDate
        'looked_worse_than_pics': didDateLookWorseThanPics
        'question_text': questionTextList
      }).then(
        (res) ->
          if res?.success
            console.log('Successfully reviewing user: ' + self.get('receiverObj.first_name'))
            self.sendAction('updateHook')
          else
            console.log('Error reviewing user ' + self.get('receiverObj.first_name') +
                        ' ' + res.message)
            self.sendAction('openModalWithMessage', res.message)
        (err) ->
          console.log('Error deleting bid: ' + err.statusText)
          self.sendAction('openModalWithMessage', res.message)
      )
)

`export default CardsReceiverLeaveReviewComponent`
