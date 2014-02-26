module TinderPyro
  module Utilities
    extend self

    def format_time(time)
      time.utc.iso8601(3)
    end
  end
end
