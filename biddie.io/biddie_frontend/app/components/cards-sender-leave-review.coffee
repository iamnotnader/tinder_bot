`import Ember from 'ember'`
`import CardsBidOnYouComponent from './cards-bid-on-you'`
`import SimpleData from '../utils/simple-data';`

CardsSenderLeaveReviewComponent = CardsBidOnYouComponent.extend(
  didDateShowUp: null
  wantsToPay: null
  didDateLookWorseThanPics: null
  biddieRating: null

  questionTextList: [
    "Your answers will not affect your reputation on the site 
     in any way, and we don't reveal your responses to your date-- so be honest!"
    "Did your biddie show up?"
    "Would you like to pay your biddie?"
    "Did your biddie look significantly worse than their pictures?"
    "Rate your overall experience."
    "We will ask your date if they showed up. If they say they did and you don’t pay, \
     you will get a “no-pay” added to your profile. This will negatively affect \
     people’s willingness to date you in the future. On the other hand, developing \
     a reputation for always paying results in much cheaper and more attractive dates. \
     So pay your biddie if they showed up and you had a good time."
  ]

  actions:
    submitButtonPressed: ->
      self = this
      didDateShowUp = self.get('didDateShowUp')
      wantsToPay = self.get('wantsToPay')
      didDateLookWorseThanPics = self.get('didDateLookWorseThanPics')
      biddieRating = self.get('biddieRating')
      questionTextList = self.get('questionTextList')

      unless (didDateShowUp? and wantsToPay? and
          didDateLookWorseThanPics? and biddieRating? and questionTextList?
      )
        console.log('Forgot to answer a questoin!')
        self.sendAction('openModalWithMessage', 'You forgot to answer a questoin!')
        return

      SimpleData.postPath('leave_review/'+self.get('senderObj.id')+'/', {
        'receiver_id': self.get('receiverObj.id')
        'receiver_showed_up': didDateShowUp
        'would_like_to_pay': wantsToPay
        'looked_worse_than_pics': didDateLookWorseThanPics
        'receiver_rating': biddieRating
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

`export default CardsSenderLeaveReviewComponent`