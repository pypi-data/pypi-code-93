"""Utility functions to download Ascend resource definitions."""

import base64
import glog
from google.protobuf import descriptor
from google.protobuf.message import Message as ProtoMessage
import jinja2
import networkx as nx
import os
import pathlib
from typing import Dict, List, Optional, Tuple

from ascend.sdk.applier import _component_id_map_from_list
from ascend.sdk.builder import dataflow_from_proto, data_service_from_proto
from ascend.sdk.client import Client
from ascend.sdk.definitions import Component, Dataflow, DataService, Definition, ReadConnector, Transform


class InlineCode:
  """ Represents the result of extraction of inline code from a component - such as
  a sql statement or PySpark code. Contains all of the metadata needed to render
  a component definition, with the inline code written to a separate file, and a reference
  to this code stored in the component.
  """
  def __init__(self, code: str, attribute_path: Tuple[str, ...], resource_path: str, base_path: str, base64_encoded: bool = False):
    """
    Parameters:
    - code: inline code
    - attribute_path: path of the attribute in the component definition that contains
    the inline code, represented as a tuple of path components. For instance, the
    path for sql code in a Transform is ("operator", "sql_query", "sql")
    - resource_path: file path to which inline code is written
    - base_path: base path of dataflow or data service resource definition
    - base64_encoded: if set to `True`, inline code is base64 encoded
    """
    self.code = code
    self.resource_path = resource_path
    self.attribute_path = attribute_path
    self._rel_path = os.path.relpath(os.path.realpath(resource_path), os.path.realpath(base_path))
    self.base64_encoded = base64_encoded

  def loader(self) -> str:
    rel_path_components = ", ".join(map(lambda x: f'"{x}"', pathlib.Path(self._rel_path).parts))
    if self.base64_encoded:
      return f'''base64.b64encode(pathlib.Path(os.path.join(os.path.dirname(os.path.realpath(__file__)), {rel_path_components})).read_bytes()).decode()'''
    else:
      return f'''pathlib.Path(os.path.join(os.path.dirname(os.path.realpath(__file__)), {rel_path_components})).read_text(encoding="utf-8")'''


def download_component(client: Client, data_service_id: str, dataflow_id: str, component_id: str, resource_base_path: str = "."):
  """
  Downloads a Component and writes its definition to a file named `{component_id}.py` under
  `resource_base_path`. Inline code for PySpark and SQL Transforms are written as separate
  files in the same folder with the file names derived from the id of the component to
  which the code belongs. Raises a `ValueError` if `resource_base_path` does not exist.

  Parameters:
  - client: SDK client
  - data_service_id: DataService id
  - dataflow_id: Dataflow id
  - component_id: Component id
  - resource_base_path: path to which Component definition will be written
  are written
  """
  if not os.path.isdir(resource_base_path):
    raise ValueError(f"Specified resource path ({resource_base_path}) must be a directory")

  df_proto = client.get_dataflow(data_service_id=data_service_id, dataflow_id=dataflow_id).data
  dataflow = dataflow_from_proto(client, data_service_id, df_proto)

  component_path = os.path.join(resource_base_path, f"{component_id}_apply.py")
  glog.info(f"Writing component definition to ({component_path}) and component resource files to ({resource_base_path})")

  pathlib.Path(resource_base_path).mkdir(parents=True, exist_ok=True)

  rendered_component, inline_code_list = render_component(data_service_id, dataflow, component_id, client.hostname, resource_base_path)
  for inline_code in inline_code_list:
    with open(inline_code.resource_path, "w", encoding="utf-8") as f:
      f.write(inline_code.code)

  with open(component_path, "w", encoding="utf-8") as f:
    f.write(rendered_component)


