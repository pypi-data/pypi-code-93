import os
from typing import Callable

import grpc
from jetpack._remote import codec
from jetpack.config import namespace, symbols
from jetpack.proto import remote_api_pb2, remote_api_pb2_grpc


class NoControllerAddressError(Exception):
    pass


class Client:
    def __init__(self):
        host = os.environ.get(
            "JETPACK_CONTROLLER_HOST",
            "remotesvc.jetpack-runtime.svc.cluster.local",
        )
        port = os.environ.get("JETPACK_CONTROLLER_PORT", "443")
        self.address = f"{host}:{port}"
        self.channel = None
        self.stub = None
        self.is_dialed = False  # TODO: Mutex needed?
        self.dry_run = False

    def dial(self):
        if not self.address:
            raise NoControllerAddressError("Controller address is not set")
        # Since this is inter-cluster communication, insecure is fine.
        # In the future this won't even leave the pod, and use a sidecar so
        # it will be localhost.
        self.channel = grpc.insecure_channel(self.address)
        self.stub = remote_api_pb2_grpc.RemoteExecutorStub(self.channel)
        self.is_dialed = True

    def launch_job(self, qualified_name: str, module: str):
        """Launches a k8s job. For now this function assumes job will live in
        same namespace where the launcher is located.

        Keyword arguments:
        qualified_name -- qualified name as produced by utils.qualified_func_name
        module -- jetpack module where the job resides. Used to determine correct
        docker image.
        """
        job = remote_api_pb2.RemoteJob(
            container_image=symbols.find_image_for_module(module),
            qualified_symbol=qualified_name,
            namespace=namespace.get(),
        )
        request = remote_api_pb2.LaunchJobRequest(job=job)

        if self.dry_run:
            print("Dry Run:", request)
            return

        # If dialing is slow, consider dialing earlier.
        if not self.is_dialed:
            self.dial()
        return self.stub.LaunchJob(request)
