`import Ember from 'ember'`

DAYS_OF_WEEK = [
  "Sunday"
  "Monday"
  "Tuesday"
  "Wednesday"
  "Thursday"
  "Friday"
  "Saturday"
]

MINUTES = [
  {label: 'MM', id: '-'},
  {label: '00', id: 0},
  {label: '15', id: 15},
  {label: '30', id: 30},
  {label: '45', id: 45}
]

DateTimePickerComponent = Ember.Component.extend(
  shouldSelectDuration: false

  dateChoices: (->
    daysAvailable = []
    today = new Date()
    # Push it forward by one hour to keep past dates from being
    # selected.
    today = new Date(today.getTime() + 60*60*1000)
    for numDays in [0..7]
      futureDate = new Date(today.getTime() + numDays*24*60*60*1000);
      weekday = DAYS_OF_WEEK[futureDate.getDay()]
      dd = futureDate.getDate()
      mm = futureDate.getMonth() + 1
      yyyy = futureDate.getFullYear()
      daysAvailable.push({
        label: weekday + ': ' + mm + '/' + dd
        id: yyyy + '-' + mm + '-' + dd + '-' + weekday
      })
    return daysAvailable
  ).property()

  fullTimeChoices: (->
    self = this
    timesAvailable = [{label: 'HH', id: '-'}]
    for hourTime in [1..12]
      timesAvailable.push({
        label: hourTime
        id: hourTime
      })
    return timesAvailable
  ).property()

  changeTimeChoicesIfDateChanges: (->
    self = this
    selectedDate = self.get('fieldsSet.selectedDate')
    dateChoices = self.get('dateChoices')
    return unless selectedDate?
    if selectedDate is dateChoices[0].id
      unadjustedHours = new Date().getHours()
      currentHour = (unadjustedHours + 1) % 12;
      fullTimeChoices = self.get('fullTimeChoices')
      self.set('fieldsSet.timeChoices', [{label: 'HH', id: '-'}].concat(fullTimeChoices[currentHour..]))
      self.set('fieldsSet.selectedHour', self.get('fieldsSet.timeChoices')[0].id)
      if unadjustedHours > 12
        self.set('amOrPmChoices',[{label: 'pm'}])
        self.set('fieldsSet.selectedAmOrPm', self.get('amOrPmChoices')[0].label)
    else
      self.set('fieldsSet.timeChoices', self.get('fullTimeChoices'))
      self.set('amOrPmChoices',[{label: 'am'}, {label: 'pm'}])
  ).observes('fieldsSet.selectedDate', 'dateChoices')

  minuteChoices: (->
    return MINUTES
  ).property()

  amOrPmChoices: (->
    return [{label: 'am'}, {label: 'pm'}]
  ).property()

  durationChoices: (->
    return [
      {label: '30m'}
      {label: '1h'}
      {label: '2h'}
      {label: '3h'}
      {label: '4h'}
      {label: '5h'}
      {label: '24h'}
    ]
  ).property()

  fieldsSet: null

  inputIsValid: (->
    return @get('fieldsSet.seconds_since_epoch')?
  ).property('fieldsSet.seconds_since_epoch')

  _convert_12_to_24_hour: (hour, is_am) ->
    if is_am and hour is 12
      return 0
    unless is_am or hour is 12
      return hour + 12
    return hour

  fieldsSetObserver: (->
    self = this
    unless (self.get('fieldsSet.selectedDate') and
          self.get('fieldsSet.selectedHour')?  and
          self.get('fieldsSet.selectedHour') isnt '-' and
          self.get('fieldsSet.selectedMinute')? and
          self.get('fieldsSet.selectedMinute') isnt '-' and
          self.get('fieldsSet.selectedAmOrPm')?
    )
      self.set('fieldsSet.seconds_since_epoch', null)
      return
    [year, month, day] = self.get('fieldsSet.selectedDate').split('-')
    hour = self._convert_12_to_24_hour(parseInt(self.get('fieldsSet.selectedHour')),
                                       self.get('fieldsSet.selectedAmOrPm') is 'am')
    minute = self.get('fieldsSet.selectedMinute')
    self.set('fieldsSet.seconds_since_epoch',
      (new Date(year, month-1, day, hour, minute)).getTime() / 1000.0)
  ).observes('fieldsSet.selectedDate', 'fieldsSet.selectedHour',
             'fieldsSet.selectedMinute', 'fieldsSet.selectedAmOrPm')
)

`export default DateTimePickerComponent`
