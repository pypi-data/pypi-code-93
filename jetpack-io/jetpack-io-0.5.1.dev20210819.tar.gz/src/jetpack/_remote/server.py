from concurrent import futures
from typing import Callable, NamedTuple

import grpc
import jsonpickle
from jetpack._remote import codec
from jetpack.proto import remote_api_pb2, remote_api_pb2_grpc

# FuncArgs is used by jsonpickle to capture the arguments to a RPC
FuncArgs = NamedTuple("FuncArgs", [("args", tuple), ("kwargs", dict)])


class Servicer(remote_api_pb2_grpc.RemoteExecutorServicer):
    def __init__(self):
        # TODO: Figure out if we need any locking around the symbol table.
        self.symbol_table = {}  # TODO: lock?

    def export(self, fn):
        symbol = fn.__name__
        self.symbol_table[symbol] = fn
        return symbol

    def RemoteCall(self, request, context):
        fn = self.symbol_table[request.method_name]
        args, kwargs = codec.decode_args(request.json_args)
        result = fn(*args, **kwargs)
        return codec.encode_result(result)


class Server:
    def __init__(self):
        self.servicer = Servicer()
        self.server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        remote_api_pb2_grpc.add_RemoteExecutorServicer_to_server(
            self.servicer, self.server
        )
        self.is_listening = False  # TODO: Mutex needed?

    def Listen(self):
        self.server.add_insecure_port("[::]:50051")
        self.server.start()
        self.is_listening = True

    def export(self, fn):
        # Connect to the network lazily
        if not self.is_listening:
            self.Listen()
        return self.servicer.export(fn)
