import logging
import os
from os.path import getsize

from django.conf import settings

from isc_common.models.audit import AuditModel , AuditManager , AuditQuerySet
from isc_common.ssh.ssh_client import SSH_Client_settings

logger = logging.getLogger(__name__)


class Model_imagesQuerySet(AuditQuerySet):
    pass


class Model_imagesManager(AuditManager):

    @staticmethod
    def getRecord(record):
        res = {
            'id': record.id,
        }
        return res

    def get_queryset(self):
        return Model_imagesQuerySet(self.model, using=self._db)


class ImageNotFound(Exception):
    pass


class Model_images(AuditModel):
    @classmethod
    def get_image(cls, file_name, path=None):
        if file_name is None:
            return None

        if os.altsep is not None:
            have_path = file_name.find(os.altsep) != -1
        else:
            have_path = file_name.find(os.sep) != -1

        if have_path:
            if os.altsep is None:
                file_name1 = f'{settings.OLD_SITE_BASE_DIR}{file_name}'.replace(os.sep, '\\')
            else:
                file_name1 = f'{settings.OLD_SITE_BASE_DIR}{file_name}'.replace(os.altsep, os.sep)
            try:
                return cls.objects.get(path__upper=file_name1.upper()).path
            except cls.DoesNotExist:
                return None

        query = cls.objects.filter(file_name=file_name).order_by('-date')
        if query.count() == 0:
            return None
        else:
            _list = list(map(lambda x: x.path, query))
            if path is None:
                return _list[0]

            for item in _list:
                if item.find(path) != -1:
                    return item
            return None

    @classmethod
    def update_or_create_image(cls, main_model, code, path, file_name=None, self_image_field=False, name=None, exception=True, full_name_image=None, image_field_name=None, pk_name='id', defaults=None, update_from_sftp=False):
        from isc_common.models.image_types import Image_types
        from isc_common.models.images import Images
        from lfl_admin.common.models.site_lfl_images import Site_lfl_images

        if name is None:
            name = code

        if file_name is None or (file_name is not None and file_name.strip() == ''):
            return

        if full_name_image is None:
            full_name_image = Site_lfl_images.get_image(file_name=file_name, path=path)

        if full_name_image is not None:

            image_type, created = Image_types.objects.get_or_create(code=code, defaults=dict(name=name))
            image, created = Images.objects.update_or_create(image_type=image_type, real_name=full_name_image)

            zero = False

            full_name_image_replaced = full_name_image.replace(settings.PATH_IMAGES_REPLACE.get('old_path'), settings.PATH_IMAGES_REPLACE.get('new_path'))
            full_name_image_replaced = full_name_image_replaced.replace(os.altsep if os.altsep is not None else '\\', os.sep)

            if settings.REC_IMAGE is True:
                if os.path.exists(full_name_image_replaced):
                    image1, created = Images.create_update(id=image.id, image_type=image_type, real_file_name=full_name_image_replaced)

                elif update_from_sftp is True:
                    file_name = os.path.split(full_name_image_replaced)[1]
                    localpath = f"{settings.PATH_IMAGES_REPLACE.get('tmp_path')}{file_name}"
                    SSH_CLIENT = SSH_Client_settings()
                    SSH_CLIENT.get(remotepath=full_name_image_replaced, localpath=localpath)

                    if getsize(localpath) == 0:
                        os.remove(localpath)
                        logger.debug(f'{localpath} is zero size')
                        zero = True
                    elif os.path.exists(localpath):
                        image1, created = Images.create_update(
                            id=image.id,
                            image_type=image_type,
                            real_file_name=full_name_image,
                            tmp_file_name=localpath
                        )

            if not zero:
                if self_image_field is False:
                    return cls.objects.update_or_create(image=image, main_model=main_model, defaults=defaults)
                else:
                    eval(f'main_model._meta.concrete_model.objects.filter({pk_name}=main_model.{pk_name}).update({image_field_name}=image)', dict(), dict(image=image, main_model=main_model))

                logger.debug(f'{file_name} : found')

        elif file_name is not None:
            if exception is True:
                raise ImageNotFound(f'{file_name} : not found')
            else:
                logger.debug(f'{file_name} : not found !!!')
        return None, None

    objects = Model_imagesManager()

    def __str__(self):
        return f'ID:{self.id}'

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name = 'Базовый класс'
        abstract = True
