# Copyright (C) 2021 Alteryx, Inc. All rights reserved.
#
# Licensed under the ALTERYX SDK AND API LICENSE AGREEMENT;
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    https://www.alteryx.com/alteryx-sdk-and-api-license-agreement
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Entrypoint for tracer bullet application."""
import logging

from ayx_python_sdk.providers.amp_provider.grpc_util import SocketAddress
from ayx_python_sdk.providers.amp_provider.logger_config import configure_logger
from ayx_python_sdk.providers.amp_provider.plugin_class_loader import load_plugin_class
from ayx_python_sdk.providers.amp_provider.repositories import GrpcRepository
from ayx_python_sdk.providers.amp_provider.repositories.plugin_class_repository import (
    PluginClassRepository,
)
from ayx_python_sdk.providers.amp_provider.sdk_tool_runner import SdkToolRunner

import typer

app = typer.Typer()


@app.command()
def version() -> None:
    """Get the version of the CLI."""
    typer.echo("Version 1.0.0")


@app.command()
def start_sdk_tool_service(
    plugins_package: str,
    tool_name: str,
    sdk_engine_server_address: str = "localhost:65000",
) -> None:
    """Start the SDK Tool service."""
    configure_logger()
    logger = logging.getLogger()

    try:
        _log_info(f"Starting {tool_name} tool with AMP Provider.")

        PluginClassRepository().save_plugin_class(
            load_plugin_class(plugins_package, tool_name)
        )

        runner = SdkToolRunner(
            SocketAddress.from_address_str(sdk_engine_server_address)
        )

        try:
            runner.start_service()
        except Exception as e:
            _log_error(f"ERROR: Couldn't start service.")
            logger.exception(e)
            raise typer.Exit(code=1)

        _log_info(
            f"Successfully started python server at {GrpcRepository().get_sdk_tool_server_address().address}."
        )

        return_status = runner.handshake_with_sdk_engine_service()

        _log_info(
            f"SDK ENGINE CLIENT: Successfully called into SDK Engine service with response:\n{return_status}"
        )

        runner.wait_for_termination()
    except Exception as e:
        typer.echo(f"EXCEPTION: {e}")
        logger.exception(e)
        raise


def _log_info(msg: str) -> None:
    logger = logging.getLogger()
    logger.info(f"INFO: {msg}")
    typer.echo(f"INFO: {msg}")


def _log_error(msg: str) -> None:
    logger = logging.getLogger()
    logger.error(f"ERROR: {msg}")
    typer.echo(f"ERROR: {msg}")


def main() -> None:
    """Entrypoint method for the tracer bullet application."""
    app()


if __name__ == "__main__":
    main()
