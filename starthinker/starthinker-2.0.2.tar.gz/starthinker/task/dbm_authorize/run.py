#https://cloud.google.com/bigquery/docs/share-access-views

from starthinker.util.bigquery import datasets_create, datasets_access, query_to_view


# BUG: can't mix PLX with BigQuery, so this needs to be fixed.
def get_query(config, task):
  query = """
    SELECT
      SESSION_USER() AS Current_User,
      *
    FROM `%s.%s.%s`
    WHERE
      Advertiser_ID IN (
        SELECT DISTINCT CAST(advertiser_id AS INT64)
        FROM `google.com:dbm-util.plximport.dbm_access_hourly`
        WHERE
          primary_email_hashed = SHA256(LOWER(SESSION_USER()))
            OR
          (
            SELECT has_global_read
            FROM `google.com:dbm-util.plximport.dbm_access_hourly` access
            WHERE
              primary_email_hashed = SHA256(LOWER(SESSION_USER()))
                AND
              has_global_read
            LIMIT 1
          )
      )
  """ % (config.project, task['dataset'], task['table'])

  #print(query)
  return query


def dbm_authorize(config, task):
  if project.verbose:
    print('Authorizing', task['dataset'], task['table'])

  authorized_dataset = '%s_Authorized_DBM' % task['dataset']
  authorized_view = '%s_Authorized_DBM' % task['table']

  # Create a separate dataset to store the authorized view
  datasets_create(config, task['auth'], config.project, authorized_dataset)

  # Create the authorized view in the new dataset
  query_to_view(
      config,
      task['auth'],
      config.project,
      authorized_dataset,
      authorized_view,
      get_query(config, task),
      legacy=False)

  # Assign access controls to the dataset containing the view
  datasets_access(
      config,
      task['auth'],
      config.project,
      authorized_dataset,
      groups=task['groups'],
      role='READER')

  # Authorize the view to access the source dataset
  datasets_access(
      config,
      task['auth'],
      config.project,
      task['dataset'],
      views=[{
          'dataset': authorized_dataset,
          'view': authorized_view
      }])
