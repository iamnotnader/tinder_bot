`import Ember from 'ember';`

AlertModalController = Ember.ObjectController.extend(
	actions:
		close: () ->
			return this.send('closeModal')
)

`export default AlertModalController;`