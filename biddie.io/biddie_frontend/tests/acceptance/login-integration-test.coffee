`import Ember from 'ember';`
`import { test } from 'ember-qunit';`
`import startApp from '../helpers/start-app';`
`import SimpleData from 'biddie-frontend/utils/simple-data'`

App = null

module('Authentication and login',
    setup: ->
        App = startApp();

    teardown: ->
        Ember.run(App, App.destroy)
)

test('Check that login flow works', ->
    expect(13)
    SimpleData.deletePath('login/', null, false) 
    visit('/')

    andThen(->
        ok(currentPath() is 'landing',
            'Should be on landing page initially.')
        ok(find('.login__password-input').length > 0,
            'Login input field should show up initially.')
        ok(find('.login__email-input').length > 0,
            'Email input field should show up initially.')
        ok(find('.landing__signup-button').length > 0,
            'Signup button should show up initially.')
        ok(find('.topnav__logout').length is 0,
            'Logout button should NOT show up initially.')
    )

    newuser = 'newuser@biddie.io'+Math.random()
    newpass = 'newuserpassword'
    fillIn('.login__email-input', newuser)
    fillIn('.login__password-input', newpass)
    click('.landing__signup-button')

    andThen(->
        ok(find('.topnav__logout').length > 0,
            'Logout button should show up if user is created.')
    )

    click('.topnav__logout')

    andThen(->
        ok(find('.login__email-input').length > 0,
            'Email input field should show up after logout.')
        ok(find('.landing__signup-button').length > 0,
            'Signup button should show up after logout.')
        ok(find('.topnav__logout').length is 0,
            'Logout button should NOT show up after logout.')
    )

    click('.landing__login-button')

    fillIn('.login__email-input', 'wronguser@biddie.io')
    fillIn('.login__password-input', 'wrongpassword')
    click('.landing__login-button')

    andThen(->
        ok(currentPath() is 'login',
            'Should be on login page after hitting login button.')
        ok(find('.topnav__logout').length is 0,
            'Logout button should NOT show up if login is incorrect.')
    )

    fillIn('.login__email-input', newuser)
    fillIn('.login__password-input', newpass)
    click('.landing__login-button')

    andThen(->
        ok(currentPath() is 'home',
            'Login input field should show up initially.')
        ok(find('.topnav__logout').length > 0,
            'Logout button should show up if login is correct.')
    )
)