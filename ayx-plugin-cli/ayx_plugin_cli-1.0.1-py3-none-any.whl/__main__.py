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
"""Alteryx CLI - Main program."""
import os
import shutil
import string
import subprocess
from datetime import datetime
from functools import wraps
from pathlib import Path
from typing import Any, Callable, List
from zipfile import ZipFile

from ayx_plugin_cli.ayx_workspace.constants import (
    AYX_WORKSPACE_JSON_PATH,
    BackendLanguage,
    MIN_NODE_JS_VERSION,
    MIN_NPM_VERSION,
    TEMPLATE_TOOL_ICON_PATH,
    TemplateToolTypes,
    YXI_OUTPUT_DIR,
    YxiInstallType,
)
from ayx_plugin_cli.ayx_workspace.models.v1 import (
    AyxWorkspaceV1,
    PythonSettingsV1,
    PythonToolSettingsV1,
    ToolConfigurationV1,
    ToolSettingsV1,
    UiSettingsV1,
)
from ayx_plugin_cli.ayx_workspace.template_tool_settings import (
    TemplateToolSettings,
    input_settings,
    multiple_input_settings,
    multiple_output_settings,
    # optional_settings,
    output_settings,
    # single_input_multi_connection_multi_output_settings,
    single_input_single_output_settings,
)
from ayx_plugin_cli.exceptions import CliError
from ayx_plugin_cli.update_checker import UpdateChecker
from ayx_plugin_cli.validation import (
    NodeJsNotFoundError,
    NodeJsVersionError,
    NpmNotFoundError,
    NpmVersionError,
    validate_node_js,
    validate_npm,
)
from ayx_plugin_cli.version import version as cli_version

import typer

app = typer.Typer(
    help="The Alteryx CLI for SDK Development.",
    callback=UpdateChecker.check_for_updates,  # TODO: Write a general callback that handles app-level checks
)

DODO_PATH = Path(__file__).parent / "ayx_workspace" / "doit" / "dodo.py"


def _handle_cli_errors(func: Callable) -> Callable:
    @wraps(func)
    def decorator(*args: Any, **kwargs: Any) -> Any:
        try:
            return func(*args, **kwargs)
        except CliError as e:
            typer.echo(f"ERROR: {e}".encode())
            raise typer.Exit(1)

    return decorator


def _handle_missing_workspace_json(func: Callable) -> Callable:
    @wraps(func)
    def decorator(*args: Any, **kwargs: Any) -> Any:
        try:
            AyxWorkspaceV1.load()
        except FileNotFoundError:
            raise CliError(
                f"{AYX_WORKSPACE_JSON_PATH} not found in current directory. "
                "Did you initialize the workspace? (sdk-workspace-init)"
            )
        except Exception as e:
            raise CliError(f"Error loading ayx_workspace.json file:\n{e}")

        return func(*args, **kwargs)

    return decorator


def _validate_node(func: Callable) -> Callable:
    # TODO: add this to app-level callback
    @wraps(func)
    def decorator(*args: Any, **kwargs: Any) -> Any:
        try:
            validate_node_js(MIN_NODE_JS_VERSION)
            validate_npm(MIN_NPM_VERSION)
        except NodeJsNotFoundError as e:
            package = "node"
            min_version = MIN_NODE_JS_VERSION
            if isinstance(e, NpmNotFoundError):
                package = "npm"
                min_version = MIN_NPM_VERSION

            raise CliError(
                f"{package} not found. {package} v{min_version} "
                "must be installed and available on the path."
            )
        except NodeJsVersionError as e:
            package = "node"
            if isinstance(e, NpmVersionError):
                package = "npm"

            raise CliError(
                f"Incompatible version of {package} found ({e.bad_version}). "
                f"The minimum required version is {e.min_version}."
            )

        return func(*args, **kwargs)

    return decorator


