from rlogging.entities.base import BaseRecord
from rlogging.entities.base.main import BaseLoggingEntity


class BasePrinter(BaseLoggingEntity):
    """ Базовый принтер """

    def processing(self, record: BaseRecord, recordString: str):
        raise AttributeError('Принтер "{0}" не переназначил функцию принта лога'.format(
            self.__class__.__name__
        ))
