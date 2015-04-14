use server;

// This sets dude_counts_map and girl_counts_map
load('girl_counts_map.js')
load('dude_counts_map.js')
load('name_files/female-first-names.js')
load('name_files/male-first-names.js')
load('name_files/last-names.js')

print(dude_counts_map)
print(girl_counts_map)

user_base = {
    "email" : "jihgfdgffgh",
    "password" : "$2a$12$36iecoWqDuo.JSXr9CAgDekkggUEhjx58DddlpqkeMro0hLYTePYG",
    "on_waitlist" : false,
    "first_name" : "Dan",
    "last_name" : "Droxford",
    "sex" : "m",
    "orientation" : "s",
    "loc_long_lat" : [
            -74.00012,
            40.741012
    ],
    "zip_code" : "10011",
    "height_inches" : 74,
    "ivy_league" : false,
    "age" : 21
}

count = 0
for (key in dude_counts_map) {
    user_base.email = 'dude' + count + '@gmail.com'
    user_base.first_name = maleFirstNames[Math.floor(Math.random() * maleFirstNames.length)]
    user_base.first_name = user_base.first_name[0] + user_base.first_name.substring(1).toLowerCase()
    while (user_base.last_name[0] !== user_base.first_name[0]) {
        user_base.last_name = lastNames[Math.floor(Math.random() * lastNames.length)]
    }
    user_base.sex = 'm'
    user_base.height_inches = Math.floor(Math.random() * 36 + 48)
    user_base.age = Math.floor(Math.random() * 20 + 20)
    if (Math.random() < .3) {
        user_base.ivy_league = true
    }
    photos = []
    // We have an off-by-one error in the counts mapping...
    for (var i = 0; i < dude_counts_map[key] - 1; i++) {
        photo = {}
        photo.source_url = 'https://s3-us-west-2.amazonaws.com/biddie-user-photos/'+ key + '/' + i + '.jpg'
        photo.facebook_id = Math.floor(Math.random())
        photo.photo_position = i
        photos.push(photo)
    }
    user_base.photos = photos
    user_base.is_fake_user = true

    print(JSON.stringify(photos))
    print(user_base.first_name)
    print(user_base.last_name)
    print(key + ' ' + dude_counts_map[key])
    db.users.update({email: user_base.email}, user_base, {upsert: true})
    count += 1
}

count = 0
for (key in girl_counts_map) {
    user_base.email = 'girl' + count + '@gmail.com'
    user_base.first_name = femaleFirstNames[Math.floor(Math.random() * maleFirstNames.length)]
    user_base.first_name = user_base.first_name[0] + user_base.first_name.substring(1).toLowerCase()
    while (user_base.last_name[0] !== user_base.first_name[0]) {
        user_base.last_name = lastNames[Math.floor(Math.random() * lastNames.length)]
    }
    user_base.sex = 'f'
    user_base.height_inches = Math.floor(Math.random() * 36 + 36)
    user_base.age = Math.floor(Math.random() * 12 + 18)
    if (Math.random() < .03) {
        user_base.ivy_league = true
    }
    photos = []
    // We have an off-by-one error in the counts mapping...
    for (var i = 0; i < girl_counts_map[key] - 1; i++) {
        photo = {}
        photo.source_url = 'https://s3-us-west-2.amazonaws.com/biddie-user-photos/'+ key + '/' + i + '.jpg'
        photo.facebook_id = Math.floor(Math.random())
        photo.photo_position = i
        photos.push(photo)
    }
    user_base.photos = photos 
    user_base.is_fake_user = true

    print(JSON.stringify(photos))
    print(user_base.first_name)
    print(user_base.last_name)
    print(key + ' ' + girl_counts_map[key])
    db.users.update({email: user_base.email}, user_base, {upsert: true})
    count += 1
}
