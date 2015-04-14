`import Ember from 'ember';`
`import { test } from 'ember-qunit';`
`import startApp from '../helpers/start-app';`
`import { notLoggedInServer,
          loggedInServer } from '../helpers/servers/login-server';`
`import { RESPONSES } from '../helpers/responses/responses';`
`import ENV from 'biddie-frontend/config/environment';`

App = null
server = null

OLD_HOST = ENV.APP.API_HOST
module('Test login', {
    setup: ->
        ENV.APP.API_HOST = ''
        App = startApp();
    teardown: ->
        ENV.APP.API_HOST = OLD_HOST
        Ember.run(App, App.destroy);
});

test('Very basic notLoggedInServer test.', ->
    expect(2);
    server = notLoggedInServer();
    $.ajax({
        url: '/login',
        type: "GET",
        async: false,
        error: (err) ->
            ok(false)
        success: (res) ->
            ok(RESPONSES.login_get_notLoggedIn isnt '')
            ok(JSON.stringify(res) is
               JSON.stringify(JSON.parse(RESPONSES.login_get_notLoggedIn)))
    });
    server.shutdown();
);

test('Very basic loggedInServer test.', ->
    expect(2);
    server = loggedInServer();
    $.ajax({
        url: '/login',
        type: "GET",
        async: false,
        error: (err) ->
            ok(false)
        success: (res) ->
            ok(RESPONSES.login_get_loggedIn isnt '')
            ok(JSON.stringify(res) is
               JSON.stringify(JSON.parse(RESPONSES.login_get_loggedIn)))
    });
    server.shutdown();
);

test('Test not logged in should show landing page.', ->
    expect(1);
    server = notLoggedInServer();
    visit('/')
    andThen ->
        ok(currentPath() is 'landing')
    server.shutdown();
);

test('User logged in should take to main page.', ->
    expect(1);
    server = loggedInServer();
    visit('/')
    andThen ->
        ok(currentPath() is 'home')
    server.shutdown();
);
