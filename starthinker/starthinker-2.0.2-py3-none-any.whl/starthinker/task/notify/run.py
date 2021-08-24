#{
#  "notify": {
#    "auth":"user",
#    "to": "mauriciod@google.com",
#    "query": "select pv.advertiser, pv.io, pv.io_id, string(pv.pacing * 100) + ' %'  from [starthinker.pacing_view] pv where pacing < 0.7 order by pv.pacing asc"
#  }
#}

from starthinker.util.project import project
from starthinker.util.email import send_email
from starthinker.util.bigquery import query_to_rows


@project.from_parameters
def notify():
  if project.verbose:
    print('Notify')

  email_to = project.task['to']
  auth = project.task['auth']
  dataset = project.task['dataset']
  sql = project.task['query']
  rows = [row for row in query_to_rows(auth, project.id, dataset, sql)]

  if rows:
    html = '<body><table border=1><tr>'

    for row in rows:
      html += '<tr>'

      for column in row:
        html += '<td>%s</td>' % column

      html += '</tr>'

    html += '</table></body>'
    send_email(auth, email_to, 'mauriciod@google.com', None,
               'You have underpacing campaigns!', None, html)


if __name__ == '__main__':
  notify()
