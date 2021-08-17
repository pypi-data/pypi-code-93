from flask import Flask
from typing import *
import uvicorn


def run(app: Flask, host: Optional[str] = None, port: Optional[int] = None, debug=False, **kwargs):
    if not port:
        port = 5000
    if not host:
        host = "127.0.0.1"
    if debug:
        raise NotImplementedError("debug mode is not supported by uvicorn. ")

    uvicorn.run(app, host=host, port=port, **kwargs)
