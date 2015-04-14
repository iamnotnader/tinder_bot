`import Ember from 'ember';`
`import SimpleData from '../utils/simple-data';`
`import BaseController from './base-controller';`

ProfileModalController = BaseController.extend(
	onPicturePickPage: true
	onPictureOrderingPage: false
	onProfileInfoPage: false

	actions:
		close: ->
			return this.send('closeModal')

		handlePhotos: (photos) ->
			# TODO(daddy): Avoid creating repeats of photos. Check to see if they already
			# exist before posting them and stuff.
			self = this

			userId = @appGet('user.id')
			unless userId?
				@send('openModelModal', 'alert-modal', {title: "Problem downloading PHOTOS from facebook."})

			# TODO(daddy): Make this promises.all() style.
			simplePhotos = []
			for photo in photos.data
				simplePhotos.push(
					facebook_id: photo.id
					source_url: photo.source
					photo_position: null
				)
			SimpleData.patchAllPhotos(userId, simplePhotos)
			.then((user) ->
				self.appSet('user.photos', user.photos)
			)

		handleBasicInfo: (basicInfo) ->
			# We actually don't want to do anything here..

			# self = this
			# userId = @appGet('user.id')
			# unless userId?
			# 	@send('openModelModal', 'alert-modal', {title: "Problem downloading BASIC INFO from facebook."})

			# SimpleData.patchUser(userId, {
			# 	first_name: basicInfo.first_name,
			# 	last_name: basicInfo.last_name
			# }).then((newUser) ->
			# 	self.appSet('user.first_name', newUser.first_name)
			# 	self.appSet('user.last_name', newUser.last_name)
			# )
)

`export default ProfileModalController;`