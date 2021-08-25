import requests
from django.core.management.base import BaseCommand, CommandError
from djangoaddressesapp import import_regions, import_state, import_cities

class Command(BaseCommand):
    help = 'Import regions, states and cities by IBGE api'

    def handle(self, *args, **options):
        
        # Import Regions
        self.stdout.write(self.style.NOTICE('Initializing Import of Regions by IBGE API.'))
        import_regions()
        self.stdout.write(self.style.SUCCESS('Finalized import of Regions.'))

        # Import States
        self.stdout.write(self.style.NOTICE('Initializing Import of States by IBGE API.'))
        import_state()
        self.stdout.write(self.style.SUCCESS('Finalized import of States.'))

        # Import Cities
        self.stdout.write(self.style.NOTICE('Initializing Import of Cities by IBGE API.'))
        import_cities()
        self.stdout.write(self.style.SUCCESS('Finalized import of Cities.'))
