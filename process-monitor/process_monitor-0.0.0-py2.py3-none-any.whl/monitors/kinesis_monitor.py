from .monitor import Monitor


class ConsumerMonitor(Monitor):
    """A consumer monitor that extends base monitor by adding friendly methods to track received records count."""

    def init_info(self):
        super().init_info()
        self.info.setdefault('received_records', 0)
        self._received_records = self.info.get('received_records')

    def received_record(self):
        """Adds to received_records count."""
        self._received_records += 1
        self.info.update({'received_records': self._received_records})
