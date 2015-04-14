`import Ember from 'ember'`
`import CardsYourPinComponent from './cards-your-pin'`
`import SimpleData from '../utils/simple-data';`

# Everything is handled by the parent class.
CardsPokedYouComponent = CardsYourPinComponent.extend(
  fieldsSet1: (->
    timesAndPlacesList = @get('receiverObj.poke_data.poke_proposal.times_and_places_list')
    return {} unless timesAndPlacesList?
    return timesAndPlacesList[0]
  ).property('receiverObj.poke_data.poke_proposal.times_and_places_list')

  fieldsSet2: (->
    timesAndPlacesList = @get('receiverObj.poke_data.poke_proposal.times_and_places_list')
    return {} unless timesAndPlacesList?
    return timesAndPlacesList[1]
  ).property('receiverObj.poke_data.poke_proposal.times_and_places_list')

  fieldsSet3: (->
    timesAndPlacesList = @get('receiverObj.poke_data.poke_proposal.times_and_places_list')
    return {} unless timesAndPlacesList?
    return timesAndPlacesList[2]
  ).property('receiverObj.poke_data.poke_proposal.times_and_places_list')

  sharedFields: (->
    pokeProposal = @get('receiverObj.poke_data.poke_proposal')
    return {amountToBid: null, placeSelected: ''} unless pokeProposal

    firstDate = pokeProposal.times_and_places_list?[0]
    return {
      amountToBid: pokeProposal.bid_amount
      placeSelected: firstDate?.place_name ? ''
    }
  ).property('receiverObj.poke_data.poke_proposal.bid_amount',
             'receiverObj.poke_data.poke_proposal.times_and_places_list.[0].place_name')

)

`export default CardsPokedYouComponent`