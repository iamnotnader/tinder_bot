`import Ember from 'ember'`
`import SimpleData from '../utils/simple-data';`

DashboardPhotoComponent = Ember.Component.extend(
  imgClasses: 'dashboard-photo__img-stuff'
  photoClass: 'dashboard-photo__content'
  boxClass: 'dashboard-photo__box'
  classNames: 'dashboard-photo__overall-div-container'
  tagName: 'div'

  # This should be a photo object (like defined in simple-data)
  photoData: (->
    @get('selectedUserObj.photos')
  ).property('selectedUserObj.photos')

  hackUpdatePhotoData: (->
    # TODO(daddy): Figure out why we have instances where observers
    # update, but properties don't. In this case, photoData refuses to
    # update, but this observer, which depends on the exact same thing,
    # updates just fine.
    @set('photoData', @get('selectedUserObj.photos'))
    @set('selectedPhotoIndex', -1)
    @_advanceSelectedPhotoIndex()
  ).observes('selectedUserObj')

  selectedUserObj: null
  userIndex: null
  userList: null

  clickable: true
  clickHandler: null

  # This is a hack to call a function in our component from our
  # controller, which is something you generally shouldn't do in ember.
  # Sigh... When either of these is set to true, they trigger the next/previous
  # photo to be shown respectively.
  prevPhotoBool: false
  nextPhotoBool: false

  selectedPhotoIndex: 0

  oldInterval: null
  cycleThroughPicsOnHover: true

  _getNewPhotoElem: (src) ->
    imgClasses = @get('imgClasses')
    return Ember.$('<img src='+src+' class="'+imgClasses+'">')

  _appendElement: (elem) ->
    thisElem = this.$('.'+@get('photoClass'))
    thisElem.append(elem)

  didInsertElement: ->
    this._appendElement(this._getNewPhotoElem(@get('src')))

  src: (->
    selectedPhotoIndex = @get('selectedPhotoIndex')
    return @get('photoData.'+selectedPhotoIndex+'.source_url')
  ).property('photoData', 'selectedPhotoIndex')

  click: (->
    return unless @get('clickable')
    # TODO(daddy): This should open up a modal
    self = this
    if @get('oldInterval')?
      clearInterval(@get('oldInterval'))
      @set('oldInterval', null)
    this.sendAction('clickHandler', @get('selectedUserObj'), @get('userIndex'), @get('userList'))
  )

  _advanceSelectedPhotoIndex: (goBackward=false)->
    return unless @get('selectedPhotoIndex')? and @get('photoData')?
    self = this
    selectedPhotoIndex = self.get('selectedPhotoIndex')
    numPhotos = self.get('photoData.length')
    if numPhotos <= 1
      return
    if goBackward
      newPhotoIndex = (selectedPhotoIndex + numPhotos - 1) % numPhotos
    else
      newPhotoIndex = (selectedPhotoIndex + 1) % numPhotos
    self.set('selectedPhotoIndex', newPhotoIndex)

    oldPhotoElement = self.$('.'+@get('photoClass')).children()
    newSrc = @get('photoData.'+newPhotoIndex+'.source_url')
    newPhotoElement = self._getNewPhotoElem(newSrc)
    newPhotoElement.hide()
    self._appendElement(newPhotoElement)
    newPhotoElement.fadeIn(500, -> oldPhotoElement.remove())

  nextPhotoOnButtonPress: (->
    return unless @get('nextPhotoBool')
    @_advanceSelectedPhotoIndex()
    @set('nextPhotoBool', false)
  ).observes('nextPhotoBool')

  prevPhotoOnButtonPress: (->
    return unless @get('prevPhotoBool')
    @_advanceSelectedPhotoIndex(true)
    @set('prevPhotoBool', false)
  ).observes('prevPhotoBool')

  mouseEnter: (->
    return unless @get('cycleThroughPicsOnHover')
    self = this
    if self.get('oldInterval')?
      return
    self._advanceSelectedPhotoIndex()
    newInterval = setInterval(
      (-> self._advanceSelectedPhotoIndex() ),
      900)
    self.set('oldInterval', newInterval)

    # Disgusting hack we do to make the interval clear when we
    # scroll. See views/home.coffee <--
    window.dashboardPhotoInterval = newInterval
  )

  mouseLeave: (->
    return unless @get('cycleThroughPicsOnHover')
    if @get('oldInterval')?
      clearInterval(@get('oldInterval'))
      @set('oldInterval', null)
  )
)

`export default DashboardPhotoComponent`
