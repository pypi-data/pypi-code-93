import logging

from bitfield import BitField
from django.db.models import IntegerField, OneToOneField, PROTECT

from isc_common.fields.related import ForeignKeyProtect
from isc_common.models.audit import Model_withOldId
from isc_common.models.images import Images
from isc_common.models.model_images import Model_imagesQuerySet, Model_images, Model_imagesManager
from lfl_admin.competitions.models.clubs import Clubs
from lfl_admin.user_ext.models.persons import Persons

logger = logging.getLogger(__name__)


class Person_club_photosQuerySet(Model_imagesQuerySet):
    def delete(self):
        return super().delete()

    def create(self, **kwargs):
        return super().create(**kwargs)

    def filter(self, *args, **kwargs):
        return super().filter(*args, **kwargs)


class Person_club_photosManager(Model_imagesManager):

    @classmethod
    def props(cls):
        return BitField(flags=(
            ('main', 'main'),  # 1
        ), default=0, db_index=True)

    @staticmethod
    def getRecord(record):
        res = {
            'id': record.id,
            'editing': record.editing,
            'deliting': record.deliting,
        }
        return res

    def get_queryset(self):
        return Person_club_photosQuerySet(self.model, using=self._db)


class Person_club_photos(Model_images, Model_withOldId):
    club = ForeignKeyProtect(Clubs)
    image = ForeignKeyProtect(Images)
    main_model = ForeignKeyProtect(Persons)
    num = IntegerField(null=True, blank=True)
    props = Person_club_photosManager.props()

    objects = Person_club_photosManager()

    # @classmethod
    # def unknown(cls):
    #     res, _ = cls.objects.get_or_create(club=Clubs.unknown())
    #     return res

    def __str__(self):
        return f'ID:{self.id}'

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name = 'Кросс таблица'