@app.command()
@_handle_cli_errors
def version() -> None:
    """Display the version of the Alteryx CLI."""
    typer.echo(f"Alteryx CLI Version: {cli_version}")


# TODO: Add help for all arguments


@app.command()
@_handle_cli_errors
@_validate_node
def sdk_workspace_init(
    package_name: str = typer.Option(
        ...,
        prompt="Package Name",
        help="The name of the tool package that you are creating.",
    ),
    tool_category: str = typer.Option(
        default="Python SDK Examples",
        prompt="Tool Category",
        help="The category that tools will belong to in Alteryx Designer.",
    ),
    description: str = typer.Option(
        default="",
        prompt="Description",
        help="The description of the package and use-case of its tools.",
    ),
    author: str = typer.Option(
        default="", prompt="Author", help="The author of the package."
    ),
    company: str = typer.Option(
        default="", prompt="Company", help="The company that is building the package."
    ),
    backend_language: BackendLanguage = typer.Option(
        ...,
        case_sensitive=False,
        prompt="Backend Language",
        help="The language to use for the backend of tools in the package.",
    ),
) -> None:
    """Initialize the current directory as an Alteryx SDK workspace."""
    cur_dir = Path(".")

    workspace_file_path = AYX_WORKSPACE_JSON_PATH
    configuration_directory = cur_dir / "configuration"
    build_directory = cur_dir / "build_tasks"
    dodo_file = cur_dir / "dodo.py"
    backend_directory = cur_dir / "backend"
    ui_directory = cur_dir / "ui"

    paths_to_be_created = [
        workspace_file_path,
        configuration_directory,
        dodo_file,
        build_directory,
        backend_directory,
        ui_directory,
    ]

    existing_paths = [path for path in paths_to_be_created if path.exists()]
    if existing_paths:
        _overwrite_paths_with_prompt(existing_paths)

    workspace_model = AyxWorkspaceV1(
        name=package_name,
        tool_category=tool_category,
        package_icon_path=configuration_directory / "default_package_icon.png",
        author=author,
        company=company,
        copyright=str(datetime.now().year),
        description=description,
        ayx_cli_version=cli_version,
        backend_language=backend_language,
        backend_language_settings=PythonSettingsV1(
            python_version="3.8",
            requirements_local_path=cur_dir
            / "tool_backends"
            / "requirements-local.txt",
            requirements_thirdparty_path=cur_dir
            / "tool_backends"
            / "requirements-thirdparty.txt",
        ),
        tools={},
        tool_version="10.1",
    )

    workspace_model.save()

    _run_doit(["initialize_workspace"], "Workspace initialization")

    typer.echo(f"Created Alteryx workspace in directory: {Path('.').resolve()}")
    typer.echo(f"Workspace settings can be modified in: {workspace_file_path}")

    generate_config_files()


@app.command()
@_handle_cli_errors
@_handle_missing_workspace_json
@_validate_node
def create_ayx_plugin(
    tool_name: str = typer.Option(
        ..., prompt="Tool Name", help="Name of the tool to create."
    ),
    tool_type: TemplateToolTypes = typer.Option(
        default=TemplateToolTypes.SingleInputSingleOutput,
        prompt="Tool Type",
        help="The type of tool to generate.",
    ),
    description: str = typer.Option(
        default="",
        prompt="Description",
        help="The description of the tool to generate.",
    ),
    tool_version: str = typer.Option(
        default="1.0",
        prompt="Tool Version",
        help="The version of the tool to generate.",
    ),
) -> None:
    """Create a new Alteryx plugin in this workspace."""
    workspace = AyxWorkspaceV1.load()

    class_name = _remove_whitespace(tool_name)

    if class_name in [
        tool.backend.tool_class_name for _, tool in workspace.tools.items()
    ]:
        raise CliError(
            f"Tool {class_name} already exists in {AYX_WORKSPACE_JSON_PATH}. Duplicate tool names are prohibited."
        )

    template_tool_settings = _get_template_tool_settings(tool_type)
    tool_configuration = ToolConfigurationV1(
        long_name=tool_name,
        description=description,
        version=tool_version,
        search_tags=[],
        icon_path=Path(".") / (TEMPLATE_TOOL_ICON_PATH % {"tool_name": class_name}),
        input_anchors=template_tool_settings.input_anchors,
        output_anchors=template_tool_settings.output_anchors,
    )

    python_tool_settings = PythonToolSettingsV1(
        tool_module="ayx_plugins", tool_class_name=class_name,
    )

    tool_settings = ToolSettingsV1(
        backend=python_tool_settings,
        ui=UiSettingsV1(),
        configuration=tool_configuration,
    )

    workspace.tools[class_name] = tool_settings
    workspace.save()

    typer.echo(f"Creating {tool_type} plugin: {tool_name}")
    _run_doit(
        ["create_plugin", "--tool_name", class_name, "--tool_type", tool_type.value],
        "Create plugin",
    )
    generate_config_files()


