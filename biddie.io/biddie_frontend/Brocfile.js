/* global require, module */

var EmberApp = require('ember-cli/lib/broccoli/ember-app');

var app = new EmberApp({
  hinting: false,
  sassOptions: {
    includePaths: [
      'bower_components/foundation/scss'
    ]
  }
});

// Use `app.import` to add additional libraries to the generated
// output files.
//
// If you need to use different assets in different
// environments, specify an object as the first parameter. That
// object's keys should be the environment name and the values
// should be the asset to use in that environment.
//
// If the library that you are including contains AMD or ES6
// modules that you would like to import into your application
// please specify an object with the list of modules as keys
// along with the exports of each module as its value.
app.import('bower_components/bootstrap/dist/css/bootstrap.css');
app.import('bower_components/bootstrap/dist/css/bootstrap.css.map', {
  destDir: 'assets'
});
app.import('bower_components/bootstrap/dist/fonts/glyphicons-halflings-regular.woff', {
  destDir: 'fonts'
});

app.import('bower_components/moment/moment.js');
app.import('bower_components/jquery.cookie/jquery.cookie.js');

var pickFiles = require('broccoli-static-compiler');
var mergeTrees = require('broccoli-merge-trees');

var pinjs = pickFiles('bower_components/pinjs', {
  srcDir: '/',
  files: ['index.js'],
  destDir: '/assets/pinjs'
});

module.exports = mergeTrees([app.toTree(), pinjs]);
