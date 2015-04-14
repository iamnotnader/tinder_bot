"""
Takes a list of user images, where each user's list of images
is separated by "---" on its own line. For example:

  user1_1.jpg
  user1_2.jpg
  ---
  user2_1.jpg
  ...

The script downloads all the images and puts them into a directory
structure locally.
"""

import sys
import os
import urllib

BASE_DIR_NAME = 'user_photos'

photo_links_file = open(sys.argv[1])

user_photo_links = []
num_users_to_download = 99999

user_index = 0
for line in photo_links_file.readlines():
  line = line.strip('\n')
  if line == '---' and len(user_photo_links) > 0:
    print >> sys.stderr, str(user_index) + '/' + 'uh.. not sure how many..'
    folder_name = '%s/user_%s' % (BASE_DIR_NAME, user_index)
    if not os.path.exists(folder_name):
      os.makedirs(folder_name)
    for photo_index, photo_link in enumerate(user_photo_links):
      urllib.urlretrieve(photo_link, '%s/%s.jpg' % (folder_name, str(photo_index)))
    user_photo_links = []
    user_index += 1
  else:
    user_photo_links.append(line)
  if user_index == num_users_to_download:
    break

