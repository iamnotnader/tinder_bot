`import Ember from 'ember'`
`import ENV from 'biddie-frontend/config/environment';`
`import SimpleData from '../utils/simple-data';`
`import { onboardingKeys } from '../utils/constant-values';`

BASE_URL = ENV.APP.API_HOST + '/' + ENV.APP.API_NAMESPACE

ApplicationRoute = Ember.Route.extend(
  _possiblyReroute: (resolvedModel) ->
    user = resolvedModel?.user
    unless user?.id?
      this.replaceWith('landing')
      return

    onWaitlist = user.on_waitlist
    unless onWaitlist?
      # This shouldn't happen ever... If it does, just log and keep them on the waitlist...
      console.log('ERROR: onWaitlist is not defined...')
      this.replaceWith('waitlist')
      return
    if onWaitlist
      # Transition to the waitlist page
      this.replaceWith('waitlist')
      return

    # We made it past the gauntlet-- show the home page!
    # TODO(daddy): It's not really clear what we should do here. One reasonable
    # thing would be to just whitelist the routes that we are allowed to show
    # directly and redirect all other requests to /home.
    this.replaceWith('home')

  _countSelectedPhotos: (photoArr) ->
    unless photoArr? and photoArr.length > 0
      return 0
    count = 0
    for photo in photoArr
      if photo.photo_position?
        count += 1
    return count

  _parseModel: (res) ->
    self = this
    objToReturn = {
      user: res.user ? res
      bidsByCategory: res.bids_by_category ? []
      usersByCategory: res.users_by_category ? []
      allBids: res.all_bids ? []
    }
    hasAllKeys = true
    for key, value of onboardingKeys
      unless objToReturn.user[key]?
        hasAllKeys = false
        break
    objToReturn.user['has_onboarded'] = false
    if hasAllKeys and self._countSelectedPhotos(objToReturn.user.photos) >= 5
      objToReturn.user['has_onboarded'] = true
    return objToReturn

  model: ->
    self = this
    successCallback = (res) ->
      return self._parseModel(res)
    SimpleData.fetchUserWithCredentials(null, null, (->), successCallback)

  afterModel: (resolvedModel) ->
    # We have a model, now decide what to show the user based on her permissions/flags.
    this._possiblyReroute(resolvedModel)

  _resetController: ->
    # TODO(daddy): we need a way to reset all these fields without wiping
    # their values in the database...
    #
    # @controllerFor('profile')?.setProperties(
    #   'selectedSex': null
    #   'selectedOrientation': null
    #   'zipCode': null
    #   'selectedDay': null
    #   'selectedMonth': null
    #   'selectedYear': null
    #   'selectedEthnicity': null
    #   'selectedHeightFeet': null
    #   'selectedHeightInches': null
    #   'selectedIvyLeague': null
    #   'firstName': null
    #   'lastName': null
    #   'tagline': null
    # )

    @controller.set('user', null)
    @controller.set('model', null)

  actions:
    openModelModal: (modalName, model, outlet='modal') ->
      self = this
      Ember.run(->
        self.controllerFor(modalName).set('model', model)
        self.render(modalName,
          into: 'application',
          outlet: outlet
        )
      )
    
    closeModal: (modalName='modal') ->
      return this.disconnectOutlet(
        outlet: modalName,
        parentView: 'application'
      )

    openModalWithMessage: (message, message_key) ->
      self = this
      self.send(
        'openModelModal',
        'alert-modal',
        {title: message, message_key}
      )

    logOut: ->
      self = this
      SimpleData.deletePath('login/')
      .then(
        (res) -> null
        (err) ->
          console.log('Error logging out: ' + err.statusText)
      )
      self.replaceWith('landing')
      self._resetController()
      return false

    login: () ->
      # We get the email and password from the controller to avoid passing
      # arguments to the login function. This is a workaround to get input 
      # helpers to be able to call login from their action.
      email = this.controllerFor('login').get('emailLogin')
      password = this.controllerFor('login').get('passwordLogin')

      self = this
      unless email? and password?
        self.send(
          'openModelModal',
          'alert-modal',
          {title: 'Please enter a username and password.'}
        )
        return

      errorCallback = (title) ->
        self.send('openModelModal', 'alert-modal', {title})
      successCallback = (res) ->
        Ember.run(-> # Fucking hack to get testing to work...
          resolvedModel = self._parseModel(res)
          self.controller.set('model', resolvedModel)
          self._possiblyReroute(resolvedModel)
        )
      SimpleData.fetchUserWithCredentials(
        email, password, errorCallback, successCallback
      )
      return false

    signUp: () ->
      # We get the email and password from the controller to avoid passing
      # arguments to the login function. This is a workaround to get input 
      # helpers to be able to call login from their action.
      email = this.controllerFor('landing').get('emailSignup')
      password = this.controllerFor('landing').get('passwordSignup')

      self = this
      unless (email? and password?)
        self.send('openModelModal', 'alert-modal', {title: 'Please enter a username and password.'}) 
        return

      errorCallback = (title) ->
        self.send('openModelModal', 'alert-modal', {title})
      successCallback = (res) ->
        resolvedModel = self._parseModel(res)
        Ember.run(-> # Fucking hack to get testing to work...
          self.controller.set('model', resolvedModel)
          self._possiblyReroute(resolvedModel)
        )
      SimpleData.createUser(email, password, errorCallback, successCallback)
      return false
)

`export default ApplicationRoute`
