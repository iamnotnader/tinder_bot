require 'spec_helper'

describe TinderPyro::Utilities do
  describe '.format_time' do
    it 'converts time to iso8601 with milliseconds' do
      time = Time.new(2014, 2, 17, 18, 25, 42, '-08:00')

      formatted_time = TinderPyro::Utilities.format_time(time)

      expect(formatted_time).to eq '2014-02-18T02:25:42.000Z'
    end
  end
end
