from starthinker.util.project import project
from starthinker.util.trix import trix_read, trix_update
from starthinker.util.bigquery import query_to_rows

TEMPLATE_QUERY = """
SELECT
  COUNT(DISTINCT User_ID) reach,
  STRFTIME_UTC_USEC(INTEGER(Event_Time), '%%Y%%m') month,
  COUNT(DISTINCT DBM_Insertion_Order_ID) insertion_orders,
  SUM(FLOAT(DBM_Media_Cost__USD_) / 1000000000) spend,
  SUM(FLOAT(DBM_Revenue__USD_) / 1000000000) revenue
FROM
  [%s.DataTransfer_impression]
WHERE
  DBM_Advertiser_ID IN (%s)
  AND STRFTIME_UTC_USEC(INTEGER(Event_Time), '%%Y%%m%%d') BETWEEN '%s' AND '%s'
  AND REGEXP_MATCH(DBM_Matching_Targeted_Segments, r'(^| )(%s)( |$)')
GROUP BY
  month
ORDER BY
  month asc
"""


@project.from_parameters
def audience_reach_report():
  if project.verbose:
    print('AUDIENCE REACH REPORT')

  configs = trix_read(project.task['auth'], project.task['trix_id'],
                      project.task['config_range'])
  dataset = project.task['dataset']
  advertiser_ids = []
  start_date = ''
  end_date = ''
  segments = []

  for config in configs['values']:
    if config[0]:
      advertiser_ids.append('\'' + config[0] + '\'')

    if not start_date and config[1]:
      start_date = config[1]

    if not end_date and config[2]:
      end_date = config[2]

    if config[3]:
      segments.append(config[3])

  sql = TEMPLATE_QUERY % (dataset, ','.join(advertiser_ids), start_date,
                          end_date, '|'.join(segments))

  #result = run_query(sql, dataset_name=dataset)
  #trix_update(project.task['auth'], project.task['trix_id'], project.task['output_range'], {'values': result[0]}, clear=True)

  rows = query_to_rows(project.task['auth'], project.id, dataset, sql)
  trix_update(
      project.task['auth'],
      project.task['trix_id'],
      project.task['output_range'], {'values': rows},
      clear=True)


if __name__ == '__main__':
  audience_reach_report()
