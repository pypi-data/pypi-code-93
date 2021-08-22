from typing import Callable

import grpc
from jetpack._remote import codec
from jetpack.proto import remote_api_pb2, remote_api_pb2_grpc


class Client:
    def __init__(self):
        self.address = "localhost:50051"
        self.channel = None
        self.stub = None
        self.is_dialed = False  # TODO: Mutex needed?

    def Dial(self):
        self.channel = grpc.insecure_channel(self.address)
        self.stub = remote_api_pb2_grpc.RemoteExecutorStub(self.channel)
        self.is_dialed = True

    def RemoteCall(self, request):
        # Lazily connect to the network. Putting this here so we get a clean
        # API from the get-go, but in practice we might want to do the network
        # connection when a function is *imported* as a stub, rather than on the
        # actual function call (to reduce latency on the call)
        if not self.is_dialed:
            self.Dial()
        return self.stub.RemoteCall(request)

    def remote_function(self, symbol: str) -> Callable:
        def rpc_wrapper(*args, **kwargs):
            request = call_as_proto(symbol, args, kwargs)
            response = self.RemoteCall(request)
            return codec.decode_result(response)

        return rpc_wrapper


def call_as_proto(symbol: str, args, kwargs) -> remote_api_pb2.RemoteCallRequest:
    request = remote_api_pb2.RemoteCallRequest()
    request.method_name = symbol
    request.json_args = codec.encode_args(args, kwargs)
    return request
