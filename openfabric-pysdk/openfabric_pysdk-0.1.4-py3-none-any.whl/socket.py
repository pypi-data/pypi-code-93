import time
import zlib

from flask import Flask, request
from flask_socketio import SocketIO, Namespace, emit
from marshmallow import Schema

from openfabric_pysdk.register import OpenfabricRegister
from openfabric_pysdk.util import Util


class OpenfabricSocket(Namespace):
    __socket_io = None
    __session = None

    # def run(self, app):
    #     self.__socket_io.run(app)

    def __init__(self, socket_namespace, socket_session, app: Flask):
        super().__init__(socket_namespace)
        self.__session = socket_session
        # Set this variable to "threading", "eventlet" or "gevent" to test the
        # different async modes, or leave it set to None for the application to choose
        # the best option based on installed packages.
        async_mode = "eventlet"
        self.__socket_io = SocketIO(app, async_mode=async_mode, cors_allowed_origins='*')
        self.__socket_io.on_namespace(self)
        self.__socket_io.run(app)

    def on_execute(self, data):
        start = time.time()
        # print(f'Request from {request.sid} on {request.host}')
        # Uncompress data
        uncompressed = zlib.decompress(data)
        input_json = uncompressed.decode('utf-8')
        # Input Object
        object_clazz = Util.import_class(OpenfabricRegister.input_type)
        instance = object_clazz(input_json)
        result = OpenfabricRegister.execution_function(instance)
        schema_clazz: Schema = Util.import_class(OpenfabricRegister.output_type.schema)
        json_output = schema_clazz(many=False).dump(result)
        emit('response', json_output)
        end = time.time()
        duration = round(end - start, 4)
        print(f"Processing time: {duration}s")

    def on_connect(self):
        print(f'Client connected {request.sid} on {request.host}')

    def on_disconnect(self):
        print(f'Client disconnected {request.sid} on {request.host}')