@app.command()
@_handle_cli_errors
@_handle_missing_workspace_json
@_validate_node
def generate_config_files() -> None:
    """Generate the config files for the tools in this workspace."""
    _run_doit(["generate_config_files"], "Generating config files")


@app.command()
@_handle_cli_errors
@_handle_missing_workspace_json
@_validate_node
def create_yxi() -> None:
    """Create a YXI from the tools in this workspace."""
    workspace = AyxWorkspaceV1.load()
    if not workspace.tools:
        raise CliError("No tools in workspace. Add tools before creating YXI.")
    else:
        _run_doit(["create_yxi"], "Creating YXI")


@app.command()
@_handle_cli_errors
@_handle_missing_workspace_json
@_validate_node
def designer_install(
    install_type: YxiInstallType = typer.Option(
        YxiInstallType.USER,
        prompt="Install Type",
        help="The type of install to perform.\n"
        "\nuser -> %APPDATA%\\Alteryx\\Tools"
        "\n, admin -> %ALLUSERSPROFILE%\\Alteryx\\Tools",
    )
) -> None:
    """Install the tools from this workspace into Alteryx Designer."""
    yxi_name = AyxWorkspaceV1.load().name
    Path(f"build/yxi/{yxi_name}.yxi").unlink(missing_ok=True)
    create_yxi()
    install_yxi(YXI_OUTPUT_DIR.resolve() / f"{yxi_name}.yxi", install_type)
    typer.echo(
        "If this is your first time installing these tools, or you have made modifications to your ayx_workspace.json file, please restart Designer for these changes to take effect."
    )


@app.command()
@_handle_cli_errors
def install_yxi(
    yxi_path: Path = typer.Option(
        ...,
        exists=True,
        file_okay=True,
        dir_okay=False,
        writable=False,
        readable=True,
        resolve_path=True,
        prompt="YXI Path",
        help="Path to the YXI file to install.",
    ),
    install_type: YxiInstallType = typer.Option(
        ...,
        prompt="Install Type",
        help="The type of install to perform.\n"
        "\nuser -> %APPDATA%\\Alteryx\\Tools"
        "\n, admin -> %ALLUSERSPROFILE%\\Alteryx\\Tools",
    ),
) -> None:
    """
    Install a YXI into Designer.

    NOTE: This command does NOT support YXI's built for the original Alteryx Python SDK.
    """
    tool_names = _get_yxi_tool_names(yxi_path)
    install_dir = _get_install_dir(install_type)

    files_to_overwrite = []
    for tool_name in tool_names:
        if (install_dir / tool_name).exists():
            files_to_overwrite.append(install_dir / tool_name)

    if files_to_overwrite:
        _overwrite_paths_with_prompt(files_to_overwrite)

    _run_doit(
        ["install_yxi", "--yxi_path", str(yxi_path), "--install_dir", str(install_dir)],
        f"Installing yxi {str(yxi_path)} into designer",
    )


