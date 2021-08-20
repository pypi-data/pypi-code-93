import json
import logging
import os
from tempfile import TemporaryFile

from django.conf import settings
from django.core.files import File
from django.db.models import ProtectedError
from websocket import create_connection

from crypto.models.upload_file import DSResponse_UploadFile
from isc_common.common import SFTP, FILES_STORE_UNKNOWN_TYPE
from isc_common.common.UploadItem import UploadItem
from isc_common.dropzone import Dz
from isc_common.http.DSResponse import JsonResponseWithException
from isc_common.models.image_types import Image_types
from isc_common.models.images import Images
from isc_common.ssh.ssh_client import SSH_Client_settings

logger = logging.getLogger(__name__)


class Common_UploadImage(DSResponse_UploadFile):
    def upload_image(self, request):

        self.dictionary = dict(id=request.GET.get('id'))

        self.dz_dictionary = Dz(request.POST)

        self.host = request.GET.get('host')
        self.port = request.GET.get('port')
        self.image_type_name = request.GET.get('image_type_name')
        if self.image_type_name is None:
            raise Exception('Не задан параметр image_type_name.')
        if not self.port:
            self.port = 80
        self.channel = request.GET.get('ws_channel')
        self.file = request.FILES.get('upload_attatch')

        self.dictionary.update(dict(
            real_file_name=self.file.name,
            stored_file_name=self.dz_dictionary.dzuuid,
            file_size=int(self.dz_dictionary.dztotalfilesize),
            file_mime_type=self.file.content_type)
        )

        item = UploadItem(dictionary=self.dictionary)

        def load_str(pers):
            return f'Загружено: {pers} %'

        res = Images.objects.getOptional(
            size=item.file_size,
            real_name=item.real_file_name,
        )

        if res is not None:
            SSH_CLIENT = SSH_Client_settings()
            ex = SSH_CLIENT.exists(str(res.attfile))
            if ex is False:
                try:
                    res.delete()
                except ProtectedError:
                    pass

                res = None

        if res is None:
            with TemporaryFile() as src:
                src.seek(int(self.dz_dictionary.dzchunkbyteoffset))
                src.write(self.file.read())

                pers = round((int(self.dz_dictionary.dzchunkindex) * 100) / int(self.dz_dictionary.dztotalchunkcount), 2)
                if self.last_chunk:
                    pers = 100

                logger.debug(f'{load_str(pers)}, шаг : {int(self.dz_dictionary.dzchunkindex) + 1} из {self.dz_dictionary.dztotalchunkcount}')

                if self.last_chunk:
                    logger.debug(f'Загружен файл: {item.real_file_name}.')
                    logger.debug(f'Запись временного файла.')

                    with open(item.full_path, 'w+b') as destination:
                        src.seek(0)
                        destination.write(src.read())
                        logger.debug(f'Запись временного файла выполнена.')

                    logger.debug(f'Запись: {item.full_path}.')
                    with open(item.full_path, 'rb') as src:
                        src.seek(0)
                        fileObj = File(src)

                        if isinstance(settings.FILES_STORE, str):
                            file_store = os.path.abspath(settings.FILES_STORE)
                        elif isinstance(settings.FILES_STORE, dict) and settings.FILES_STORE.get('mode') == SFTP:
                            file_store = settings.FILES_STORE.get('PATH')
                        else:
                            raise Exception(FILES_STORE_UNKNOWN_TYPE)

                        res = Images.objects.create(
                            image_type=Image_types.objects.get_or_create(code=self.image_type_name, defaults=dict(name=self.image_type_name))[0],
                            attfile=fileObj,
                            file_store=file_store,
                            format=item.file_format,
                            mime_type=item.file_mime_type,
                            size=item.file_size,
                            real_name=item.real_file_name,
                        )

                        ws = create_connection(f"ws://{self.host}:{self.port}/ws/{self.channel}/")
                        ws.send(json.dumps(dict(id=item.id, item_id=res.id, type="uploaded")))
                        ws.close()

                    logger.debug(f'Запись: {item.real_file_name} ({fileObj.name}) завершена.')

                    self.remove(item.full_path)
                    logger.debug(f'Удаление: {item.full_path} завершено.')

        return res, item.id

    @property
    def last_chunk(self):
        res = int(self.dz_dictionary.dztotalchunkcount) == int(self.dz_dictionary.dzchunkindex) + 1
        return res


@JsonResponseWithException()
class DSResponse_UploadImage(Common_UploadImage):
    def __init__(self, request):
        self.upload_image(request=request)