def download_dataflow(client: Client, data_service_id: str, dataflow_id: str, resource_base_path: str = "."):
  """
  Downloads a Dataflow and writes its definition to a file named `{dataflow_id}.py` under
  `resource_base_path`. Inline code for Transforms and ReadConnectors are written as separate
  files to a sub-folder - `resource_base_path`/`{dataflow_id}`/ with the file names derived
  from the id of the component to which the code belongs. Raises a `ValueError` if
  `resource_base_path` does not exist.

  Parameters:
  - client: SDK client
  - data_service_id: DataService id
  - dataflow_id: Dataflow id
  - resource_base_path: path to which Dataflow definition and resource files
  are written
  """
  if not os.path.isdir(resource_base_path):
    raise ValueError(f"Specified resource path ({resource_base_path}) must be a directory")

  df_proto = client.get_dataflow(data_service_id=data_service_id, dataflow_id=dataflow_id).data
  dataflow = dataflow_from_proto(client, data_service_id, df_proto)

  dataflow_resource_path = os.path.join(resource_base_path, f"{dataflow.id}")
  dataflow_path = os.path.join(resource_base_path, f"{dataflow.id}.py")
  glog.info(f"Writing dataflow definition to ({dataflow_path})" f" and dataflow resource files to ({dataflow_resource_path})")

  pathlib.Path(dataflow_resource_path).mkdir(parents=True, exist_ok=True)

  rendered_dataflow, inline_code_list = render_dataflow(data_service_id, dataflow, client.hostname, dataflow_resource_path, resource_base_path)
  for inline_code in inline_code_list:
    with open(inline_code.resource_path, "w", encoding="utf-8") as f:
      f.write(inline_code.code)

  with open(dataflow_path, "w", encoding="utf-8") as f:
    f.write(rendered_dataflow)


def download_data_service(client: Client, data_service_id: str, resource_base_path: str = "."):
  """
  Downloads a DataService and writes its definition to a file named `{data_service_id}.py`
  under `resource_base_path`. Inline code for Transforms and ReadConnectors are written as separate
  files to sub-folders - `resource_base_path`/`{dataflow_id}`/ with the file name derived from
  the id of the component to which the code belongs. Raises `ValueError` if `resource_base_path`
  does not exist.

  Parameters:
  - client: SDK client
  - data_service_id: DataService id
  - resource_base_path: base path to which DataService definition and resource
  files are written
  """
  if not os.path.isdir(resource_base_path):
    raise ValueError(f"Specified resource path ({resource_base_path}) must be a directory")

  ds_proto = client.get_data_service(data_service_id=data_service_id).data
  data_service = data_service_from_proto(client, ds_proto)
  write_data_service(client.hostname, data_service, resource_base_path)


def write_data_service(hostname: str, data_service: DataService, resource_base_path: str = "."):
  data_service_path = os.path.join(resource_base_path, f"{data_service.id}.py")
  dataflow_resource_paths = [os.path.join(resource_base_path, f"{dataflow.id}") for dataflow in data_service.dataflows]
  glog.info(f"Writing data service definition to ({data_service_path})" f" and dataflow resource files to ({','.join(dataflow_resource_paths)})")

  for path in dataflow_resource_paths:
    pathlib.Path(path).mkdir(parents=True, exist_ok=True)

  rendered_data_service, inline_code_list = render_data_service(data_service, hostname, resource_base_path)
  for inline_code in inline_code_list:
    with open(inline_code.resource_path, "w", encoding="utf-8") as f:
      f.write(inline_code.code)

  with open(data_service_path, "w", encoding="utf-8") as f:
    f.write(rendered_data_service)


class InlineCodeMap:
  """Maps component to InlineCode list."""
  def __init__(self):
    self._inline_code_map: Dict[Tuple[str, str], List[InlineCode]] = {}

  def add(self, dataflow_id: str, component_id: str, inline_code: InlineCode):
    if (dataflow_id, component_id) not in self._inline_code_map:
      self._inline_code_map[(dataflow_id, component_id)] = []
    self._inline_code_map[(dataflow_id, component_id)].append(inline_code)

  def attribute_path_to_loader(self, dataflow_id: str, component_id: str) -> Dict[Tuple[str, ...], str]:
    if (dataflow_id, component_id) in self._inline_code_map:
      inline_code_list = self._inline_code_map[(dataflow_id, component_id)]
      return {ic.attribute_path: ic.loader() for ic in inline_code_list}
    else:
      return {}


