import random
import string
import typing as _T

from rlogging.setup.proxy import LoggingSetupEntityProxy


def random_entity_name(length):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))


class BaseLoggingEntity(object):
    """ Базовый класс сущности логирования.

    Содержит функции для переноса настроек

    """

    __setup_fields__: _T.Iterable[str]

    def __init__(self, name: str) -> None:
        self.name = name

    @classmethod
    def setup(cls, entityType, **kwargs) -> LoggingSetupEntityProxy:
        try:
            settingsFields = cls.__setup_fields__

        except AttributeError:
            raise ValueError(
                'У сущности логирования "{0}" не объявлен атирубут "__setup_fields__",'
                'который указывает поля настройки'.format(
                    cls.__name__
                )
            )

        newEntityName = '{0}:{1}'.format(
            entityType, random_entity_name(10)
        )

        kwargs.setdefault('name', newEntityName)

        settings = {
            'name': newEntityName,
        }

        for field in settingsFields:
            if field in kwargs:
                settings[field] = kwargs.get(field)

            elif hasattr(cls, field):
                settings[field] = getattr(cls, field)

            else:
                raise TypeError(
                    'У сущности логирования "{0}" указано поле "{1}" как используемое при настройке. '
                    'Но оно не получено и не установленно по умолчанию.'.format(
                        cls.__name__,
                        field
                    )
                )

        entityName = settings.get('name')

        entityProxy = LoggingSetupEntityProxy.from_entity(entityType, cls, entityName)
        entityProxy.set_settings(settings)
        return entityProxy

    def load_data(self, dumpData: dict[str, _T.Any]):
        for field, fieldValue in dumpData.items():
            setattr(self, field, fieldValue)

    @classmethod
    def cls_load_data(cls, dumpData: dict[str, _T.Any]):
        entityName = dumpData['name']
        newObject = cls(entityName)
        newObject.load_data(dumpData)
        return newObject
