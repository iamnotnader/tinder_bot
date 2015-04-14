`import Ember from 'ember';`

WaitlistController = Ember.ObjectController.extend(
  needs: ['application']

  isAuthenticated: Ember.computed.alias('controllers.application.isAuthenticated')
)

`export default WaitlistController`