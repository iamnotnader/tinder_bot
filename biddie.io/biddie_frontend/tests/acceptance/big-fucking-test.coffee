###
IMPORTANT! This test assumes a user already exists in the database with the
following information:
username: a
password: a
zip code: 47933
###

`import Ember from 'ember';`
`import { test, asyncTest } from 'ember-qunit';`
`import startApp from '../helpers/start-app';`
`import SimpleData from 'biddie-frontend/utils/simple-data'`

App = null

module('Full motherfucking account creation and bidding flow test (MAKE THIS WORK FOREVER!).',
    setup: ->
        App = startApp();

    teardown: ->
        Ember.run(App, App.destroy)
)

_logoutLoginUserASYNC = (username, password) ->
    click('.topnav__logout')
    click('.landing__login-button')
    fillIn('.login__email-input', username)
    fillIn('.login__password-input', password)
    click('.landing__login-button')

test('Do everything.', ->
    expect(11)
    QUnit.stop()

    SimpleData.deletePath('login/', null, false)
    visit('/')
    newuser = 'newuser@biddie.io'+Math.random()
    newpass = 'newuserpassword'
    fillIn('.login__email-input', newuser)
    fillIn('.login__password-input', newpass)
    click('.landing__signup-button')

    fillIn('.home__zip-search', 47933)
    click('.home__search-button')

    andThen(->
        ok(find('.home__biddie-image').length > 0,
            'Users should show up in search.')
    )

    # Like two users.
    click('.home__biddie-bid-button:first')
    click('.home__biddie-bid-button:last')
    click('.home__likes-tab')

    andThen(->
        oldNumLikes = find('.home__biddie-image').length
        ok(oldNumLikes is 2,
            'Liked users should show up in likes tab.')
    )

    # Unlike one user.
    click('.home-biddies__unlike-button:last')
    andThen(->
        newNumLikes = find('.home__biddie-image').length
        ok(newNumLikes is 1,
            'Unliked user should disappear from likes tab.')
    )

    # Bid on the 'a' user.
    click('.home-biddies__bid-button:first')
    fillIn('.bid-info-modal__bid-input', 23)
    fillIn('.bid-info-modal__start-time-hour', 11)
    fillIn('.bid-info-modal__start-time-minute', 59)
    fillIn('.bid-info-modal__start-time-am-pm', 'pm')
    fillIn('.bid-info-modal__place', 'my place')
    fillIn('.bid-info-modal__submit-button', 'my place')
    click('.bid-info-modal__submit-button')
    click('.home__biddies-tab')

    andThen(->
        numBiddies = find('.home__biddie-image').length
        ok(numBiddies is 1,
            'Bidding on user should put them in biddies tab.')
    )

    # Add a profile picture
    click('.topnav__profile-button a')
    andThen(->
        ok(currentPath() is 'profile',
            'Profile page should load when hit profile button.')
    )

    click('.profile__main-photo-null-state')
    andThen(->
        ok(find('.facebook-login-button').length > 0,
            'Facebook login button should show up after clicking add photos.')
    )

    click('.facebook-login-button')

    afterFacebookPhotosLoaded = ->
        # Select all the photos.
        click('.profile__initial-facebook-photo')
        click('.profile__done-selecting-photos')

        # Log out the original user.
        _logoutLoginUserASYNC('a', 'a')

        click('.home__offers-tab')
        
        andThen ->
            numOldOffers = find('.home__biddie-image').length
            ok(numOldOffers > 0,
                'At least one user should show up in offers tab.')

        click('.home-offers__accept-button')
        andThen ->
            numOffersAfterAccept = find('.home__biddie-image').length
            ok(numOffersAfterAccept is 0,
                'At least one user should show up in offers tab.')

        click('.home__upcoming-dates-tab')
        andThen ->
            numUnpaidDatesReceiverOld = (
                find('.home-upcoming-dates__unpaid-dates').length)
            numPaidDatesReceiverOld = (
                find('.home-upcoming-dates__paid-dates').length)
            ok(numUnpaidDatesReceiverOld > 0,
                'At least one user should show up as unpaid date for receiver.')
        _logoutLoginUserASYNC(newuser, newpass)
        click('.home__upcoming-dates-tab')
        andThen ->
            numUnpaidDatesSenderOld = (
                find('.home-upcoming-dates__unpaid-dates').length)
            numPaidDatesSenderOld = (
                find('.home-upcoming-dates__paid-dates').length)
            ok(numUnpaidDatesSenderOld is 1,
                'Exactly one user should show up as unpaid date for sender.')
            ok(numPaidDatesSenderOld is 0,
                'No users should show up as paid date for sender at first.')
            QUnit.start()

        # TODO(daddy): Figure out how to test the stripe shit here...

    andThen(->
        # TODO(daddy): This is fragile-- we wait 1.5 seconds for the facebook
        # photos to finish downloading before continuing with the test.
        setTimeout(afterFacebookPhotosLoaded, 2000)
    )
)
