import logging

from django.core.management import BaseCommand

from lfl_admin.statistic.models.import_command_stuctures import Import_command_stuctures

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Проверка наличия файлов изображений"

    images_files = set()
    cnt = 1

    def handle(self, *args, **options):
        Import_command_stuctures.import_add_info('/home/ayudin/Job/GIT-HUB/LFL/lfl-admin-dev/doc/Составы 6х6 АПЛ.xlsx')
