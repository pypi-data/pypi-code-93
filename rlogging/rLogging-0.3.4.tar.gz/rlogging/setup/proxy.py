import typing as _T

from rlogging import utils


class LoggingSetupEntityProxy(object):
    """ Интерфейс для настройки логирования, через создание объектов """

    entityType: str
    classPath: str
    name: str

    settings: dict[str, _T.Any]

    def __init__(self, entityType: str, classPath: str, name: _T.Optional[str] = None) -> None:
        self.entityType = entityType
        self.classPath = classPath
        self.name = name

    @classmethod
    def from_entity(cls, entityType: str, entityClass: type, name: _T.Optional[str] = None):
        entityClassPath = '{0}.{1}'.format(
            entityClass.__module__,
            entityClass.__name__
        )

        return cls(entityType, entityClassPath, name)

    def set_settings(self, entitySettings: dict):
        self.settings = entitySettings

    def dump_settings(self) -> dict:
        settings = {
            'entityType': self.entityType,
            'name': self.name,
            'classPath': self.classPath,
        }

        self.settings.update(settings)
        settings['settings'] = self.settings

        return settings

    @staticmethod
    def load_data(dumpData: dict[str, _T.Any]) -> _T.Any:
        entityClass = utils.get_obj(dumpData['entityClassPath'])

        entity = entityClass()

        for field, fieldValue in dumpData['settings'].items():
            setattr(entity, field, fieldValue)

        return entity