def render_component(data_service_id: str, dataflow: Dataflow, component_id: str, hostname: str, base_path: str) -> Tuple[str, List[InlineCode]]:
  target_component = None
  inline_code_list: List[InlineCode] = []
  inline_code_map = InlineCodeMap()

  for component in dataflow.components:
    if component.id == component_id:
      target_component = component
      icl = _inline_code_list_for(component, base_path, base_path)
      for ic in icl:
        inline_code_list.append(ic)
        inline_code_map.add(dataflow.id, component.id, ic)
  if target_component is None:
    raise KeyError(f"Component with id of {component_id} not found in dataflow {data_service_id}.{dataflow.id}")

  env = _jinja_env()
  tmpl = env.get_template("component.jinja")
  rendered = tmpl.render(data_service_id=data_service_id,
                         dataflow_id=dataflow.id,
                         component=target_component,
                         hostname=hostname,
                         renderer=_render_definition,
                         proto_mods=_proto_mods,
                         gmod_classes=_gmod_classes,
                         inline_code_map=inline_code_map,
                         classname_map=_classname_map())
  return rendered, inline_code_list


def render_dataflow(data_service_id: str, dataflow: Dataflow, hostname: str, resource_path: str, base_path: str) -> Tuple[str, List[InlineCode]]:
  inline_code_list: List[InlineCode] = []
  inline_code_map = InlineCodeMap()

  for component in dataflow.components:
    icl = _inline_code_list_for(component, resource_path, base_path)
    for ic in icl:
      inline_code_list.append(ic)
      inline_code_map.add(dataflow.id, component.id, ic)

  env = _jinja_env()
  tmpl = env.get_template("dataflow.jinja")
  rendered = tmpl.render(data_service_id=data_service_id,
                         dataflow=dataflow,
                         hostname=hostname,
                         renderer=_render_definition,
                         proto_mods=_proto_mods,
                         gmod_classes=_gmod_classes,
                         ordered_components=_components_ordered_by_dependency,
                         inline_code_map=inline_code_map,
                         classname_map=_classname_map())
  return rendered, inline_code_list


def render_data_service(data_service: DataService, hostname: str, resource_path: str) -> str:
  inline_code_list: List[InlineCode] = []
  inline_code_map = InlineCodeMap()

  for dataflow in data_service.dataflows:
    dataflow_resource_path = os.path.join(resource_path, f"{dataflow.id}")
    for component in dataflow.components:
      icl = _inline_code_list_for(component, dataflow_resource_path, resource_path)
      for ic in icl:
        inline_code_list.append(ic)
        inline_code_map.add(dataflow.id, component.id, ic)

  env = _jinja_env()
  tmpl = env.get_template("data_service.jinja")
  rendered = tmpl.render(data_service=data_service,
                         hostname=hostname,
                         renderer=_render_definition,
                         proto_mods=_proto_mods,
                         gmod_classes=_gmod_classes,
                         ordered_components=_components_ordered_by_dependency,
                         inline_code_map=inline_code_map,
                         classname_map=_classname_map())
  return rendered, inline_code_list


_proto_mods = [
    "ascend", "component", "connection", "content_encoding", "core", "environment", "expression", "format", "function", "io", "operator", "pattern", "schema",
    "text"
]

_gmod_classes = [("google.protobuf.wrappers_pb2", "DoubleValue"), ("google.protobuf.wrappers_pb2", "BoolValue"), ("google.protobuf.wrappers_pb2", "Int64Value"),
                 ("google.protobuf.wrappers_pb2", "UInt64Value"), ("google.protobuf.wrappers_pb2", "Int32Value"),
                 ("google.protobuf.wrappers_pb2", "UInt32Value"), ("google.protobuf.duration_pb2", "Duration"), ("google.protobuf.timestamp_pb2", "Timestamp"),
                 ("google.protobuf.struct_pb2", "NullValue"), ("google.protobuf.empty_pb2", "Empty")]


def _classname_map() -> dict:
  classname_map: dict = {}

  for defclass in [
      'DataService', 'Credential', 'Connection', 'Dataflow', 'ReadConnector', 'WriteConnector', 'Transform', 'ComponentGroup', 'DataFeed', 'DataFeedConnector'
  ]:
    classname_map[defclass] = f"definitions.{defclass}"

  for _, cls in _gmod_classes:
    classname_map[f"google.protobuf.{cls}"] = cls

  return classname_map


