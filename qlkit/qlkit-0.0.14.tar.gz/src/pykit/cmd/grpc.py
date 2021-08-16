#!/usr/bin/env python
# -*- coding:utf-8 -*-
import signal

import grpc
from concurrent import futures

from .. import log
from . import Server
from ..config import DEFAULT_CONFIG
from ..database.transaction import TransactionFactory


def load_credential_from_file(file_absolute_path):
    with open(file_absolute_path, 'rb') as f:
        return f.read()


def create_grpc_credentials(server_cert_path, server_cert_key_path,
                            root_cert_path=None) -> grpc.ServerCredentials:
    """
    create gRPC server credentials
    :param server_cert_path:
    :param server_cert_key_path:
    :param root_cert_path: if provided, gRPC client must be authenticated.
    :return:
    """
    server_cert_content = load_credential_from_file(server_cert_path)
    server_cert_key_content = load_credential_from_file(server_cert_key_path)
    if root_cert_path:
        root_cert_content = load_credential_from_file(root_cert_path)
        server_credentials = grpc.ssl_server_credentials(
            (server_cert_key_content, server_cert_content),
            root_cert_content,
            require_client_auth=True
        )
    else:
        server_credentials = grpc.ssl_server_credentials(
            (server_cert_key_content, server_cert_content)
        )
    return server_credentials


def create_grpc_server(address: str, max_thread_workers: int,
                       maximum_concurrent_rpcs: int = None,
                       server_credentials: grpc.ServerCredentials = None,
                       interceptors: grpc.ServerInterceptor = None,
                       channel_options: type = None,
                       compression: grpc.Compression = None) -> grpc.Server:
    """Create gRPC server
    :param address: "127.0.0.1:8888"
    :param max_thread_workers:
    :param maximum_concurrent_rpcs
    :param server_credentials: gRPC traffic credentials.
    :param interceptors: https://grpc.github.io/grpc/python/grpc.html#service-side-interceptor
           interceptors use case https://github.com/grpc/grpc/blob/master/examples/python/interceptors
    :param channel_options: https://grpc.github.io/grpc/python/glossary.html#term-channel_arguments
    :param compression: grpc.Compression.NoCompression
    :return:
    """
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=max_thread_workers),
        maximum_concurrent_rpcs=maximum_concurrent_rpcs,
        interceptors=interceptors,
        options=channel_options,
        compression=compression
        )
    if server_credentials:
        server.add_secure_port(address, server_credentials)
    else:
        server.add_insecure_port(address)
    return server


class GRPCServer(Server):
    def __init__(self, grpc_runtime_server: grpc.Server,
                 config: dict = None):
        self.runtime_server = grpc_runtime_server
        self.config = config if config else DEFAULT_CONFIG

    def start(self):
        self.runtime_server.start()

    def graceful_stop(self):
        self.runtime_server.stop(self.config["grpc_graceful_shutdown"])

    def handle_term_signal(self):
        self.graceful_stop()

    def run_forever(self):
        self.runtime_server.wait_for_termination()


def run_grpc_server_forever(server: GRPCServer):
    """
    Run gRPC server as daemon process.
    While received SIGTERM signals, it will shutdown gracefully.
    :return:
    """
    logger = log._get_root_logger()
    server.start()
    logger.info("gRPC server start")

    def handle_signal_term(*_):
        logger.info(
            f"gRPC server received term signal, will shutdown "
            f"after {server.config['grpc_graceful_shutdown']} seconds"
        )
        server.graceful_stop()
        logger.info("gRPC server terminated")

    signal.signal(signal.SIGTERM, handle_signal_term)

    server.run_forever()
