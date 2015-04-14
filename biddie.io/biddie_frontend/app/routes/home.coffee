`import Ember from 'ember'`

HomeRoute = Ember.Route.extend(
    activate: ->
        window.scrollTo(0, 0)
)

`export default HomeRoute`