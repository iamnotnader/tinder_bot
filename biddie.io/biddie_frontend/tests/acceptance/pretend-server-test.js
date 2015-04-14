import Ember from 'ember';
import { test } from 'ember-qunit';
import startApp from '../helpers/start-app';
import { testServer } from '../helpers/servers/test-server';
import { RESPONSES } from '../helpers/responses/responses';
import ENV from 'biddie-frontend/config/environment';

var App;
var server;

var OLD_HOST = ENV.APP.API_HOST;
module('Test of testing framework', {
    setup: function() {
        ENV.APP.API_HOST = '';
        App = startApp();
    },
    teardown: function() {
        ENV.APP.API_HOST = OLD_HOST;
        Ember.run(App, App.destroy);
    },
});

test('Check that pretend server fakes requests.', function() {
    expect(1);
    server = testServer();
    $.ajax({
        url: '/test',
        type: "GET",
        async: false,
        error: function(err) { ok(false); },
        success: function(res) { ok(res === RESPONSES.test); }
    });
    server.shutdown();
});

test('Check that pretend server shuts down properly.', function() {
    expect(1);
    $.ajax({
        url: '/test',
        type: "GET",
        async: false,
        error: function(err) { ok(true); },
        success: function(res) { ok(false); }
    });
});
