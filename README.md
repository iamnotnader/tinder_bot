Fork of Tinder Pyro, a bot that lets you auto-like and message on Tinder.

Nader's Version:

1) Make sure Ruby is installed. I think you need 2.0.0

2) Figure out your facebook token by following:
    - http://nickfishman.com/post/50557873036/reverse-engineering-native-apps-by-intercepting-network

3) Change FACEBOOK_TOKEN and FACEBOOK_ID in run_tinder.rb


4) Change latitude and longitude to where you want to be in run_tinder.rb


5) ./run_tinder.rb > matches_<location>
    - eg: ./run_tinder.rb > matches_soho


6) tail -f matched_location
    - eg: tail -f matches_soho
    - This shows you some information on the girls you're "like"ing.




Tinder Pyro
===========

A wrapper for the Tinder App API.


Installation
------------

Add this line to your application's `Gemfile`:

    gem 'tinder_pyro', '~> 0.0.1'

And then execute:

    $ bundle

Alternatively, install it via command line:

    $ gem install tinder_pyro


Getting Your oauth Token
------------------------

Before using pyro, you must grab your Facebook oauth token. This is best done by
installing (Charles)[http://www.charlesproxy.com/]. This will allow you to view
all HTTP requests from your phone to the network. Note that Tinder uses SSL so
you must set up SSL proxying.

After setting up your proxy, all you need to do in log out and then back in to
the Tinder app. Make sure you are recording with Charles, and it will give you a
request to `https://api.gotinder.com/auth` that looks like:

    {
      "facebook_token":"CAAGm0PX4ZCp...",
      "facebook_id": "547255555"
    }

Now use your Facebook ID and token as shown below.


Usage
-----

**Authenticating**

```ruby
FACEBOOK_ID = '547255555'
FACEBOOK_TOKEN = 'CAAGm0PX4ZCp...'

pyro = TinderPyro::Client.new
pyro.sign_in(FACEBOOK_ID, FACEBOOK_TOKEN)
```

**Interacting with users**

```ruby
# Get nearby users
pyro.get_nearby_users

user_id = '51ddbe849573ef0d12011111'

# Get a user's info
pyro.info_for_user(user_id)

# Swipe Right
pyro.like(user_id)

# Swipe Left
pyro.dislike(user_id)

# Send a saucy message
pyro.send_message(user_id, 'I luv u plz b my friend')
```

**Interacting with yourself**

```ruby
# Update your location
# Note: this request often takes around 30 seconds
latitude = 16.7758
longitude = 3.0094

pyro.update_location(latitude, longitude)

# Fetch updates (messages, likes, etc)
pyro.fetch_updates
```


Contributing
------------

1. Fork it
2. Create your feature branch (`git checkout -b my-new-feature`)
3. Commit your changes (`git commit -am 'Add some feature'`)
4. Push to the branch (`git push origin my-new-feature`)
5. Add tests and make sure they pass
6. Create new Pull Request


Credits
-------

* [Neal Kemp](http://nealke.mp)
* [Carolyn Atterbury](http://github.com/carocaro1234) for coming up with the
  name

Copyright &copy; 2014 Neal Kemp

Released under the MIT License, which can be found in the repository in `LICENSE.txt`.
