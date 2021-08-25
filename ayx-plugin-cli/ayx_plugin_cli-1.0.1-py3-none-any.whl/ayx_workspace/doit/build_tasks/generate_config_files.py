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
"""Task definition for generation of config files."""
import os
from collections import defaultdict
from pathlib import Path
from typing import Dict, Generator, List, Tuple

from ayx_plugin_cli.ayx_workspace.constants import (
    AYX_WORKSPACE_JSON_PATH,
    WORKSPACE_CONFIG_DIR,
)
from ayx_plugin_cli.ayx_workspace.models.v1 import (
    AyxWorkspaceV1,
    ManifestV1,
    ToolSettingsV1,
)

import xmltodict

CONFIG_XML_NAME = "Config.xml"


def task_generate_config_files() -> Generator[Dict, None, None]:
    """Generate the config files for the workspace."""
    yield {
        "name": "generate_config_xml",
        "targets": [WORKSPACE_CONFIG_DIR / CONFIG_XML_NAME],
        "file_dep": [AYX_WORKSPACE_JSON_PATH],
        "actions": [generate_config_xml],
        "clean": True,
        "verbosity": 2,
    }
    workspace = AyxWorkspaceV1.load()

    if workspace.tools:
        tools = workspace.tools
        (
            tool_config_xml_targets,
            manifest_json_targets,
            icon_file_targets,
        ) = generate_targets(tools)

        yield {
            "name": "generate_tool_config_xml",
            "targets": tool_config_xml_targets,
            "file_dep": [AYX_WORKSPACE_JSON_PATH],
            "actions": [generate_tool_xmls],
            "clean": True,
            "verbosity": 2,
        }

        yield {
            "name": "generate_tool_manifest_json",
            "targets": manifest_json_targets,
            "file_dep": [AYX_WORKSPACE_JSON_PATH],
            "actions": [generate_manifest_json],
            "clean": True,
            "verbosity": 2,
        }


def generate_config_xml() -> None:
    """Parse the ayx_workspace.json to generate the top-level Config XML."""
    print("Generating top level config XML file...")
    workspace = AyxWorkspaceV1.load()
    config_xml = {
        "AlteryxJavaScriptPlugin": {
            #  TODO: Figure out what values to use for @EngineDLL and @SDKVersion -- hard coded for now
            "EngineSettings": {
                "@EngineDLL": "Python",
                "@SDKVersion": workspace.tool_version,
            },
            "Properties": {
                "MetaInfo": {
                    "Name": workspace.name,
                    "Description": workspace.description,
                    "CategoryName": workspace.tool_category,
                    "ToolVersion": workspace.tool_version,
                    "Author": workspace.author,
                    "Company": workspace.company,
                    "Copyright": workspace.copyright,
                    "Icon": Path(workspace.package_icon_path).name,
                }
            },
        }
    }

    config_xml_path = WORKSPACE_CONFIG_DIR / CONFIG_XML_NAME
    _output_dict_to_xml(config_xml, config_xml_path)


def generate_tool_xmls() -> None:
    """Parse the ayx_workspace.json to generate the tool config XMLs for each tool that is specified in the workspace json."""
    print("Generating tool configuration XMLs...")

    workspace = AyxWorkspaceV1.load()
    tools = workspace.tools
    for _, tool in tools.items():
        tool_name = tool.backend.tool_class_name
        print(f"Generating {tool_name} XML...")
        os.makedirs(WORKSPACE_CONFIG_DIR / tool_name, exist_ok=True)

        tool_config = tool.configuration
        input_anchors = tool_config.input_anchors
        output_anchors = tool_config.output_anchors
        input_connections_dict = {}
        output_connections_dict = {}
        if input_anchors:
            input_connections_dict = _create_connection_dict(input_anchors)

        if output_anchors:
            output_connections_dict = _create_connection_dict(output_anchors)

        entrypoint = get_entrypoint(len(input_anchors))

        config_xml = {
            "AlteryxJavaScriptPlugin": {
                "EngineSettings": {
                    "@EngineDll": "SdkEnginePlugin.dll",
                    "@EngineDllEntryPoint": entrypoint,
                    "@SDKVersion": workspace.tool_version,
                },
                "SdkSettings": {"@Manifest": "True", "@Language": "Python"},
                "GuiSettings": {
                    "@Html": "index.html",
                    "@Icon": tool_config.icon_path.name,
                    "@SDKVersion": workspace.tool_version,
                    "InputConnections": input_connections_dict,
                    "OutputConnections": output_connections_dict,
                },
                "Properties": {
                    "MetaInfo": {
                        "Name": tool_config.long_name,
                        "Description": tool_config.description,
                        "ToolVersion": tool_config.version,
                        "CategoryName": workspace.tool_category,
                        "SearchTags": ", ".join(tool_config.search_tags),
                        "Author": workspace.author,
                        "Company": workspace.company,
                        "Copyright": workspace.copyright,
                    }
                },
            }
        }

        config_xml_path = WORKSPACE_CONFIG_DIR / tool_name / f"{tool_name}Config.xml"
        _output_dict_to_xml(config_xml, config_xml_path)

    print("Done!")


