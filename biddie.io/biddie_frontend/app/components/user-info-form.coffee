`import Ember from 'ember'`
`import SimpleData from '../utils/simple-data';`
`import ConstantValues from '../utils/constant-values';`
`import nameGenerator from '../utils/name-generator';`

THROTTLE_MS = 1000

UserInfoFormComponent = Ember.Component.extend(
  user: null

  firstName: null
  lastName: null

  ethnicityOn: false
  dateOfBirthOn: false;
  taglineOn: false;

  _getChoice: (choiceKey, defaultVal='-') ->
    # Get the previousValue if we can
    previousValue = @get('user.'+choiceKey)
    if previousValue?
      return previousValue
    else
      return defaultVal

  sexChoices: (-> return ConstantValues.sexChoices()).property()
  selectedSex: (-> @_getChoice('sex')).property('user.sex')
  isSexSelected: (->
    return @get('selectedSex') isnt '-'
  ).property('selectedSex')

  selectedsexDidChange: (->
    selectedSex = @get('selectedSex')
    if selectedSex is '-'
      selectedSex = null

    self = this
    unless @get('user.id')?
      return
    SimpleData.patchUser(@get('user')?.id,
      {sex: selectedSex})
    .then((new_user) ->
      self.set('user.sex', new_user.sex)
    )
  ).observes('selectedSex')

  orientationChoices: (-> ConstantValues.orientationChoices()).property()
  selectedOrientation: (-> this._getChoice('orientation')).property('user.orientation')
  isOrientationSelected: (->
    return @get('selectedOrientation') isnt '-'
  ).property('selectedOrientation')

  selectedOrientationDidChange: (->
    selectedOrientation = @get('selectedOrientation')
    if selectedOrientation is '-'
      selectedOrientation = null

    self = this
    unless @get('user.id')?
      return
    SimpleData.patchUser(@get('user')?.id,
      {orientation: selectedOrientation})
    .then((new_user) ->
      self.set('user.orientation', new_user.orientation)
    )
  ).observes('selectedOrientation')


  zipCode: (-> this._getChoice('zip_code', '')).property('user.zip_code')

  zipCodeDidChange: (->
    self = this
    func = ->
      zipCode = @get('zipCode')
      if zipCode?.length < 5
        return

      unless @get('user.id')?
        return
      SimpleData.patchUser(@get('user')?.id,
        {zip_code: zipCode})
      .then((new_user) ->
        self.set('user.zip_code', new_user.zip_code)
      )
    Ember.run.debounce(this, func, THROTTLE_MS)
  ).observes('zipCode')

  isZipCodeFilled: (->
    return @get('zipCode')?.length is 5
  ).property('zipCode')

  monthChoices: (-> ConstantValues.monthChoices).property()
  selectedMonth: (->
    # Get the date_of_birth if we can
    date_of_birth = @get('user.date_of_birth')
    if date_of_birth?
      return parseInt(date_of_birth.split('-')[1])
    else
      return 'MM'
  ).property('user.date_of_birth')

  yearChoices: (-> ConstantValues.yearChoices() ).property()
  selectedYear: (->
    # Get the date_of_birth if we can
    date_of_birth = @get('user.date_of_birth')
    if date_of_birth?
      return parseInt(date_of_birth.split('-')[0])
    else
      return 'YY'
  ).property('user.date_of_birth')


  dayChoices: (-> ConstantValues.dayChoices() ).property()
  selectedDay: (->
    # Get the date_of_birth if we can
    date_of_birth = @get('user.date_of_birth')
    if date_of_birth?
      return parseInt(date_of_birth.split('-')[2])
    else
      return 'DD'
  ).property('user.date_of_birth')

  dateOfBirthChanged: (->
    year = @get('selectedYear')
    month = @get('selectedMonth')
    day = @get('selectedDay')

    date_of_birth = null
    if day? and month? and year? and day isnt 'DD' and month isnt 'MM' and year isnt 'YY'
      date_of_birth = year + '-' + month + '-' + day

    self = this
    unless @get('user.id')?
      return
    SimpleData.patchUser(@get('user')?.id,
      {date_of_birth})
    .then((new_user) ->
      self.set('user.date_of_birth', new_user.date_of_birth)
    )
  ).observes('selectedYear', 'selectedMonth', 'selectedDay')

  isDaySelected: (->
    return @get('selectedDay') isnt 'DD'
  ).property('selectedDay')

  isMonthSelected: (->
    return @get('selectedMonth') isnt 'MM'
  ).property('selectedMonth')

  isYearSelected: (->
    return @get('selectedYear') isnt 'YY'
  ).property('selectedYear')

  ethnicityChoices: (-> ConstantValues.ethnicityChoices()).property()
  selectedEthnicity: (-> this._getChoice('ethnicity') ).property('user.ethnicity')
  isEthnicitySelected: (->
    return @get('selectedEthnicity') isnt '-'
  ).property('selectedEthnicity')

  selectedEthnicityDidChange: (->
    selectedEthnicity = @get('selectedEthnicity')
    if selectedEthnicity is '-'
      selectedEthnicity = null

    self = this
    unless @get('user.id')?
      return
    SimpleData.patchUser(@get('user')?.id, 
      {ethnicity: selectedEthnicity})
    .then((new_user) ->
      self.set('user.ethnicity', new_user.ethnicity)
    )
  ).observes('selectedEthnicity')

  heightFeetChoices: (-> ConstantValues.heightFeetChoices()).property()
  selectedHeightFeet: (->
    # Get the height_inches if we can
    height_inches = @get('user.height_inches')
    if height_inches?
      return Math.floor(height_inches / 12)
    else
      return '-'
  ).property('user.height_inches')

  isHeightFeetSelected: (->
    return @get('selectedHeightFeet') isnt '-'
  ).property('selectedHeightFeet')

  heightInchesChoices: (-> ConstantValues.heightInchesChoices()).property()
  selectedHeightInches: (->
    # Get the height_inches if we can
    height_inches = @get('user.height_inches')
    if height_inches?
      return height_inches % 12
    else
      return '-' 
  ).property('user.height_inches')

  isHeightInchesSelected: (->
    return @get('selectedHeightInches') isnt '-'
  ).property('selectedHeightInches')

  heightDidChange: (->
    inches = @get('selectedHeightInches')
    feet = @get('selectedHeightFeet')
    height_inches = null
    if (inches? and feet? and inches isnt '-' and feet isnt '-')
      height_inches = inches + feet*12

    self = this
    unless @get('user.id')?
      return
    SimpleData.patchUser(@get('user')?.id, 
        {height_inches})
    .then((new_user) ->
      self.set('user.height_inches', new_user.height_inches)
    )
  ).observes('selectedHeightInches', 'selectedHeightFeet')


  ivyLeagueChoices: (-> ConstantValues.ivyLeagueChoices).property()
  selectedIvyLeague: (-> this._getChoice('ivy_league')).property('user.ivy_league')
  ivyLeagueDidChange: (->
    ivyLeague = @get('selectedIvyLeague')
    if ivyLeague is '-'
      ivyLeague = null

    self = this
    unless @get('user.id')?
      return
    SimpleData.patchUser(@get('user')?.id, 
      {ivy_league: ivyLeague})
    .then((new_user) ->
      self.set('user.ivy_league', new_user.ivy_league)
    )
  ).observes('selectedIvyLeague')

  isIvyLeagueSelected: (->
    return @get('selectedIvyLeague') isnt '-'
  ).property('selectedIvyLeague')

  ageChoices: (-> ConstantValues.ageChoices()).property()
  selectedAge: (-> this._getChoice('age')).property('user.age')
  ageDidChange: (->
    age = @get('selectedAge')
    if age is '-'
      age = null

    self = this
    unless @get('user.id')?
      return
    SimpleData.patchUser(@get('user.id'), 
      {age})
    .then((new_user) ->
      self.set('user.age', new_user.age)
    )
  ).observes('selectedAge')

  isAgeSelected:  (->
  	return @get('selectedAge') isnt '-'
  ).property('selectedAge')

  initializeNames: (->
    firstName = @get('user.first_name')
    lastName = @get('user.last_name')

    if firstName? and lastName?
      @set('firstName', firstName)
      @set('lastName', lastName)
    else
      this.send('randomNameButtonPressed')
  ).on('init').observes('selectedSex')

  isFirstNameFilled: (->
    return @get('firstName') isnt ''
  ).property('firstName')

  isLastNameFilled: (->
    return @get('lastName') isnt ''
  ).property('lastName')

  nameChanged: (->
    self = this
    func = ->
      firstName = self.get('firstName')
      lastName = self.get('lastName')
      return unless firstName? and lastName?

      unless @get('user.id')?
        return
      SimpleData.patchUser(@get('user')?.id,
        {first_name: firstName, last_name: lastName})
      .then((new_user) ->
        self.set('user.first_name', new_user.first_name)
        self.set('user.last_name', new_user.last_name)
      )
    Ember.run.debounce(this, func, THROTTLE_MS)
  ).observes('firstName', 'lastName')

  tagline: (-> this._getChoice('tagline', '')).property('user.tagline')
  taglineChanged: (->
    self = this
    func = ->
      tagline = self.get('tagline')

      unless @get('user.id')?
        return
      SimpleData.patchUser(@get('user')?.id,
        {tagline: tagline})
      .then((new_user) ->
        self.set('user.tagline', new_user.tagline)
      )
    Ember.run.debounce(this, func, THROTTLE_MS)
  ).observes('tagline')

  isTaglineFilled: (->
    return @get('tagline') isnt ''
  ).property('tagline')

  actions:
    randomNameButtonPressed: ->
      names = nameGenerator(@get('selectedSex'))
      @set('firstName', names[0].substring(0,1).toUpperCase() + names[0].substring(1).toLowerCase())
      @set('lastName', names[1].substring(0, 1).toUpperCase() + names[1].substring(1).toLowerCase())
)

`export default UserInfoFormComponent`
