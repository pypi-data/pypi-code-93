import abc


class EVSEConnector(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def lock(self):
        """Lock the charging plug to car or charger."""
        return

    @abc.abstractmethod
    def unlock(self):
        """Unlock the charging plug from car or charger."""
        return

    @abc.abstractmethod
    def get_lock_status(self) -> bool:
        """Check if charger is locked."""
        pass

    @abc.abstractmethod
    def start_charge(self):
        """Begin charging vehicle."""
        return

    @abc.abstractmethod
    def stop_charge(self):
        """Stop charging vehicle."""
        return

    @abc.abstractmethod
    def set_current_limit(self, amperage: float):
        """Set the current flow limit."""
        return

    @abc.abstractmethod
    def get_current_limit(self) -> float:
        """Check the current flow limit."""
        pass

    @abc.abstractmethod
    def get_current(self) -> float:
        """Check the current presently flowing through the charger."""
        pass

    @abc.abstractmethod
    def get_charge_status(self) -> bool:
        """Check if the charger is actively charging or not."""
        pass
