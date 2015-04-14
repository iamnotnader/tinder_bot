`import Ember from 'ember'`

ModalDialogComponent = Ember.Component.extend(
  actions:
    close: () ->
      return this.sendAction();
)

`export default ModalDialogComponent`
