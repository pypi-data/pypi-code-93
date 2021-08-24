import pprint
import json
import pytz
import traceback
import dateutil
import requests
import re

from datetime import datetime
from tzlocal import get_localzone
from starthinker.util.project import project
from starthinker.util.google_api import API_DCM
from starthinker.util.email import send_email
from starthinker.task.traffic.feed import Feed, FieldMap

DATE_FORMAT = '%m/%d/%Y %H:%M:%S'


def is_live(url):
  try:
    request_headers = {
        'user-agent':
            'Mozilla/5.0 (X11; CrOS x86_64 11151.113.1) AppleWebKit/537.36 '
            '(KHTML, like Gecko) Chrome/71.0.3578.127 Safari/537.36',
        'Accept':
            '*/*'
    }

    response = requests.get(url, headers=request_headers, timeout=5)

    return_code = response.status_code
    response.close()

    return return_code >= 200 and return_code <= 299
  except Exception as ex:
    print(str(ex))

    return False


def write_status(status, message):
  status_feed = Feed(
      project.task['auth'],
      project.task['sheet_id'],
      'lp_dawn_status',
      parse=False)

  if len(status_feed.feed) == 1:
    status_feed_item = status_feed.feed[0]

    now = datetime.now(get_localzone())
    now = now.astimezone(pytz.timezone('America/Chicago'))

    status_feed_item['Last Run Time'] = now.strftime('%Y-%m-%dT%H:%M:%S.000%z')
    status_feed_item['Last Run Status'] = status
    status_feed_item['Message'] = message

    status_feed.update()


@project.from_parameters
def lp_dawn():
  if project.verbose:
    print('Landing Page Dawn')

  # Load feed
  feed = None
  status = 'NORMAL'
  message = ''

  try:
    feed = Feed(
        project.task['auth'], project.task['sheet_id'], 'lp_dawn', parse=False)
  except:
    pass

  # For each item in the feed
  try:
    for feed_item in feed.feed:
      try:
        # Verify the status of the status of the item to determine if it needs
        # processing
        if feed_item[FieldMap.LP_DAWN_STATUS] in ['', 'PENDING', 'LP_NOT_LIVE']:

          # Verify if the date is in the past
          if feed_item[FieldMap.LP_DAWN_TIME_FOR_UPDATE]:
            date = dateutil.parser.parse(
                '%sT%s' % (feed_item[FieldMap.LP_DAWN_DATE_FOR_UPDATE],
                           feed_item[FieldMap.LP_DAWN_TIME_FOR_UPDATE]))
          else:
            date = dateutil.parser.parse(
                '%s' % (feed_item[FieldMap.LP_DAWN_DATE_FOR_UPDATE]))

          date = pytz.timezone('America/Chicago').localize(date)
          now = datetime.now(get_localzone())

          if date < now:

            # Verify if the landing page is live
            if feed_item.get('Force', 'false').lower() == 'true' or is_live(
                feed_item[FieldMap.LP_DAWN_URL]):

              # Update Landing Page
              landing_page = API_DCM(project.task['auth']).advertiserLandingPages().get(
                  profileId=project.task['dcm_profile_id'],
                  id=feed_item[FieldMap.LP_DAWN_LP_ID]).execute()
              landing_page['url'] = feed_item[FieldMap.LP_DAWN_URL]
              API_DCM(project.task['auth']).advertiserLandingPages().update(
                  profileId=project.task['dcm_profile_id'],
                  body=landing_page).execute()

              # Update status in the feed
              feed_item[FieldMap.LP_DAWN_STATUS] = 'UPDATED'
              feed_item[FieldMap.LP_DAWN_UPDATE_TIME] = now.strftime(
                  '%Y-%m-%dT%H:%M:%S.000%z')
              feed_item[FieldMap.LP_DAWN_MESSAGE] = ''

            else:
              feed_item[FieldMap.LP_DAWN_STATUS] = 'PENDING'
              feed_item[
                  FieldMap.LP_DAWN_MESSAGE] = '%s is not live' % feed_item[
                      FieldMap.LP_DAWN_URL]

              if status == 'NORMAL':
                status = 'WARNING'
                message = 'One or more landing pages are not live'
          else:
            feed_item[FieldMap.LP_DAWN_STATUS] = 'PENDING'
            feed_item[
                FieldMap.LP_DAWN_MESSAGE] = 'Date / Time for update not reached'
      except Exception as e:
        traceback.print_exc()
        msg = str(e)

        status = 'ERROR'
        message = msg

        try:
          print('sending email')
          print(feed_item)
          print(feed_item[FieldMap.LP_DAWN_EMAIL])
          send_email(
              'user', feed_item[FieldMap.LP_DAWN_EMAIL], 'mauriciod@google.com',
              '', 'Landing Page Dawn Error Notification',
              '%s: Landing Page ID: %s' %
              (msg, feed_item[FieldMap.LP_DAWN_LP_ID]))
        except:
          pass

        match = re.search(r'"(.*)"', msg)

        if match:
          feed_item[FieldMap.LP_DAWN_MESSAGE] = 'ERROR: %s' % match.group(1)
        else:
          feed_item[FieldMap.LP_DAWN_MESSAGE] = 'ERROR: %s' % msg

        feed_item[FieldMap.LP_DAWN_STATUS] = 'ERROR'

  except Exception as ex:
    status = 'ERROR'
    message = str(e)
    send_email('user', 'mauriciod@google.com', 'mauriciod@google.com', '',
               'Landing Page Dawn Error Notification', 'Unhandled error!')

  finally:
    feed.update()
    try:
      write_status(status, message)
    except:
      pass

  # handle errors, do not fail silently


if __name__ == '__main__':
  lp_dawn()
