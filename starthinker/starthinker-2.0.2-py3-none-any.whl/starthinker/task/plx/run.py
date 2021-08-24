from starthinker.util.project import project
from starthinker.util.sheets import sheets_read


@project.from_parameters
def plx():
  # read peers from sheet
  rows = sheets_read(project.task['auth'], project.task['sheet']['url'],
                     project.task['sheet']['tab'],
                     project.task['sheet']['range'])

  wheres = []
  # construct where clause
  for row in rows:
    if not row:
      continue
    account, advertisers = row
    if account and advertisers:
      for advertiser in advertisers.split(','):
        wheres.append('(%s=%d AND %s=%d)' %
                      (project.task['field']['account'], int(account),
                       project.task['field']['advertiser'], int(advertiser)))
    elif advertisers:
      for advertiser in advertisers.split(','):
        wheres.append('%s=%d' %
                      (project.task['field']['advertiser'], int(advertiser)))
    elif account:
      wheres.append('%s=%d' % (project.task['field']['account'], int(account)))

  wheres = '\n  OR '.join(wheres)

  # print ( no API so STDOUT )
  print(project.task['query'].replace('[WHERE]', wheres).replace('; ', ';\n'))


if __name__ == '__main__':
  plx()
