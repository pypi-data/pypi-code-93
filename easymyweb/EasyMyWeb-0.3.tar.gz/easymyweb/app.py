from flask import Flask
from typing import *
from .runner import run as runner_run


class EasyMyWeb(Flask):
    def __init__(
        self,
        import_name: str,
        *args, **kwargs
    ):
        super().__init__(import_name=import_name,
                         *args, **kwargs)

    # def run(self, host: Optional[str] = None, port: Optional[int] = None, debug=False, **kwargs):
    #     if debug:
    #         self.logger.warning(
    #             "EasyMyWebRunner does not support debug mode. Using fallback server and it may cause a lower performance. Also, please disable debug in production environment.")
    #         Flask.run(self, host=host, port=port, debug=debug, **kwargs)
    #     else:
    #         runner_run(self, host=host, port=port, **kwargs)
