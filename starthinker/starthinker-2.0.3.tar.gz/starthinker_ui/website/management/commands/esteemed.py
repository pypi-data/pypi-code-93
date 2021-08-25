import os
from itertools import chain

from django.core.management.base import BaseCommand, CommandError
from django.template.loader import render_to_string
from django.conf import settings

from starthinker_ui.recipe.scripts import Script


class Command(BaseCommand):
  help = 'Generate GTECH Files For Google3'

  def handle(self, *args, **kwargs):

    # hard code to be the internal server
    settings.CONST_URL = "https://starthinker.corp.google.com"

    scripts = list(Script.get_scripts())

    print('Writing:', '%s/docs/GTECH' % settings.UI_ROOT)

    with open('%s/docs/GTECH' % settings.UI_ROOT, 'w') as gtech_file:
      gtech_file.write(
          render_to_string(
              'website/starthinker.gtech', {
                  'scripts':
                      len(scripts),
                  'authors':
                      len(
                          set(
                              chain(
                                  *[script.get_authors()
                                    for script in scripts])))
              }))

    scripts = [
        s for s in Script.get_scripts()
        if s.get_impacts() and s.get_open_source()
    ]

    for script in scripts:

      directory = '%s/docs/solution/%s' % (settings.UI_ROOT, script.get_tag())
      print('Writing: %s/GTECH' % directory)
      if not os.path.exists(directory):
        os.makedirs(directory)

      with open('%s/GTECH' % directory, 'w') as solution_file:
        solution_file.write(
            render_to_string('website/script.gtech', {'script': script}))
