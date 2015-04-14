`import Ember from 'ember';`
`import SimpleData from '../utils/simple-data';`


BaseController = Ember.ObjectController.extend(
  needs: ['application']

  _checkPath: (fullKey) ->
    self = this
    keyPieces = fullKey.split('.')
    cumStr = keyPieces[0]
    for i in [1...keyPieces.length]
      unless self.get(cumStr)?
        return false
      cumStr += '.'+keyPieces[i]
    return true

  appGet: (keyObj) ->
    self = this
    Ember.run(->
      self.get('controllers.application.' + keyObj)
    )
  appSet: (keyObj, valObj) ->
    self = this
    Ember.run(->
      if self._checkPath('controllers.application.'+keyObj)
        self.set('controllers.application.' + keyObj, valObj)
    )
)

`export default BaseController`