import logging

from bitfield import BitField
from django.db import transaction , connection
from django.db.models import SmallIntegerField, CharField, TextField

from isc_common.auth.models.user import User
from isc_common.common import unknown
from isc_common.fields.code_field import CodeStrictField
from isc_common.fields.related import ForeignKeyProtect
from isc_common.http.DSRequest import DSRequest
from isc_common.models.audit import Model_withOldId
from isc_common.models.base_ref import BaseRefHierarcyManager, BaseRefHierarcyQuerySet, BaseRef
from lfl_admin.competitions.models.disqualification_condition import Disqualification_condition
from lfl_admin.competitions.models.disqualification_zones import Disqualification_zones
from lfl_admin.region.models.regions import Regions

logger = logging.getLogger(__name__)


class DivisionsQuerySet(BaseRefHierarcyQuerySet):
    pass


class DivisionsManager(BaseRefHierarcyManager):
    def updateFromRequest(self, request, removed=None, function=None):
        request = DSRequest(request=request)
        data = request.get_data()
        id = data.get('id')
        props = data.get('props')

        active = data.get('active')
        if active is True:
            props |= Divisions.props.active
        else:
            props &= ~Divisions.props.active

        favorites = data.get('favorites')
        if favorites is True:
            props |= Divisions.props.favorites
        else:
            props &= ~Divisions.props.favorites

        res = super().filter(id=id).update(props=props)
        return data

    @classmethod
    def props(cls):
        return BitField(flags=(
            ('active', 'active'),  # 0
            ('completed', 'completed'),  # 1
            ('show_news', 'show_news'),  # 2
            ('favorites', 'Избранные'),  # 3
            ('hidden', 'Скрывать ФИО'),  # 4
        ), default=1, db_index=True)

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
        return DivisionsQuerySet(self.model, using=self._db)


class Divisions(BaseRef, Model_withOldId):
    code = CodeStrictField()
    disqualification_condition = ForeignKeyProtect(Disqualification_condition)
    editor = ForeignKeyProtect(User, related_name='Divisions_creator', null=True, blank=True)
    number_of_rounds = SmallIntegerField()
    props = DivisionsManager.props()
    region = ForeignKeyProtect(Regions)
    scheme = CharField(null=True, blank=True, max_length=255)
    top_text = TextField(null=True, blank=True)
    zone = ForeignKeyProtect(Disqualification_zones)

    objects = DivisionsManager()

    @classmethod
    def unknown(cls):
        res, _ = cls.objects.get_or_create(
            code=unknown,
            disqualification_condition=0,
            number_of_rounds=0,
            region=Regions.unknown(),
            zone=Disqualification_zones.unknown()
        )
        return res

    @classmethod
    def get_urls_data( cls , id):
        with connection.cursor() as cursor :
            cursor.execute( '''select (select ici.real_name
                                        from competitions_divisions_images as usi
                                                 join isc_common_images ici on ici.id = usi.image_id
                                                 join isc_common_image_types icit on ici.image_type_id = icit.id
                                        where usi.main_model_id = cd.id
                                          and icit.code = 'scheme'
                                        limit 1)                                                                                                           as real_name,
                                       concat('logic/Imgs/Download/', (
                                           select usi.image_id
                                           from competitions_divisions_images as usi
                                                    join isc_common_images ici on ici.id = usi.image_id
                                                    join isc_common_image_types icit on ici.image_type_id = icit.id
                                           where usi.main_model_id = cd.id
                                             and icit.code = 'scheme'
                                           limit 1), '?', 'code=scheme', '&', 'path=divisions', '&', 'main_model=divisions', '&', 'main_model_id=', cd.id) as image_src
                                from competitions_divisions as cd
                                where cd.id = %s''' , [ id ] )
            record = cursor.fetchone()
            return record

    def __str__(self):
        return f'ID:{self.id}'

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name = 'Супертурниры'
