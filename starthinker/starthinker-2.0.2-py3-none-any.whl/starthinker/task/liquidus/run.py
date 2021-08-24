import re
import json
import datetime
from urllib.request import urlopen

from starthinker.util.project import project
from starthinker.util.sheets import sheets_read, sheets_write, sheets_clear

URL_SUFFIX = 'cm_mmc=DIS-_-AQ-_-DIS-_-%ecid!&cm_mmca1=Core&cm_mmca2=uf&cm_mmca20=OLAMC--%ebuy!--%esid!--%epid!'
liquidus_url = 'http://api.cofactordigital.com/retail/480058ae784e2461/listings.json?limit=500&storeid=%s&promotioncode=%s&tagid=5913,5914&returnmode=full&require=ListingWithLink'
stores_url = 'http://api.cofactordigital.com/retail/480058ae784e2461/stores.json?limit=%d&offset=%d'

states = {
    'AL': 'Alabama',
    'AK': 'Alaska',
    'AZ': 'Arizona',
    'AR': 'Arkansas',
    'CA': 'California',
    'CO': 'Colorado',
    'CT': 'Connecticut',
    'DE': 'Delaware',
    'FL': 'Florida',
    'GA': 'Georgia',
    'HI': 'Hawaii',
    'ID': 'Idaho',
    'IL': 'Illinois',
    'IN': 'Indiana',
    'IA': 'Iowa',
    'KS': 'Kansas',
    'KY': 'Kentucky',
    'LA': 'Louisiana',
    'ME': 'Maine',
    'MD': 'Maryland',
    'MA': 'Massachusetts',
    'MI': 'Michigan',
    'MN': 'Minnesota',
    'MS': 'Mississippi',
    'MO': 'Missouri',
    'MT': 'Montana',
    'NE': 'Nebraska',
    'NV': 'Nevada',
    'NH': 'New Hampshire',
    'NJ': 'New Jersey',
    'NM': 'New Mexico',
    'NY': 'New York',
    'NC': 'North Carolina',
    'ND': 'North Dakota',
    'OH': 'Ohio',
    'OK': 'Oklahoma',
    'OR': 'Oregon',
    'PA': 'Pennsylvania',
    'RI': 'Rhode Island',
    'SC': 'South Carolina',
    'SD': 'South Dakota',
    'TN': 'Tennessee',
    'TX': 'Texas',
    'UT': 'Utah',
    'VT': 'Vermont',
    'VA': 'Virginia',
    'WA': 'Washington',
    'WV': 'West Virginia',
    'WI': 'Wisconsin',
    'WY': 'Wyoming',
    'AS': 'American Samoa',
    'DC': 'District of Columbia',
    'FM': 'Federated States of Micronesia',
    'GU': 'Guam',
    'MH': 'Marshall Islands',
    'MP': 'Northern Mariana Islands',
    'PW': 'Palau',
    'PR': 'Puerto Rico',
    'VI': 'Virgin Islands',
    'AE': 'Armed Forces Africa',
    'AA': 'Armed Forces Americas',
    'AE': 'Armed Forces Canada',
    'AE': 'Armed Forces Europe',
    'AE': 'Armed Forces Middle East',
    'AP': 'Armed Forces Pacific'
}


def get_offers(store_id, promotion_code, retry=5):
  try:
    url = liquidus_url % (store_id, promotion_code)
    response = urlopen(url, timeout=10)
    offers = json.loads(response.read())
    return offers
  except Exception as e:
    print('An error occurred calling Liquidus API %s' % str(e))
    if retry > 0:
      return get_offers(store_id, promotion_code, retry - 1)


def clean(store):
  zip_replaces = {'98503': '98506', '98509': '98503', '60418': '60803'}

  if store['zip'].find('-') >= 0:
    store['zip'] = store['zip'][:store['zip'].find('-')]

  store['zip'] = zip_replaces.get(store['zip'], store['zip'])

  return store


def get_stores(retry=5):
  result = []
  limit = 1000
  offset = 0
  done = False

  try:
    while not done:
      url = stores_url % (limit, offset)
      offset += limit

      response = json.loads(urlopen(url).read())
      stores = response.get('results', [])

      for store in stores:
        result.append(
            clean({
                'id': store['id'],
                'state': store['address']['state'],
                'zip': store['address']['postalCode']
            }))

      if len(stores) < 1000:
        done = True

    return result
  except Exception as e:
    print(str(e))
    if retry > 0:
      return get_stores(retry - 1)


