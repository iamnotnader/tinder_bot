a_user_id = ObjectId('54b7385d194498a1acecc5c1');

var sender_review = {
  "receiver_rating": 2,
    "would_like_to_pay": false,
    "receiver_showed_up": true,
    "question_text": [
    "Your answers will not affect your reputation on the site in any way, and we don't reveal your responses to your date-- so be honest!",
        "Did your biddie show up?",
        "Would you like to pay your biddie?",
        "Did your biddie look significantly worse than their pictures?",
        "Rate your overall experience.",
        "We will ask your date if they showed up. If they say they did and you don\u2019t pay, you will get a \u201cno-pay\u201d added to your profile. This will negatively affect people\u2019s willingness to date you in the future. On the other hand, developing a reputation for always paying results in much cheaper and more attractive dates. So pay your biddie if they showed up and you had a good time."
  ],
    "looked_worse_than_pics": true
};

var receiver_review = {
  "comfort_rating": 2,
    "question_text": [
    "Did you show up to the date?",
    "How comfortable did your date make you feel?",
    "Did your date look significantly worse than their pictures?",
    "Your answers will not affect your compensation or your reputation on the site in any way, and we don't reveal your responses to your date-- so be honest!"
  ],
    "did_show_up": true,
    "looked_worse_than_pics": false
};

var base_bid = {
  "receiver_id" : ObjectId("54b7385d194498a1acecc5c1"),
  "sender_id" : ObjectId("54c53ed54298651ae2758044"),
  "time_bid_created_at" : ISODate("2015-01-23T02:24:16.206Z"),
  "bid_state" : "sender_confirmed",
  "bid_amount" : 100,
  "times_and_places_list" : [
    { "selectedAmOrPm" : "am", "selectedDuration" : "30m", "selectedMinute" : 0, "selectedHour" : 4, "seconds_since_epoch" : 1922090000, "selectedDate" : "2015-1-24-Saturday", "place_name" : "my place" },
    { "selectedAmOrPm" : "am", "selectedDuration" : "30m", "selectedMinute" : 0, "selectedHour" : 5, "seconds_since_epoch" : 1422090000, "selectedDate" : "2015-1-24-Sunday", "place_name" : "my place" }
  ],
  "accepted_time_and_place_index": 1,
  "sender_review": sender_review,
  "receiver_review": receiver_review
};

use server;
user_ids = db.users.find({}, {_id: 1});

var insert_bid_between_users = function(sender_id, receiver_id) {
  base_bid.sender_id = sender_id;
  base_bid.receiver_id = receiver_id;
  print(sender_id);
  print(receiver_id);
  db.bids.insert(base_bid);
};

num_reviews = 3;
for (var i = 0; i < num_reviews; i++) {
  insert_bid_between_users(user_ids[i]._id, a_user_id);
}
for (var i = num_reviews; i < num_reviews + num_reviews; i++) {
  insert_bid_between_users(a_user_id, user_ids[i]._id);
}
a_is_receiver = db.bids.find(
  {
    receiver_id: ObjectId('54b7385d194498a1acecc5c1'),
    bid_state: 'sender_confirmed',
    sender_review: {$exists: true}
  },
  {
    'sender_review.receiver_rating': 1,
    'sender_review.receiver_showed_up': 1,
    'sender_review.looked_worse_than_pics': 1,
     _id: 0
   }
);

a_is_sender = db.bids.find(
  {
    sender_id: ObjectId('54b7385d194498a1acecc5c1'),
    bid_state: 'sender_confirmed',
    receiver_review: {$exists: true},
    sender_review: {$exists: true}
  },
  {
    'receiver_review.looked_worse_than_pics': 1,
    'receiver_review.comfort_rating': 1,
    'receiver_review.did_show_up': 1,
    'sender_review.would_like_to_pay': 1,
    _id: 0
  }
);
