/* jshint node: true */

module.exports = function(environment) {
  var ENV = {
    contentSecurityPolicyHeader: 'Disabled-Content-Security-Policy',
    modulePrefix: 'biddie-frontend',
    environment: environment,
    baseURL: '/',
    locationType: 'hash',
    EmberENV: {
      FEATURES: {
        // Here you can enable experimental features on an ember canary build
        // e.g. 'with-controller': true
      }
    },

    APP: {
      // Here you can pass flags/options to your application instance
      // when it is created

    }
  };

  if (environment === 'development') {
    // ENV.APP.LOG_RESOLVER = true;
    ENV.APP.LOG_ACTIVE_GENERATION = true;
    // ENV.APP.LOG_TRANSITIONS = true;
    // ENV.APP.LOG_TRANSITIONS_INTERNAL = true;
    ENV.APP.LOG_VIEW_LOOKUPS = true;
    // This is the endpoint Django runs on locally so hit that.
    // Make sure to change /etc/hosts to redirect local.biddie.io to localhost
    ENV.APP.API_HOST = 'http://local.biddie.io';
    ENV.APP.API_NAMESPACE = '';
    // ENV.APP.API_HOST = 'http://local.biddie.io:8000';
    // ENV.APP.API_NAMESPACE = 'api/v1';
  }

  if (environment === 'test') {
    // Testem prefers this...
    ENV.baseURL = '/';
    ENV.locationType = 'auto';

    // keep test console output quieter
    ENV.APP.LOG_ACTIVE_GENERATION = false;
    ENV.APP.LOG_VIEW_LOOKUPS = false;

    ENV.APP.rootElement = '#ember-testing';

    // Fuck it-- don't mock anything, just run django backend to test stuff..
    // cd biddie_backend; python manage.py runserver <- that should do it.
    ENV.APP.API_HOST = 'http://local.biddie.io';
    ENV.APP.API_NAMESPACE = '';
  }

  if (environment === 'production') {
    // This is the endpoint we hit in prod
    ENV.APP.API_HOST = 'http://api.biddie.io';
    ENV.APP.API_NAMESPACE = '';
  }

  return ENV;
};