def _get_install_dir(install_type: YxiInstallType) -> Path:
    relative_path = Path("Alteryx") / "Tools"
    user_path = os.environ.get("APPDATA") or os.environ.get("AYX_USER")
    admin_path = os.environ.get("ALLUSERSPROFILE") or os.environ.get("AYX_ADMIN")

    if user_path is None:
        raise CliError("Either APPDATA or AYX_USER must be set.")
    if admin_path is None:
        raise CliError("Either ALLUSERSPROFILE or AYX_ADMIN must be set.")

    return {
        YxiInstallType.USER: Path(user_path) / relative_path,
        YxiInstallType.ADMIN: Path(admin_path) / relative_path,
    }[install_type]


def _get_yxi_tool_names(yxi_path: Path) -> List[str]:
    with ZipFile(yxi_path, "r") as yxi:
        # Assumes all directories that exist at top level of YXI will be tools
        all_dirs = set([Path(path).parent for path in yxi.namelist()])
        tool_names = set(
            [directory.parts[0] for directory in all_dirs if directory.parts]
        )

    return list(tool_names)


def _get_template_tool_settings(tool_type: TemplateToolTypes,) -> TemplateToolSettings:
    """Get the template tool settings based on a tool's type."""
    tool_type_to_template_tool_settings = {
        TemplateToolTypes.Input: input_settings,
        TemplateToolTypes.MultipleInputs: multiple_input_settings,
        TemplateToolTypes.MultipleOutputs: multiple_output_settings,
        # TemplateToolTypes.Optional: optional_settings,
        TemplateToolTypes.Output: output_settings,
        TemplateToolTypes.SingleInputSingleOutput: single_input_single_output_settings,
        # TemplateToolTypes.MultipleInputConnections: single_input_multi_connection_multi_output_settings,
    }
    return tool_type_to_template_tool_settings[tool_type]


def _remove_whitespace(s: str) -> str:
    """Remove whitespace from a string."""
    for whitespace_char in string.whitespace:
        s = s.replace(whitespace_char, "")

    return s


def _overwrite_paths_with_prompt(paths: List[Path]) -> None:
    replace = typer.confirm(
        "\nThe following paths will be overwritten:\n"
        + ("\n".join([str(path.resolve()) for path in paths]))
        + "\n\nConfirm that it is okay to remove these paths."
    )

    if not replace:
        raise typer.Abort()

    for path in paths:
        _delete_path_and_wait_for_cleanup(path)


def _delete_path_and_wait_for_cleanup(path: Path) -> None:
    if path.is_file():
        path.unlink()
    else:
        shutil.rmtree(path)

    while path.exists():
        # Wait for OS to remove file
        pass


def _run_doit(args: List[str], step_name: str) -> None:
    # Note: if the current directory has a dodo.py file, those tasks will be executed instead of the ones in DODO_PATH
    command = [
        "doit",
        "--file",
        str(DODO_PATH),
        "--dir",
        str(Path(".").resolve()),
    ] + args
    typer.echo(f"[{step_name}] started")
    completed_process = _run_command(command, step_name)

    if completed_process.returncode != 0:
        if completed_process.stderr:
            err_str = completed_process.stderr.read().decode("utf-8")
        else:
            err_str = ""
        raise CliError(f"{step_name} failed with error:\n" f"stderr:\n{err_str}\n")
    typer.echo(f"[{step_name}] finished")


def _run_command(args: List[str], step_name: str) -> subprocess.Popen:
    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"

    process = subprocess.Popen(
        args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=os.getcwd(), env=env
    )

    while process.poll() is None:
        output = process.stdout
        if output:
            output_line = output.readline().decode().replace("\n", "")
            if len(output_line) > 0:
                typer.echo(f"[{step_name}] {output_line}")
        else:
            break

    return process


def main() -> None:
    """Define the main Entry point to typer."""
    app()


if __name__ == "__main__":
    main()
