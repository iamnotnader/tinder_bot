`import Ember from 'ember';`
`import config from './config/environment';`

Router = Ember.Router.extend(
  location: config.locationType
)

Router.map(->
  this.route("home")
  this.route("waitlist")
  this.route("landing")
  this.route("login")
  this.route("profile")
  this.route("how-it-works")
);

Router.reopen({
  notifyGoogleAnalytics: (->
    return ga('send', 'pageview', {
        'page': this.get('url'),
        'title': this.get('url')
      });
  ).on('didTransition')
});

`export default Router;`
