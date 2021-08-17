from AsteriskRealtimeData.domain.pause_reason.pause_reasons_vo import PauseReasonVo
from AsteriskRealtimeData.domain.pause_reason.pause_reason import PauseReason
from AsteriskRealtimeData.api import Api


class InitializePauseReasons:
    def __init__(self) -> None:
        self.api = Api.PauseReason

    def initialize_pause_reasons(self):
        self.api.create(PauseReasonVo(pause_code="100001", description="Conectado", paused=False))
        self.api.create(PauseReasonVo(pause_code="100002", description="Disponible", paused=False))
        self.api.create(PauseReasonVo(pause_code="200001", description="Desconectado", paused=True))
        self.api.create(PauseReasonVo(pause_code="200002", description="En colación", paused=True))
        self.api.create(PauseReasonVo(pause_code="200003", description="Baño", paused=True))
        self.api.create(PauseReasonVo(pause_code="200004", description="En Reunión", paused=True))
        self.api.create(PauseReasonVo(pause_code="200005", description="Atención vendedor", paused=True))
        self.api.create(PauseReasonVo(pause_code="300001", description="Hablando", paused=True))
        self.api.create(PauseReasonVo(pause_code="300002", description="ACW (After Call Work)", paused=True))
        self.api.create(PauseReasonVo(pause_code="300003", description="Ocupado", paused=True))
        self.api.create(PauseReasonVo(pause_code="300004", description="Recibiendo llamada", paused=True))
        self.api.create(PauseReasonVo(pause_code="300005", description="Discando", paused=True))
        self.api.create(PauseReasonVo(pause_code="000000", description="Estado desconocido", paused=True))


InitializePauseReasons().initialize_pause_reasons()
