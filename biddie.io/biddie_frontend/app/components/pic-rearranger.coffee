`import Ember from 'ember'`
`import SimpleData from '../utils/simple-data';`
`import { sortFacebookPhotosByPosition } from '../utils/common-functions';`

PicRearrangerComponent = Ember.Component.extend(
    allPhotos: null

    actions:
        rearrangePhotos: (beingDraggedSourceUrl, draggedOverSourceUrl) ->
          self = this
          # Used to rearrange photos when dragging them around.
          selectedPhotos = @get('allPhotos')?.filter((x) -> x.photo_position?)

          # Figure out the index of the photo being dragged and the one it's
          # being dragged over.
          fromPosition = null
          toPosition = null
          for photo, i in selectedPhotos
            if photo.source_url is beingDraggedSourceUrl
              fromPosition = i
            if photo.source_url is draggedOverSourceUrl
              toPosition = i

          console.log(fromPosition + ' ' + toPosition)

          return unless fromPosition? and toPosition? and (fromPosition isnt toPosition)

          # Move all the photos appropriately.
          savedPhoto = selectedPhotos[fromPosition]
          if fromPosition < toPosition
            for i in [fromPosition...toPosition]
              selectedPhotos[i] = selectedPhotos[i+1]
          else
            for i in [fromPosition...toPosition]
              selectedPhotos[i] = selectedPhotos[i-1]
          selectedPhotos[toPosition] = savedPhoto

          # Renumber all the photos.
          for photo, i in selectedPhotos
            photo.photo_position = i+1

          # Sort the global photos list to reflect the change in positions.
          sortFacebookPhotosByPosition(self, 'allPhotos')

        patchPhotoOrder: ->
          # Upload new photo ordering to the server.
          self = this
          selectedPhotos = @get('allPhotos')?.filter((x) -> x.photo_position?)
          SimpleData.patchAllPhotos(@get('user.id'), selectedPhotos)
          .then((userRes) ->
              self.set('allPhotos', userRes.photos)
          )
)

`export default PicRearrangerComponent`
