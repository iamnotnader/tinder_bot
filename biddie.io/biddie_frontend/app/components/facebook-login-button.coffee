`import Ember from 'ember'`

FacebookLoginButtonComponent = Ember.Component.extend(
	tagName: 'button'
	classNames: ['facebook-login-button']
	click: ->
		self = this
		FB.login(
			(res) ->
				if (res.authResponse)
					FB.api('/me', (basicResponse) ->
						self.sendAction('handleBasicInfo', basicResponse)
						console.log('Basic info scraped.')
					);
					FB.api('/me/photos', (photoResponse) ->
						self.sendAction('handlePhotos', photoResponse)
						console.log('Photos scraped.')
					);

					console.log('good auth')
				else
					console.log('ERROR: Received facebook response with no authResponse.')
			{scope: 'public_profile,email,user_photos,user_friends'}
		)
)

`export default FacebookLoginButtonComponent`
