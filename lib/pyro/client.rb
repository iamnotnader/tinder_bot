module TinderPyro
  class Client
    def initialize
      @requestor = Requestor.new
    end

    def dislike(user_id)
      @requestor.get_request("pass/#{user_id}")
    end

    def fetch_updates(last_activity_time = Time.now)
      @requestor.post_request(
        :updates,
        last_activity_date: Utilities.format_time(last_activity_time)
      )
    end

    def get_nearby_users
      @requestor.get_request('user/recs')
    end

    def info_for_user(user_id)
      @requestor.get_request("user/#{user_id}")
    end

    def like(user_id)
      @requestor.get_request("like/#{user_id}")
    end

    def profile
      @requestor.get_request(:profile)
    end

    def send_message(user_id, message)
      @requestor.post_request(
        "user/matches/#{user_id}",
        message: message
      )
    end

    def sign_in(facebook_id, facebook_token)
      @requestor.auth_request(facebook_id, facebook_token)
    end

    def update_location(latitude, longitude)
      @requestor.post_request("user/ping", lat: latitude, lon: longitude)
    end
  end
end