def _inline_code_list_for(component: Component, resource_path_prefix: str, base_path: str) -> Optional[List[InlineCode]]:
  if isinstance(component, Transform) and component.operator:
    if component.operator.HasField("spark_function") and component.operator.spark_function.executable.code.source.HasField("inline"):
      if component.operator.spark_function.executable.code.language.HasField("sql"):
        resource_name = f"{component.id}.sql"
      elif component.operator.spark_function.executable.code.language.HasField("python"):
        resource_name = f"{component.id}.py"
      else:
        l = component.operator.spark_function.executable.code.language.WhichOneof("language")
        raise ValueError(f"code download for language type \"{l}\" is unsupported")
      return [
          InlineCode(code=component.operator.spark_function.executable.code.source.inline,
                     resource_path=os.path.join(resource_path_prefix, resource_name),
                     base_path=base_path,
                     attribute_path=("operator", "spark_function", "executable", "code", "source", "inline"))
      ]
    elif component.operator.HasField("sql_query"):
      return [
          InlineCode(code=component.operator.sql_query.sql,
                     resource_path=os.path.join(resource_path_prefix, f"{component.id}.sql"),
                     base_path=base_path,
                     attribute_path=("operator", "sql_query", "sql"))
      ]
    else:
      return []
  elif isinstance(component, ReadConnector):
    icl = []
    if component.container and component.container.HasField("byte_function") and component.container.byte_function.container.executable.code.source.HasField(
        "inline"):
      icl.append(
          InlineCode(
              code=base64.b64decode(component.container.byte_function.container.executable.code.source.inline).decode(),
              resource_path=os.path.join(resource_path_prefix, f"custom_read_connector_{component.id}.py"),  # noqa: E126
              base_path=base_path,
              attribute_path=("container", "byte_function", "container", "executable", "code", "source", "inline"),
              base64_encoded=True))
    if component.bytes and component.bytes.parser.HasField("lambda_parser") and component.bytes.parser.lambda_parser.HasField(
        "code") and component.bytes.parser.lambda_parser.code.HasField("inline"):
      icl.append(
          InlineCode(
              code=base64.b64decode(component.bytes.parser.lambda_parser.code.inline).decode(),
              resource_path=os.path.join(resource_path_prefix, f"custom_parser_{component.id}.py"),  # noqa: E126
              base_path=base_path,
              attribute_path=("bytes", "parser", "lambda_parser", "code", "inline"),
              base64_encoded=True))
    return icl
  else:
    return []


def _jinja_env():
  module_dir = os.path.dirname(os.path.abspath(__file__))
  template_dir = os.path.join(module_dir, "templates")
  return jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir), trim_blocks=True, lstrip_blocks=True)


def _render_definition(val: Definition, attribute_path: Tuple[str, ...] = (), indent=0, classname_map: dict = {}, attribute_overrides: dict = {}):
  defcls = val.__class__.__name__
  cls = classname_map.get(defcls, defcls)
  tmpl = jinja2.Template('''{{cls}}(
{% for k, v in vars(val).items() %}\
{% if attribute_overrides.get(_append(attribute_path, k)) %}\
{{_spaces_for(indent+2)}}{{k}}=\
{{attribute_overrides.get(_append(attribute_path, k))}},\n\
{% else %}\
{{_spaces_for(indent+2)}}{{k}}=\
{{_render_value(v, _append(attribute_path, k), indent+2, classname_map, attribute_overrides)}},\n\
{% endif %}\
{% endfor %}\
{{_spaces_for(indent)}})''')
  return tmpl.render(val=val,
                     vars=vars,
                     _render_value=_render_value,
                     _spaces_for=_spaces_for,
                     _append=_append,
                     indent=indent,
                     classname_map=classname_map,
                     attribute_path=attribute_path,
                     attribute_overrides=attribute_overrides,
                     cls=cls)


def _render_value(val, attribute_path: Tuple[str, ...], indent=0, classname_map: dict = {}, attribute_overrides: dict = {}):
  """ Renders values in Python definition form. Support is limited to
  resource definitions, proto messages, and native types.
  """
  if isinstance(val, list):
    return _render_array(val, attribute_path, indent, classname_map, attribute_overrides)
  elif isinstance(val, dict):
    return _render_map(val, attribute_path, indent, classname_map, attribute_overrides)
  elif isinstance(val, ProtoMessage):
    return _render_message(val, attribute_path, indent, classname_map, attribute_overrides)
  elif isinstance(val, Definition):
    return _render_definition(val, attribute_path, indent, classname_map, attribute_overrides)
  elif isinstance(val, str):
    return repr(val)
  else:
    return val


