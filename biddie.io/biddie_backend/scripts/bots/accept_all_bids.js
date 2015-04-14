// Accept all the bids placed on fake users.

use server;

fake_user_ids = []
db.users.find({is_fake_user: true}).forEach(function(user_obj) {
    fake_user_ids.push(user_obj._id)
})

db.bids.find({}).forEach(function(bid_obj) {
    for (var i = 0; i < fake_user_ids.length; i++) {
        user_id = fake_user_ids[i]
        if(user_id.equals(bid_obj.receiver_id) & bid_obj.bid_state === 'outstanding') {
            db.bids.update({_id: bid_obj._id}, {$set: {'bid_state': 'receiver_accepted', 'accepted_time_and_place_index': 0}})
        }
    }
})

