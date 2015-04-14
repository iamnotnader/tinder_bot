import requests
import re
import sys
import urllib

num_profiles = 500
page_number = 1
girl_url_path = 'https://www.seekingarrangement.com/member/search.php?country_id=231&distance=250&body_type%%5B0%%5D=slim&age_high=26&ethnicity%%5B0%%5D=asian&ethnicity%%5B1%%5D=white&sort=modified_dt_desc&photo=1&edu=1&last_login_dt=1392085231&pg_page=%s&pg_perpage=%s&pg_width=7&pg_total=841' % (str(page_number), str(num_profiles))
dude_url_path = 'https://www.seekingarrangement.com/member/search.php?distance=50&sort=modified_dt_desc&photo=1&last_login_dt=1392096699&pg_page=%s&pg_perpage=%s&pg_width=7&pg_total=10000' % (str(page_number), str(num_profiles))

# You have to get this from Chrome right after you visit the site..
cookie = {
  'log_last_activity': '1423632726',
  'dACCOUNT': 'miqogec32tckto5gq5u0ebn7c7',
  '_dc_gtm_UA-724180-1': '1',
  'location_not_validated': '1',
  '_gat_UA-724180-1': '1',
  'sa_language': 'en-us',
  '_ga': 'GA1.2.1577639176.1423622967',
}

num_users_to_scrape = 9999999
min_num_photos = 3

if len(sys.argv) > 1:
  if sys.argv[1] == 'dude':
    print >> sys.stderr, 'using dude!'
    url_path = dude_url_path
else:
  print >> sys.stderr, 'using chick!'
  url_path = girl_url_path

resp = requests.get(url_path, cookies=cookie)
profile_links = set(re.findall('https.*?search-recently-active', resp.text))
profile_images_by_user = []

for i, profile_link in enumerate(profile_links):
  print >> sys.stderr, str(i) + '/' + str(len(profile_links))
  profile_resp = requests.get(profile_link, cookies=cookie)
  photo_links = set([ph for ph in re.findall('https.*?photos.*?.jpg', profile_resp.text) if 'thumbs' in ph])
  if len(photo_links) >= min_num_photos:
    for single_image in photo_links:
      print single_image.replace('thumbs/', '')
    print '---'
  profile_images_by_user.append(photo_links)
  if i == num_users_to_scrape:
    break
