from AsteriskRealtimeData.domain.queue_status.queue_status_vo import QueueStatusVo
from AsteriskRealtimeData.api import Api


class InitializePauseReasons:
    def __init__(self) -> None:
        self.api = Api.QueueStatus

    def initialize_queue_status(self):
        self.api.create(QueueStatusVo(status_code=0, description="Desconocido"))
        self.api.create(QueueStatusVo(status_code=1, description="Sin Uso"))
        self.api.create(QueueStatusVo(status_code=2, description="Hablando"))
        self.api.create(QueueStatusVo(status_code=3, description="Ocupado"))
        self.api.create(QueueStatusVo(status_code=4, description="Invalido"))
        self.api.create(QueueStatusVo(status_code=5, description="Indisponible"))
        self.api.create(QueueStatusVo(status_code=6, description="Ringing"))
        self.api.create(QueueStatusVo(status_code=7, description="RingInUse"))
        self.api.create(QueueStatusVo(status_code=8, description="En Espera"))
        self.api.create(QueueStatusVo(status_code=9, description="Cortando"))


InitializePauseReasons().initialize_queue_status()