@project.from_parameters
def liquidus():
  # Read store ids from stores list
  # Legacy: reading stores from sheet, can be removed
  #sheet_range = project.task['stores_list']['range']
  #store_data = sheets_read(project.task['auth'],
  #project.task['stores_list']['sheet_id'],
  #sheet_range.split('!')[0],
  #sheet_range.split('!')[1])
  #stores = [{'id': str(item[0]), 'zip': item[6], 'state': item[5]} for item in store_data]

  stores = get_stores()

  # Read category tree
  cat_tree_range = project.task['category_tree']['range']
  raw_category_tree = sheets_read(
      project.task['auth'],
      cat_tree_range.split('!')[0],
      cat_tree_range.split('!')[1],
      sheets_url=project.task['category_tree']['sheet_id'])

  category_tree = {}
  for category in raw_category_tree:
    if len(category) >= 4:
      category_tree[int(category[0])] = {
          'CategoryTreePathForwards': category[1],
          'audience': category[2],
          'dcm_targeting_Key': category[3]
      }

  # Determine promotion code for the current week
  today = datetime.date.today()
  offset = (today.weekday() + 1) % 7
  previous_sunday = today - datetime.timedelta(offset)
  promotion_code = previous_sunday.strftime('officedepot-%y%m%d')

  # Call liquidus API for each store and add to the feed
  feed = []
  row = 0
  store_ct = 0

  # Use this in case you want to just process the first store, useful for
  # testing while developing
  # for store in stores[:1]:
  for store in stores:

    store_ct += 1

    while len(store['zip']) < 5:
      store['zip'] = '0' + store['zip']

    offers = get_offers(store['id'], promotion_code)

    print('processing store %s' % store['id'])

    for offer in offers['results']:
      feed.append([])

      startDate = datetime.datetime.fromtimestamp(
          int(re.search('\(([\d]*)\)', offer['saleStartDate']).group(1)) / 1000)
      endDate = datetime.datetime.fromtimestamp(
          int(re.search('\(([\d]*)\)', offer['saleEndDate']).group(1)) / 1000)

      days_to_save = abs(endDate - datetime.datetime.now()).days
      days_to_save_message = 'Last chance to save'
      if days_to_save == 1:
        days_to_save_message = '1 day to save'
      elif days_to_save > 1:
        days_to_save_message = '%d days to save' % days_to_save

      zip = '%s,%s,United States' % (store['zip'], states[store['state']])

      category = None

      if offer.get('departments', None):
        category = category_tree.get(offer['departments'][0]['id'], None)

      # Map API response to feed
      # TODO: Using the following line causes an overflow problem because the offer
      # ids and store ids are too long. We can't use strings because Studio
      # doesn't like it. We need to find out a way to hash these values into
      # shorter ints while keeping them unique
      # feed[row].append(int(str(offer['id']) + str(store['id'])))
      feed[row].append(int(str(offer['id']) + str(store_ct)))
      feed[row].append(offer['title'])
      feed[row].append(category['audience'] if category else '')
      feed[row].append(str(startDate))
      feed[row].append(str(endDate))
      feed[row].append(offer['deal'])
      feed[row].append(offer['originalDeal'])
      feed[row].append(offer['brands'][0]['name'])
      feed[row].append(offer['images'][0]['imageURL'])
      feed[row].append(offer['additionalDealInformation'])
      feed[row].append(zip)

      if category:
        feed[row].append(category['CategoryTreePathForwards'])
      else:
        feed[row].append('')

      link = ''

      if 'links' in offer and len(offer['links']) > 0:
        link = offer['links'][0]['linkURL']

        if not '?' in link:
          link += '?'
        else:
          link += '&'

        link += URL_SUFFIX

      feed[row].append(link)

      feed[row].append(days_to_save_message)

      if category:
        feed[row].append(category['dcm_targeting_Key'])
      else:
        feed[row].append('')

      feed[row].append(offer.get('buyOnlineLinkURL') or link)

      row += 1

  # Write feed to trix
  print('uploading feed, size %d rows' % len(feed))
  feed_range = project.task['feed']['range']
  sheets_clear(project.task['auth'], project.task['feed']['sheet_id'],
               feed_range.split('!')[0],
               feed_range.split('!')[1])
  sheets_write(project.task['auth'], project.task['feed']['sheet_id'],
               feed_range.split('!')[0],
               feed_range.split('!')[1], feed)


if __name__ == '__main__':
  liquidus()