def generate_manifest_json() -> None:
    """Parse the ayx_workspace.json to generate the manifest.json that corresponds to each tool."""
    workspace = AyxWorkspaceV1.load()
    tools = workspace.tools
    entrypoint = tools[list(tools.keys())[0]].backend.tool_class_name
    for _, tool in tools.items():
        tool_name = tool.backend.tool_class_name
        print(f"Generating manifest.json for {tool_name}...")
        manifest = ManifestV1(
            version="3.8",
            entry_point=Path(entrypoint) / f"main.pyz",
            tool_package="ayx_plugins",
            tool_name=tool_name,
        )
        manifest_json_path = WORKSPACE_CONFIG_DIR / tool_name / "manifest.json"
        manifest.save(manifest_json_path)

    print("Done!")


def _create_connection_dict(anchor_dict: Dict) -> Dict[str, List]:
    connections_dict: Dict[str, List] = {"Connection": []}
    for anchor in anchor_dict:
        connection_dict = {
            "@AllowMultiple": "True" if anchor_dict[anchor].allow_multiple else "False",
            "@Label": anchor_dict[anchor].label or "",
            "@Name": anchor,
            "@Optional": "True" if anchor_dict[anchor].optional else "False",
            "@Type": "Connection",
        }
        connections_dict["Connection"].append(connection_dict)
    return connections_dict


def get_entrypoint(num_input_anchors: int) -> str:
    """Get the engine's entrypoint based on the number of input anchors associated with the tool."""
    return defaultdict(
        lambda: "SdkEnginePluginMultiInput",
        {0: "SdkEnginePluginNoInput", 1: "SdkEnginePlugin"},
    )[num_input_anchors]


def generate_targets(
    tools: Dict[str, ToolSettingsV1],
) -> Tuple[List[Path], List[Path], List[Path]]:
    """Generate doit targets for subtasks."""
    tool_config_xml_targets = []
    manifest_json_targets = []
    icon_path_targets = []

    for _, tool in tools.items():
        class_name = tool.backend.tool_class_name
        config_file_name = class_name + CONFIG_XML_NAME
        target_path = WORKSPACE_CONFIG_DIR / class_name / config_file_name
        tool_config_xml_targets.append(target_path)
        manifest_json_targets.append(
            WORKSPACE_CONFIG_DIR / class_name / "manifest.json"
        )
        icon_path_targets.append(tool.configuration.icon_path)

    return tool_config_xml_targets, manifest_json_targets, icon_path_targets


def _add_xml_comment(file_path: Path) -> None:
    with open(file_path, mode="r") as generated_xml:
        lines = generated_xml.readlines()
        lines.insert(
            1, "<!--FILE AUTOMATICALLY GENERATED BY AYX_CLI. DO NOT MODIFY.-->\n"
        )
        generated_xml = open(file_path, mode="w")
        generated_xml.writelines(lines)


def _output_dict_to_xml(xml: Dict, xml_path: Path) -> None:
    with open(xml_path, mode="w") as output_file:
        xmltodict.unparse(
            xml, output=output_file, short_empty_elements=True, pretty=True
        )
        _add_xml_comment(xml_path)
