import logging
import os
import shutil

from crypto.models.crypto_file import Crypto_file
from django.conf import settings
from django.core.management import BaseCommand
from isc_common.models.images import Images
from tqdm import tqdm

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Проверка наличия файлов изображений"

    images_files = set()
    cnt = 1

    def handle(self, *args, **options):
        logger.debug(self.help)

        # self.pbar = tqdm(total=Images.objects.count())

        self.ls_files = os.listdir(settings.FILES_STORE)

        self.checkModelFiles(model=Images)

        if self.pbar:
            self.pbar.close()

        for item in [itm[0] for itm in self.images_files if itm[1] == False]:
            self.cnt += 1
            logger.debug(f'File #{self.cnt} {item} not found !!!!')

        images_files = [itm[0] for itm in self.images_files if itm[1] is True]
        logger.debug(f'images_files: {len(images_files)} founded.')
        self.pbar = tqdm(total=len(self.ls_files))

        self.cnt = 0
        self.size = 0
        for file in self.ls_files:
            if not file in images_files:
                from_full_name = f'{settings.FILES_STORE}{os.sep}{file}'
                to_full_name = f'{settings.UNBOUNDED_FILES_STORE}{os.sep}{file}'

                if os.path.exists(from_full_name):
                    self.size += int(os.path.getsize(from_full_name) / (1024 * 1024))
                    shutil.move(from_full_name, to_full_name)
                    # os.remove(full_name)
                    logger.debug(f'File #{self.cnt} {file} moved.')
                    self.cnt += 1

            self.pbar.update(1)
        logger.debug(f'Removed: {self.size} MB.')

    def checkModelFiles(self, model):
        if not issubclass(model, Crypto_file):
            raise Exception('model must be a Crypto_file')

        self.pbar = tqdm(total=model.objects.count())
        for item in model.objects.all().order_by('id'):
            file_path = item.attfile.name
            if file_path is None or file_path == '':
                continue

            _, file = os.path.split(file_path)

            if file in self.ls_files:
                self.images_files.add((file, True))
                # logger.debug(f'File {file} found')
            else:
                self.images_files.add((file, False))
                logger.debug(f'In {item} File {file} not found !!!!')

            self.pbar.update()
