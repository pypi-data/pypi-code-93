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
"""Task definition for creating a YXI for the workspace."""
import shutil
import tempfile
from pathlib import Path
from typing import Callable, Dict, Generator, List, Tuple, Union

from ayx_plugin_cli.ayx_workspace.constants import (
    AYX_WORKSPACE_ARTIFACT_EXTENSIONS,
    AYX_WORKSPACE_JSON_PATH,
    BUILD_CACHE_DIR,
    BackendLanguage,
    TEMPLATE_TOOL_CONFIG_DIR,
    TEMPLATE_TOOL_UI_DIR,
    WORKSPACE_CONFIG_DIR,
    YXI_OUTPUT_DIR,
)
from ayx_plugin_cli.ayx_workspace.models.v1 import (
    AyxWorkspaceV1,
    ToolSettingsV1,
)
from ayx_plugin_cli.node_js_helpers import run_npm


def task_create_yxi() -> Generator[Dict, None, None]:
    """Create a YXI from the tools in the workspace."""
    workspace = AyxWorkspaceV1.load()

    backend_artifact_name = (
        "main" + AYX_WORKSPACE_ARTIFACT_EXTENSIONS[workspace.backend_language]
    )

    backend_artifact_path = Path(backend_artifact_name)
    all_tools = [tool.backend.tool_class_name for _, tool in workspace.tools.items()]
    actions: List[Union[Callable, List[str], Tuple]] = [
        lambda: print(f"Creating {workspace.name}.yxi..."),
        (_build_action, [all_tools]),
        generate_build_artifact_command(
            workspace.backend_language, BUILD_CACHE_DIR, backend_artifact_path
        ),
    ]

    yield {
        "task_dep": ["generate_config_files"],
        "actions": actions,
        "targets": [backend_artifact_path],
        "clean": True,
        "name": "build_artifacts",
    }

    yield {
        "file_dep": [backend_artifact_path, AYX_WORKSPACE_JSON_PATH],
        "task_dep": ["generate_config_files"],
        "actions": [(create_yxi, [workspace, backend_artifact_path])],
        "targets": [YXI_OUTPUT_DIR / f"{workspace.name}.yxi"],
        "clean": True,
        "name": "create_yxi",
    }


def create_yxi(workspace: AyxWorkspaceV1, backend_artifact_path: Path) -> None:
    """Bundle workspace tools into a yxi."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir_path = Path(temp_dir)
        copy_top_level_files(workspace, temp_dir_path)
        for _, tool in workspace.tools.items():
            copy_tool(tool, temp_dir_path)

        make_archive(backend_artifact_path, workspace, temp_dir_path)


def copy_top_level_files(workspace: AyxWorkspaceV1, temp_dir: Path) -> None:
    """Copy top-level config xml and icon files from workspace directory into temp directory for yxi creation."""
    top_level_config = WORKSPACE_CONFIG_DIR / "Config.xml"
    shutil.copy(top_level_config, temp_dir)
    shutil.copy(workspace.package_icon_path, temp_dir)


def copy_tool(tool: ToolSettingsV1, temp_dir: Path) -> None:
    """Copy tool files from workspace directory into temp directory for yxi creation."""
    tool_name = tool.backend.tool_class_name
    tool_config_dir = Path(TEMPLATE_TOOL_CONFIG_DIR % {"tool_name": tool_name})
    tool_config_file = tool_config_dir / f"{tool_name}Config.xml"
    tool_config_icon = Path(tool.configuration.icon_path).resolve()

    manifest_json = tool_config_dir / "manifest.json"

    tool_folder = temp_dir / tool_name
    tool_folder.mkdir()
    shutil.copy(tool_config_file, tool_folder)
    shutil.copy(manifest_json, tool_folder)
    shutil.copy(tool_config_icon, tool_folder)

    tool_ui_artifact_dir = (
        Path(".") / (TEMPLATE_TOOL_UI_DIR % {"tool_name": tool_name}) / "dist"
    )
    for path in tool_ui_artifact_dir.iterdir():
        if path.is_file() and path.suffix != ".gz":
            shutil.copy(path, tool_folder)


def make_archive(
    artifact_path: Path, workspace: AyxWorkspaceV1, temp_dir: Path
) -> None:
    """Zip workspace and rename to yxi file."""
    YXI_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    shutil.copy(artifact_path, Path(temp_dir) / list(workspace.tools)[0])
    shutil.make_archive(f"{workspace.name}.yxi", "zip", temp_dir)
    shutil.move(f"{workspace.name}.yxi.zip", YXI_OUTPUT_DIR / f"{workspace.name}.yxi")


def generate_build_artifact_command(
    language: BackendLanguage, cache_dir: Path, output_path: Path
) -> List[str]:
    """Delegate call to backend's build artifact command."""
    try:
        return {
            BackendLanguage.Python: [
                "ayx_python_sdk",
                "build-artifact",
                "--dependency-cache-dir",
                str(cache_dir.resolve()),
                "--output-path",
                str(output_path.resolve()),
            ]
        }[language]
    except KeyError:
        raise NotImplementedError(f"{language} is not supported as a backend language.")


def _build_action(all_tools: List[str]) -> None:
    for tool_name in all_tools:
        ui_dir = TEMPLATE_TOOL_UI_DIR % {"tool_name": tool_name}
        completed_process = run_npm(["install"], cwd=Path(".") / ui_dir,)
        if completed_process.returncode != 0:
            raise RuntimeError(
                f"'npm install' on directory {ui_dir} failed with:\n"
                f"stdout:\n{completed_process.stdout}\n\n"
                f"stderr:{completed_process.stderr}"
            )
        completed_process = run_npm(["run", "build"], cwd=Path(".") / ui_dir,)

        if completed_process.returncode != 0:
            raise RuntimeError(
                f"'npm run build' on directory {ui_dir} failed with:\n"
                f"stdout:\n{completed_process.stdout}\n\n"
                f"stderr:{completed_process.stderr}"
            )
