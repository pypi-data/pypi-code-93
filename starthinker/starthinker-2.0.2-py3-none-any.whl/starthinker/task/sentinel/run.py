import json

from starthinker.util.project import project
from starthinker.util.google_api import API_Drive
from starthinker.util.bigquery import query_to_rows


def get_drive_authorized_users(auth, drive, file_id):
  drive_file = drive.files().get(
      fileId=project.task['file_id'], fields='name,permissions').execute()
  result = {}

  for permission in drive_file['permissions']:
    if permission.get('emailAddress', None):
      result[permission['emailAddress']] = permission['id']

  return result


def get_dbm_authorization(auth, emails):
  result = {}

  in_email = '\'%s\'' % '\',\''.join(emails)
  query = ('SELECT email, primaryEmail, super_user, global_access, '
           'global_reporting_user, permissions FROM '
           '[plx.google:mauriciod.starthinker_dbmsentinel.all] WHERE email in '
           '(%s) or primaryEmail in (%s) ') % (in_email, in_email)

  access_list = query_to_rows(
      auth,
      'google.com:starthinker',
      'starthinker',
      query,
      row_max=None,
      legacy=True)

  for row in access_list:
    access = {
        'email': row[0],
        'primary_email': row[1] == 'true',
        'super_user': row[2] == 'true',
        'global_access': row[3] == 'true',
        'global_reporting_user': row[4],
        'permissions': row[5] or 'NOPERMISSIONS'
    }

    for email in emails:
      if email.lower() == access['email'].lower() or email.lower(
      ) == access['primary_email']:
        result[email] = access

  return result


def is_dbm_super_user(access):
  return access['super_user'] or access['global_access']


def has_dbm_partner_access(access, partner_ids):
  if not partner_ids:
    return False

  for partner_id in partner_ids:
    if access.get('permissions', '').find('P%s' % partner_id) == -1:
      return False

  return True


def has_dbm_advertiser_access(access, advertiser_ids):
  if not advertiser_ids:
    return False

  for advertiser_id in advertiser_ids:
    if access.get('permissions', '').find('A%s' % advertiser_id) == -1:
      return False

  return True


def get_dbm_unauthorized_users(emails, dbm_authorization, partner_ids,
                               advertiser_ids):
  result = []

  for email in emails:
    if email in dbm_authorization:
      access = dbm_authorization[email]

      if not is_dbm_super_user(access):
        if not has_dbm_partner_access(access, partner_ids):
          if not has_dbm_advertiser_access(access, advertiser_ids):
            result.append(email)
    else:
      # No user access found
      result.append(email)

  return result


@project.from_parameters
def sentinel():
  if project.verbose:
    print('Sentinel')

  auth = project.task['auth']

  partner_ids = None
  partner_ids_config = project.task.get('dbm_partner_ids', '')
  if partner_ids_config:
    partner_ids = [
        partner_id.strip() for partner_id in partner_ids_config.split(',')
    ]

  advertiser_ids = None
  advertiser_ids_config = project.task.get('dbm_advertiser_ids', '')
  if advertiser_ids_config:
    advertiser_ids = [
        advertiser_id.strip()
        for advertiser_id in advertiser_ids_config.split(',')
    ]

  authorized_users = get_drive_authorized_users(auth, drive,
                                                project.task['file_id'])

  dbm_authorization = get_dbm_authorization(auth, authorized_users.keys())
  unauthorized_users = get_dbm_unauthorized_users(authorized_users.keys(),
                                                  dbm_authorization,
                                                  partner_ids, advertiser_ids)

  for user in unauthorized_users:
    API_Drive(auth).permissions().delete(
        fileId=project.task['file_id'],
        permissionId=authorized_users[user]).execute()


if __name__ == '__main__':
  sentinel()
