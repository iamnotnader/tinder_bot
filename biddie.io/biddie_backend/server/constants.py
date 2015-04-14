from pyzipcode import ZipCodeDatabase
from enum import Enum


# Allowed origins.
ALLOWED_ORIGINS = ['http://local.biddie.io:4200',
                   'http://local.biddie.io:7357',
                   'http://www.biddie.io', 'http://www.biddie.io:8000']
ALLOWED_HEADERS = 'Content-Type'

# General constants.
MAX_BID_AMOUNT = 9999

ERROR_MESSAGES = {
    'invalid': "Invalid email or password.",
    'disabled': "Sorry, this account is suspended.",
    'user_exists': "A user already exists with that email address.",
    'does_not_exist': "A user with that ID does not exist.",
    'no_photos': "This user has no photos.",
    'bad_bid_times': "Bid request must contain at least one time+place.",
    'bad_bid_amount': (
        "Bid amount must be between 0 and %d." % (MAX_BID_AMOUNT)),
    'bid_was_none': "The bid entered was None.",
    'bad_sender_id': "Bidder id was null or invalid.",
    'bad_receiver_id': "Biddie id was null or invalid.",
    'bid_on_yourself': "You cannot bid on yourself.",
    'delete_bid_failed': "We couldn't find the bid you wanted to delete.",
    'invalid_bid_rejection': (
        "Attempted to reject a nonexistent bid or something."),
    'cannot_bid_after_rejection': (
        "Cannot bid on a biddie that has rejected you."),
    'nothing_to_cancel': 'No bids to reject.',
    'cannot_reject_twice': 'Cannot reject offer twice.',
    'cannot_cancel_rejected_offer': 'Cannot cancel rejected offer.',
    'weird_bid_state': 'Weird bid state encountered...',
    'outstanding_offer': 'This person has already bid on you-- go accept their date!',
    'cant_bid_after_accepted': ('You have already accepted an offer with this person; ' +
        'cancel it in the dates tab if you want to bid on them.'),
    'pending_date': ('You cant bid on this person because you have a pending date.' +
        ' Cancel it in your dates tab first.'),
    'nothing_to_accept': 'There are no bids to accept.',
    'bad_accept_request': ('Accept request must have receiver_id and ' +
        'accepted_time_and_place_index embedded.'),
    'invalid_index': ('accepted_time_and_place_index cannot be larger than length' + 
        ' of times_and_places_list'),
    'weird_accept_with_no_date': 'Encountered accepted bid with no selected date...',
    'user_bid_access': 'You do not have access to another user\'s bids.',
    'cannot_bid_receiver_accepted': ('You have an accepted offer from this biddie. ' + 
        'Go confirm or cancel it.'),
    'date_passed': 'One of the dates selected has already passed.',
    'weird_bid_with_invalid_date': 'Encountered bid with invalid time+place...',
    'bad_payment_data': 'Bad payment data received.',
    'most_recent_bid_none': 'Most recent bid was None.',
    'cannot_pay_for_unaccepted_bid': 'Trying to pay for a bid that has not been accepted.',
    'cannot_pay_for_expired_date': 'Trying to pay for a bid that has expired.',
    'unpaid_bid_confirmation': 'You must pay for your date before you can accept.',
    'most_recent_bid_has_no_amount': ('Most recent bid for this user has no amount associated ' +
                                      'with it.'),
    'no_user_to_like': 'Like posted without receiver_id in payload.',
    'bid_on_unliked_user': 'Cannot bid on a user until she is liked.',
    'nothing_to_cancel': 'No bid to cancel.',
    'cant_like_bid_on_user': ('Cannot like a user that already has an outstanding bid or ' +
            'something.'),
    'already_liked': 'Already liked this user.',
    'like_yourself': 'Cannot like yourself.',
    'weird_field_in_request': 'Request contained an invalid field.',
    'missing_field': 'Request is missing fields.',
    'too_many_fields': 'Request contains too many fields.',
    'invalid_review': 'You can\'t leave a review for this person because there is ' +
            'another outstanding bid.',
    'you_need_to_review': 'You need to review this person in your feed tab first.',
    'waiting_on_review': 'This person needs to review you first.',
    'already_poked': 'You have already poked this user.',
    'no_poke_to_cancel': 'There are no pokes to cancel.',
    'unaffiliated_poke_cancellation': 'You cannot cancel a poke you\'re not involved in.',
}

# Zip code -> long/lat mapping
ZCDB = ZipCodeDatabase()


# Mongo stuff
class USER_FIELD_NAMES(Enum):
    ZIP_CODE = 'zip_code'  # 5-character string
    LOCATION = 'loc_long_lat'  # [longitude, latitude]
    PHOTOS = 'photos'
    CUSTOMER_ID = 'customer_id'
    LAST_LOGIN_TIME = 'last_login_time'


class SEARCH_FIELD_NAMES(Enum):
    ZIP_CODE = 'zip_code'  # 5-character string
    SEX = 'sex'  # 'm', 'f', 'o'
    ORIENTATION = 'orientation'  # 'g', 's', 'b'


