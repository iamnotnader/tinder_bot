`import Ember from 'ember'`
`import CardsBidOnYouComponent from './cards-bid-on-you'`
`import SimpleData from '../utils/simple-data';`

CardsWaitingOnPaymentComponent = CardsBidOnYouComponent.extend(
  # TODO(daddy): Move all this logic into components when we implement cards
  payMeButtonPressed: (otherUserObj) ->
    self = this
    bid_amount = parseInt(otherUserObj.bid_data.bid_amount)
    bid_amount_cents = bid_amount*100
    handler = StripeCheckout.configure({
      key: 'pk_test_6pRNASCoBOKtIshFeQd4XMUh', # TODO(daddy): get a real API key.
      image: '/images/logo_pink.svg',
      email: self.get('senderObj.email'),
      token: (payment_token) ->
        SimpleData.payMe(self.get('senderObj.id'), otherUserObj.id, payment_token).then(
          (res) ->
            if res?.success
              console.log('Successfully paid for user user: ' + 
                self.get('receiverObj.first_name')
              )
              self.sendAction('updateHook')
            else
              console.log('Error paying for user ' + self.get('receiverObj.first_name') +
                          ' ' + res.message)
              self.sendAction('openModalWithMessage', res.message)
          (err) -> 
            console.log('Error paying for user ' + self.get('receiverObj.first_name') +
                        ' ' + res.message)
            self.sendAction('openModalWithMessage', res.message)
        )
    })
    handler.open({
      name: 'biddie.io',
      description: '$'+bid_amount+' to date this biddie.',
      amount: bid_amount_cents,
      currency: 'usd'
    })
)

`export default CardsWaitingOnPaymentComponent`