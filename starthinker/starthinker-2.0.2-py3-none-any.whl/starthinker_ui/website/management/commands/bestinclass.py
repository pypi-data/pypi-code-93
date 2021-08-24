from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from starthinker_ui.recipe.scripts import Script
from starthinker_ui.recipe.colab import script_to_colab


class Command(BaseCommand):
  help = 'Generate Templates For Colab'

  def handle(self, *args, **kwargs):

    for script in Script.get_scripts():
      print('%s, %s, "%s", %s' %
            (script.get_name(), script.get_requirements(),
             script.get_description().replace('"', '\''), script.get_authors()))
