from datetime import date
import json
import argparse

from starthinker.util.project import project
from starthinker.util.google_api import API_SNIPPETS

if __name__ == '__main__':

  # get parameters
  parser = argparse.ArgumentParser()
  parser.add_argument(
      '--ldap', '-l', help='Name of user to fetch snippets for.', default=None)
  parser.add_argument(
      '--weeks_back',
      '-w',
      help='Number of weeks to go back, 0 is this week.',
      default=0)

  # initialize project
  project.from_commandline(parser=parser)

  results = API_SNIPPETS('user').listByConstraints(
      startDate='09-03-2108',  #date.today().strftime('%m-%d-%Y'),
      #endDate=date.today().strftime('%m-%d-%Y'),
      userGroupKey='kenjora',  #project.args.ldap,
      fields='items(text)').execute()

  print(results)
