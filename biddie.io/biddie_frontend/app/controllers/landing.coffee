`import Ember from 'ember';`

LandingController = Ember.ObjectController.extend(
  needs: ['application']

  emailSignup: Ember.computed.alias('controllers.application.emailSignup')
  passwordSignup: Ember.computed.alias('controllers.application.passwordSignup')
)

`export default LandingController`