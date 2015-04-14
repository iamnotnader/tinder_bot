`import Ember from 'ember';`
`import ENV from 'biddie-frontend/config/environment';`
`import SimpleData from '../utils/simple-data';`

BASE_URL = ENV.APP.API_HOST + '/' + ENV.APP.API_NAMESPACE

ApplicationController = Ember.ObjectController.extend(
  isAuthenticated: (->
    return not Ember.isEmpty(@get('model'))
  ).property('model')

  passwordSignup: ''
  emailSignup: ''
)

`export default ApplicationController`
