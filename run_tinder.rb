#!/usr/bin/env ruby

require_relative 'lib/pyro.rb'
require 'json'

# Get this using Charles Proxy
# http://nickfishman.com/post/50557873036/reverse-engineering-native-apps-by-intercepting-network
FACEBOOK_TOKEN = 'XXX'
FACEBOOK_ID    = 'XXX'

# We need to sleep when we get rate-limited by Tinder.
SLEEP_SECONDS  = 1800

# Where you want to be.
LATITUDE = 40.7231
LONGITUDE = -74.0008


pyro = TinderPyro::Client.new
my_info = pyro.sign_in(FACEBOOK_ID, FACEBOOK_TOKEN)

# print my_info
my_user_id = my_info["user"]["_id"]

puts my_user_id

# Update your location
# Note: this request often takes around 30 seconds
pyro.update_location(LATITUDE, LONGITUDE)

while 1 == 1 do
    # Fetch updates (messages, likes, etc)
    pyro.fetch_updates

    # Try 
    nearby_users_response = pyro.get_nearby_users
    STDERR.puts "nearby_users_response: %s" % nearby_users_response

    nearby_users = nearby_users_response.fetch("results", [])
    STDERR.puts "nearby_users: %s" % nearby_users.join(", ")

    # If we don't have any nearby users, we're probably being throttled by Tinder.
    # Try again in a bit.
    if nearby_users.length == 0
        STDERR.puts "Going to sleep for %s seconds" % SLEEP_SECONDS
        sleep SLEEP_SECONDS

        # Update our location when we wake up.
        pyro.update_location(LATITUDE, LONGITUDE)
    end

    #print JSON.pretty_generate(nearby_users)

    # print parsed['results'][0].keys()
    # [u'distance_mi', u'common_like_count', u'common_friend_count', u'common_likes',
    # u'bio', u'gender', u'birth_date_info', u'photos', u'common_friends', u'ping_time',
    # u'birth_date', u'_id', u'name']

    for user in nearby_users
        this_user_id = user["_id"]
        puts "user_id: %s, distance: %s, birth_date: %s, name: %s" % [this_user_id, user["distance_mi"], user["birth_date"], user["name"]]
        pyro.like(this_user_id)

        STDOUT.flush

        # Can't send a message if you're not matched..
        #resp = pyro.send_message(this_user_id, "Hey, let's grab dinner this week :)")
        #print resp
    end
end
