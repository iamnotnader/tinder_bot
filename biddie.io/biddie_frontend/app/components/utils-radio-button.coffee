`import Ember from 'ember';`

UtilsRadioButton = Ember.Component.extend(
  tagName: 'input'
  type: 'radio'
  attributeBindings: ['type', 'htmlChecked:checked', 'value', 'name', 'disabled']
  classNames: 'utils-radio-button__default'

  htmlChecked: (->
    return this.get('value') is this.get('checked');
  ).property('value', 'checked')

  change: (->
    this.set('checked', this.get('value'));
  )

  _updateElementValue: (->
    Ember.run.next(this, ->
      this.$().prop('checked', this.get('htmlChecked'));
    )
  ).observes('htmlChecked')
)

`export default UtilsRadioButton;`
