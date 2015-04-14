myOnboardingKeys = {
  first_name: true,
  height_inches: true,
  ivy_league: true,
  last_name: true,
  orientation: true,
  photos: true,
  sex: true,
  zip_code: true,
  age: true,
};
`export var onboardingKeys = myOnboardingKeys`

ConstantValues = {
  textSexChoices: {
    'f': 'chick'
    'm': 'dude'
    'o': 'other'
  }
  sexChoices: ->
    self = this
    sexChoicesRet = [ { label: '-', id: '-' } ]
    for key, val of self.textSexChoices
      sexChoicesRet.push(
        id: key
        label: val
      )
    return sexChoicesRet

  textOrientationChoices: {
    'g': 'gay'
    's': 'straight'
    'b': 'bisexual'
  }
  orientationChoices: ->
    orientationChoicesRet = [ { label: '-', id: '-' } ]
    for key, val of ConstantValues.textOrientationChoices
      orientationChoicesRet.push(
        id: key
        label: val
      )
    return orientationChoicesRet


  textEthnicityChoices: {
    'a': 'Asian'
    'n': 'Native American'
    'h': 'Hispanic / Latin'
    'm': 'Middle Eastern'
    'i': 'Indian'
    'w': 'White'
    'b': 'Black'
    'o': 'Other'
  }
  ethnicityChoices: ->
    ethnicityChoicesRet = [ { label: '-', id: '-' } ]
    for key, val of ConstantValues.textEthnicityChoices
      ethnicityChoicesRet.push(
        id: key
        label: val
      )
    return ethnicityChoicesRet

  heightFeetChoices: ->
    ret = [{label: '-', id: '-'}]
    for i in [3..8]
      ret.push({id: i, label: i.toString()+'\''})
    return ret

  heightInchesChoices: ->
    ret = [{label: '-', id: '-'}]
    for i in [0..11]
      ret.push({id: i, label: i.toString()+'"'})
    return ret

  ivyLeagueChoices: [
    {label: '-', id: '-'}
    {label: 'Yes', id: true}
    {label: 'No', id: false}
  ]

  ageChoices: ->
    ret = [{label: '-', id: '-'}]
    for i in [21..60]
      ret.push({id: i, label: i.toString()})
    return ret

  monthChoices: [
    {label: 'MM', id: 'MM'}
    {label: 'Jan', id: 1}
    {label: 'Feb', id: 2}
    {label: 'Mar', id: 3}
    {label: 'Apr', id: 4}
    {label: 'May', id: 5}
    {label: 'Jun', id: 6}
    {label: 'Jul', id: 7}
    {label: 'Aug', id: 8}
    {label: 'Sep', id: 9}
    {label: 'Oct', id: 10}
    {label: 'Nov', id: 11}
    {label: 'Dec', id: 12}
  ]

  yearChoices: ->
    years = [{label: "YY", id: 'YY'}]
    currentYear = new Date().getFullYear()
    minYear = currentYear - 19
    for i in [minYear..1930]
      years.push({id: i, label: i.toString()})
    return years

  dayChoices: ->
    ret = [{label: 'DD', id: 'DD'}]
    for i in [1..31]
      ret.push({id: i, label: i.toString()})
    return ret
}

`export default ConstantValues`
