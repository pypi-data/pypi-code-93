from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from starthinker_worker.log import log_get
from starthinker_ui.recipe.models import Recipe


class Command(BaseCommand):
  help = 'Loads logs into recipes'

  def add_arguments(self, parser):
    parser.add_argument(
        '--recipe',
        action='store',
        dest='recipe',
        default=None,
        help='Run a specific recipe.',
    )

  def handle(self, *args, **kwargs):
    print('Load Recipes')
    recipes = Recipe.objects.filter(
        pk=kwargs['recipe']) if kwargs['recipe'] else Recipe.objects.all()

    print('Load Logs')
    logs = log_get([r.uid() for r in recipes], settings.TIME_ZONE)

    print('Assign Logs')
    for recipe in recipes:
      print('.', end='')
      recipe.set_log(logs.get(recipe.uid(), {}))

    print('\nDone')
