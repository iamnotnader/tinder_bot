# Biddie-frontend

## Prerequisites

You will need the following things properly installed on your computer.

* [Git](http://git-scm.com/)
* [Node.js](http://nodejs.org/) (with NPM) and [Bower](http://bower.io/)

## Installation

* Install npm
* `npm install -g ember-cli`
* `npm install -g bower`
* `npm install -g phantomjs`

* `git clone <repository-url>` this repository
* change into the new directory
* `npm install`
* `bower install`

* ember server
* python manage.py runserver (on django)
* navigate to test.local.host.com

## Running / Development
* Modify /etc/hosts file to have the following line (so cookies work):
* `127.0.0.1   test.local.host.com`
* `ember server`
* Visit your app at http://localhost:4200.

### Code Generators

Make use of the many generators for code, try `ember help generate` for more details

### Running Tests

* `ember test`
* `ember test --server`

### Building

* `ember build` (development)
* `ember build --environment production` (production)

### Deploying

Specify what it takes to deploy your app.

## Further Reading / Useful Links

* ember: http://emberjs.com/
* ember-cli: http://www.ember-cli.com/
* Development Browser Extensions
  * [ember inspector for chrome](https://chrome.google.com/webstore/detail/ember-inspector/bmdblncegkenkacieihfhpjfppoconhi)
  * [ember inspector for firefox](https://addons.mozilla.org/en-US/firefox/addon/ember-inspector/)