class BID_FIELD_NAMES(Enum):
    TIMES_AND_PLACES_LIST = 'times_and_places_list'
    BID_AMOUNT = 'bid_amount'
    SENDER_ID = 'sender_id'
    RECEIVER_ID = 'receiver_id'
    BID_STATE = 'bid_state'
    TIME_SELECTED_FOR_DATE = 'time_selected_for_date'
    TIME_BID_CREATED_AT = 'time_bid_created_at'
    ACCEPTED_TIME_AND_PLACE_INDEX = 'accepted_time_and_place_index'
    TIMESTAMP_LIST = 'timestamp_list'
    SECONDS_SINCE_EPOCH = 'seconds_since_epoch'
    CARD_ID = 'card_id'
    SENDER_REVIEW = 'sender_review'
    RECEIVER_REVIEW = 'receiver_review'
    POKE_PROPOSAL = 'poke_proposal'


class BID_STATES(Enum):
    SENDER_LIKED = 'sender_liked'
    OUTSTANDING = 'outstanding'
    RECEIVER_ACCEPTED = 'receiver_accepted'
    SENDER_CONFIRMED = 'sender_confirmed'
    RECEIVER_REJECTED = 'receiver_rejected'
    SENDER_CANCELLED_AFTER_ACCEPTED = 'sender_cancelled_after_accepted'
    SENDER_CANCELLED_AFTER_CONFIRMED = 'sender_cancelled_after_confirmed'
    RECEIVER_CANCELLED_AFTER_CONFIRMED = 'receiver_cancelled_after_confirmed'
    SENDER_CANCELLED_BEFORE_ACCEPTED = 'sender_cancelled_before_accepted'
    SENDER_UNLIKED = 'sender_unliked'


class PAYMENT_FIELDS:
    PAYMENT_TOKEN = 'payment_token'
    BID_AMOUNT_CENTS = 'bid_amount_cents'


# Remember to update BID_GROUP_KEY_LIST
class BID_GROUP_KEYS(Enum):
    YOU_HAVE_BID_ON = 'you_have_bid_on'
    USER_LIKES = 'user_likes'
    HAVE_BID_ON_YOU = 'have_bid_on_you'
    CONFIRMED_UPCOMING_DATES = 'confirmed_upcoming_dates'
    UNCONFIRMED_UPCOMING_DATES = 'unconfirmed_upcoming_dates'
    PAST_UNREVIEWED_DATES = 'past_unreviewed_dates'
    PAST_REVIEWED_DATES = 'past_reviewed_dates'
    POKED_YOU = 'poked_you'
    YOU_POKED = 'you_poked'
    # Did you remember update BID_GROUP_KEY_LIST?


class SENDER_REVIEW_FIELDS(Enum):
    RECEIVER_SHOWED_UP = 'receiver_showed_up'
    WOULD_LIKE_TO_PAY = 'would_like_to_pay'
    RECEIVER_RATING = 'receiver_rating'
    LOOKED_WORSE_THAN_PICS = 'looked_worse_than_pics'
    QUESTION_TEXT = 'question_text'


class RECEIVER_REVIEW_FIELDS(Enum):
    DID_SHOW_UP = 'did_show_up'
    COMFORT_RATING = 'comfort_rating'
    LOOKED_WORSE_THAN_PICS = 'looked_worse_than_pics'
    QUESTION_TEXT = 'question_text'


class POKE_STATES(Enum):
    POKE_OUTSTANDING = 'poke_outstanding'
    POKE_CANCELLED_BY_POKER = 'poke_cancelled_by_poker'
    POKE_REJECTED_BY_OTHER = 'poke_rejected_by_other'


class STATS_FIELDS(Enum):
    NO_SHOW = 'no_show'
    NO_PAY = 'no_pay'
    VERY_COMFORTABLE = 'very_comfortable'
    VERY_SATISFIED = 'very_satisfied'
    LOOKED_WORSE_THAN_PICS = 'looked_worse_than_pics'
    UNCOMFORTABLE_DATE = 'uncomfortable_date'
    UNSATISFIED_DATE = 'unsatisfied_date'
    NUM_DATES = 'num_dates'


POKE_CANCEL_STATES = [
    POKE_STATES.POKE_CANCELLED_BY_POKER,
    POKE_STATES.POKE_REJECTED_BY_OTHER,
]


# TODO(daddy): We define this list explicitly becaues
# BID_GROUP_KEYS.__members__ isn't working for some reason.
BID_GROUP_KEY_LIST = [
    BID_GROUP_KEYS.YOU_HAVE_BID_ON,
    BID_GROUP_KEYS.USER_LIKES,
    BID_GROUP_KEYS.HAVE_BID_ON_YOU,
    BID_GROUP_KEYS.UNCONFIRMED_UPCOMING_DATES,
    BID_GROUP_KEYS.CONFIRMED_UPCOMING_DATES,
    BID_GROUP_KEYS.PAST_UNREVIEWED_DATES,
    BID_GROUP_KEYS.PAST_REVIEWED_DATES,
    BID_GROUP_KEYS.POKED_YOU,
    BID_GROUP_KEYS.YOU_POKED,
]


CANCELLED_BID_STATES = [
    BID_STATES.SENDER_CANCELLED_AFTER_ACCEPTED,
    BID_STATES.SENDER_CANCELLED_BEFORE_ACCEPTED,
    BID_STATES.SENDER_CANCELLED_AFTER_CONFIRMED,
    BID_STATES.RECEIVER_CANCELLED_AFTER_CONFIRMED,
    BID_STATES.SENDER_UNLIKED
]


def get_long_lat_for_zip(input_zip):
    zipcode = ZCDB[int(input_zip)]
    return [zipcode.longitude, zipcode.latitude]
