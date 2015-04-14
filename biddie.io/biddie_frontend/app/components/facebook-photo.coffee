`import Ember from 'ember'`
`import SimpleData from '../utils/simple-data';`

FacebookPhotoComponent = Ember.Component.extend(
  tagName: 'img'
  classNameBindings: ['isSelected:facebook-photo-component-selected:'] # If isSelected, attach class, else do nothing.
  attributeBindings: ['src', 'draggable']

  draggable: false

  dragOverHook: null

  dropHook: null

  # This should be a photo object (like defined in simple-data)
  photoData: null

  # Whether or not clicking on this image should do anything.
  selectable: true

  user_id: null

  src: (->
    return @get('photoData')?.source_url
  ).property('photoData')

  isSelected: (->
    # A photo is selected if its position is defined.
    return @get('selectable') and @get('photoData.photo_position')?
  ).property('photoData.photo_position')

  click: (->    
    if @get('selectable')
      if @get('photoData.photo_position')?
        @set('photoData.photo_position', null)
      else
        @set('photoData.photo_position', -1)
      # Send the position to the server.
      SimpleData.postPhoto(@get('user_id'), @get('photoData'))
  )

  dragLeave: (event) ->
    return unless @get('draggable')
    event.preventDefault()
    otherPhotoSource = window.photoSourceBeingDragged

    # TODO(daddy): style this
    #@set 'dragClass', 'deactivated'

  dragOver: (event) ->
    return unless @get('draggable')
    event.preventDefault()
    photoSourceBeingDragged = window.photoSourceBeingDragged
    photoSourceCurrentlyDraggedOver = @get('photoData.source_url')
    # We have to do this check because dragOver gets called like a bazilliion times
    # with the same id...
    if photoSourceCurrentlyDraggedOver isnt window.lastPhotoSourceDraggedOver
      window.lastPhotoSourceDraggedOver = photoSourceCurrentlyDraggedOver
      this.sendAction('dragOverHook', photoSourceBeingDragged, photoSourceCurrentlyDraggedOver)

      # TODO(daddy): style this
      #@set 'dragClass', 'activated'

  drop: (event) ->
    return unless @get('draggable')

    otherPhotoSource = window.photoSourceBeingDragged

    # Have to set properties on window because html5 dragging doesn't
    # support data transfer between drop->dragOver
    window.photoSourceBeingDragged = null
    window.photoSourceCurrentlyDraggedOver = null

    this.sendAction('dropHook')

    # TODO(daddy): style this
    #@set 'dragClass', 'deactivated'

  dragStart: (event) ->
    return unless @get('draggable')

    # Have to set properties on window because html5 dragging doesn't
    # support data transfer between drop->dragOver
    window.photoSourceBeingDragged = @get('photoData.source_url')
    window.photoSourceCurrentlyDraggedOver = null
)

`export default FacebookPhotoComponent`
