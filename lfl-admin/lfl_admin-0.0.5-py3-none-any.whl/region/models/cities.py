import logging

from isc_common.fields.related import ForeignKeyProtect
from isc_common.models.audit import Model_withOldId
from isc_common.models.base_ref import BaseRefManager, BaseRefQuerySet, BaseRef
from lfl_admin.region.models.regions import Regions

logger = logging.getLogger(__name__)


class CitiesQuerySet(BaseRefQuerySet):
    pass


class CitiesManager(BaseRefManager):

    @staticmethod
    def getRecord(record):
        res = {
            'id': record.id,
            'code': record.code,
            'name': record.name,
            'description': record.description,
            'editing': record.editing,
            'deliting': record.deliting,
        }
        return res

    def get_queryset(self):
        return CitiesQuerySet(self.model, using=self._db)


class Cities(BaseRef, Model_withOldId):
    region = ForeignKeyProtect(Regions, null=True, blank=True)

    objects = CitiesManager()

    def __str__(self):
        return f'ID:{self.id} name: {self.name} region: [{self.region}]'

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name = 'Города'