def _render_array(arr, attribute_path: Tuple[str, ...], indent=0, classname_map: dict = {}, attribute_overrides: dict = {}):
  tmpl = jinja2.Template('''[
{% for v in arr %}\
{{_spaces_for(indent+2)}}{{ _render_value(v, attribute_path, indent+2, classname_map, attribute_overrides) }},\n\
{% endfor %}\
{{_spaces_for(indent)}}]''')
  return tmpl.render(arr=arr,
                     _render_value=_render_value,
                     _spaces_for=_spaces_for,
                     indent=indent,
                     classname_map=classname_map,
                     attribute_path=attribute_path,
                     attribute_overrides=attribute_overrides)


def _render_map(mp, attribute_path: Tuple[str, ...], indent=0, classname_map: dict = {}, attribute_overrides: dict = {}):
  tmpl = jinja2.Template('''{
{% for k in sorted(mp.keys()) %}\
{{_spaces_for(indent+2)}}{{_render_value(k, attribute_path, indent+2, classname_map, attribute_overrides)}}: \
{{ _render_value(mp[k], attribute_path, indent+2, classname_map, attribute_overrides) }},\n\
{% endfor %}\
{{_spaces_for(indent)}}}''')
  return tmpl.render(mp=mp,
                     sorted=sorted,
                     _render_value=_render_value,
                     _spaces_for=_spaces_for,
                     indent=indent,
                     classname_map=classname_map,
                     attribute_path=attribute_path,
                     attribute_overrides=attribute_overrides)


def _render_message(message: ProtoMessage, attribute_path: Tuple[str, ...], indent=0, classname_map: dict = {}, attribute_overrides: dict = {}):
  def render_message_field(field_descriptor, val, attribute_path, indent):
    if field_descriptor.label == descriptor.FieldDescriptor.LABEL_REPEATED:
      if hasattr(val, 'items'):
        return _render_map(val, attribute_path, indent, classname_map, attribute_overrides)
      else:
        return _render_array(val, attribute_path, indent, classname_map, attribute_overrides)
    elif field_descriptor.type == descriptor.FieldDescriptor.TYPE_MESSAGE:
      return _render_message(val, attribute_path, indent, classname_map, attribute_overrides)
    elif field_descriptor.type == descriptor.FieldDescriptor.TYPE_STRING:
      return repr(val)
    else:
      return val

  cls = message.DESCRIPTOR.full_name
  cls = classname_map.get(cls, cls)
  tmpl = jinja2.Template('''{{cls}}(
{% for field in message.ListFields() %}\
{{ _spaces_for(indent+2) }}{{ field[0].name }}=\
{{ attribute_overrides.get(_append(attribute_path, field[0].name),\
render_message_field(field[0], field[1], _append(attribute_path, field[0].name), indent+2)) }},\n\
{% endfor %}\
{{_spaces_for(indent)}})''')
  return tmpl.render(message=message,
                     cls=cls,
                     render_message_field=render_message_field,
                     _spaces_for=_spaces_for,
                     _append=_append,
                     indent=indent,
                     attribute_path=attribute_path,
                     attribute_overrides=attribute_overrides)


def _append(tpl: Tuple[str, ...], val: str):
  return tpl + (val, )


def _spaces_for(indent):
  return " " * indent


def _components_ordered_by_dependency(components: List[Component]) -> List[Component]:
  # return sorted(components, key=lambda c: c.name)

  ordered: List[Component] = []

  id_to_component = _component_id_map_from_list(components)
  g = nx.DiGraph()
  for component in components:
    g.add_node(component.id)
    for dep in component.dependencies():
      # A data feed connector will not be in the component list.
      if dep in id_to_component:
        g.add_edge(component.id, dep)

  for component_id in reversed(list(nx.topological_sort(g))):
    component = id_to_component[component_id]
    ordered.append(component)

  return ordered
