# coding: utf-8
from __future__ import absolute_import
from __future__ import unicode_literals

from abc import ABCMeta
from abc import abstractmethod

from django.http.response import JsonResponse

from m3.actions import Action
from m3.actions import ActionPack
from six import text_type
from six import with_metaclass

from m3_gar_client.utils import correct_keyboard_layout

from .utils import HouseLoader
from .utils import PlaceLoader
from .utils import StreetLoader


class ActionBase(with_metaclass(ABCMeta, Action)):
    """
    Базовый класс для обработчиков запросов на поиск данных в ГАР.
    """

    @abstractmethod
    def _get_loader(self, context):
        """Возвращает загрузчик данных.

        :rtype: m3_gar_client.backends.m3_rest_gar.proxy.utils.LoaderBase
        """

    def context_declaration(self):
        return {
            'filter': {
                'type': 'unicode',
                'default': '',
            },
        }

    def run(self, request, context):
        context.filter = correct_keyboard_layout(context.filter)

        loader = self._get_loader(context)
        rows = loader.load()

        return JsonResponse({
            'rows': rows,
            'total': len(rows),
        })


class PlaceSearchAction(ActionBase):
    """
    Обработчик запросов на поиск населенных пунктов.
    """

    url = '/search/place'

    def _get_loader(self, context):
        # pylint: disable=abstract-class-instantiated
        return PlaceLoader(context.filter)


class ParentMixin(object):

    def context_declaration(self):
        result = super(ParentMixin, self).context_declaration()

        result.update({
            'parent': {
                'type': 'unicode',
            },
        })

        return result


class StreetSearchAction(ParentMixin, ActionBase):
    """
    Обработчик запросов на поиск улиц в населенном пункте.
    """

    url = '/search/street'

    def _get_loader(self, context):
        # pylint: disable=abstract-class-instantiated
        return StreetLoader(context.filter, parent_id=text_type(context.parent))


class HouseSearchAction(ParentMixin, ActionBase):
    """
    Обработчик запросов на поиск домов.
    """

    url = '/search/house'

    def _get_loader(self, context):
        # pylint: disable=abstract-class-instantiated
        return HouseLoader(context.filter, parent_id=context.parent)


class Pack(ActionPack):
    """
    Набор действий для проксирования запросов к серверу ГАР.
    """

    url = '/gar'

    def __init__(self):
        super(Pack, self).__init__()

        self.place_search_action = PlaceSearchAction()
        self.street_search_action = StreetSearchAction()
        self.house_search_action = HouseSearchAction()

        self.actions.extend((
            self.place_search_action,
            self.street_search_action,
            self.house_search_action,
        ))
