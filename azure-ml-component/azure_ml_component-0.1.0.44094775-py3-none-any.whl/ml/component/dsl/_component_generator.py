# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Union
from pathlib import Path
from abc import ABC, abstractmethod

from azure.ml.component.dsl._component import InputPath, OutputPath
from azure.ml.component.dsl.types import Input, Output, String, _Param, Enum, _Group
from azure.ml.component.dsl._module_spec import BaseModuleSpec, Param, OutputPort, InputPort
from azure.ml.component.dsl._utils import logger, _sanitize_python_class_name, is_notebook_file,\
    NOTEBOOK_EXT, is_py_file, _to_camel_case
from azure.ml.component._util._utils import _sanitize_python_variable_name
from azure.ml.component.run_settings import _RunSettingsInterfaceGenerator

DATA_PATH = Path(__file__).resolve().parent / 'data'
NOTEBOOK_ENTRY_TPL_FILE = DATA_PATH / 'from_notebook_sample_code.template'
ARGPARSE_ENTRY_TPL_FILE = DATA_PATH / 'from_argparse_sample_code.template'
ARGPRASE_ENTRY_TPL_FILE_PARALLEL = DATA_PATH / 'from_argparse_parallel_sample_code.template'
GENERATE_MODULE_PATH = DATA_PATH / 'generate_module'
GENERATE_MOUDLE_TPL_FILE = GENERATE_MODULE_PATH / 'generate_module.template'
GENERATE_MOUDLE_SINGLE_COMPONENT_TPL_FILE = GENERATE_MODULE_PATH / 'single_component.template'
GENERATE_MOUDLE_SINGLE_RUNSETTING_CLS_TPL_FILE = GENERATE_MODULE_PATH / 'single_runsetting_class.template'


SINGLE_SPACE = ' '
LINE_SEP = '\n'
CLASS_SEP = LINE_SEP * 2


def new_line(meta='', indent=0):
    return '%s%s%s' % (LINE_SEP, SINGLE_SPACE * indent, meta)


def normalize_working_dir(working_dir):
    if working_dir is None:
        working_dir = '.'
    if not Path(working_dir).is_dir():
        raise ValueError("Working directory '%s' is not a valid directory." % working_dir)
    return working_dir


def normalize_entry_path(working_dir, entry, ext=None, job_type=None):
    is_file = False
    if ext:
        is_file = entry.endswith(ext)
    if is_file:
        if Path(entry).is_absolute():
            raise ValueError("Absolute file path '%s' is not allowed." % entry)
        if not (Path(working_dir) / entry).is_file():
            raise FileNotFoundError("Entry file '%s' not found in working directory '%s'." % (entry, working_dir))
        entry = Path(entry).as_posix()
        # For parallel component, we need to import the entry instead of run it.
        if job_type == 'parallel':
            entry = entry[:-3].replace('/', '.')
    return entry


def normalized_target_file(working_dir, target_file, force):
    if target_file:
        if Path(target_file).is_absolute():
            raise ValueError("Absolute target file path '%s' is not allowed." % target_file)
        if not target_file.endswith('.py'):
            raise ValueError("Target file must has extension '.py', got '%s'." % target_file)
        if not force and (Path(working_dir) / target_file).exists():
            raise FileExistsError("Target file '%s' already exists." % target_file)
    return target_file


def normalized_spec_file(working_dir, spec_file, force):
    if spec_file:
        if Path(spec_file).is_absolute():
            raise ValueError("Absolute module spec file path '%s' is not allowed." % spec_file)
        if not spec_file.endswith('.yaml'):
            raise ValueError("Module spec file must has extension '.yaml', got '%s'." % spec_file)
        if not force and (Path(working_dir) / spec_file).exists():
            raise FileExistsError("Module spec file '%s' already exists." % spec_file)
    return spec_file


class BoolParam(Param):
    def __init__(self, name, description=None, default=None, arg_name=None, arg_string=None):
        super().__init__(
            name=name, type='Bool', description=description,
            default=default, arg_name=arg_name, arg_string=arg_string,
        )


class StoreTrueParam(BoolParam):
    @property
    def append_argv_statement(self):
        return "    if %s:\n        sys.argv.append(%r)" % (self.arg_name, self.arg_string)


class StoreFalseParam(BoolParam):
    @property
    def append_argv_statement(self):
        return "    if not %s:\n        sys.argv.append(%r)" % (self.arg_name, self.arg_string)


class BaseParamGenerator:
    def __init__(self, param: Union[_Param, InputPort, OutputPort, InputPath, OutputPath]):
        self.param = param

    @property
    def type(self):
        return self.param.type

    @property
    def description(self):
        return self.param.description

    @property
    def arg_string(self):
        return self.param.arg_string

    @property
    def default(self):
        value = self.param.default if isinstance(self.param, (_Param, Param)) else None
        if value is None:
            if hasattr(self.param, 'optional') and self.param.optional:
                return 'None'
            return None
        if self.type.lower() == String.TYPE_NAME:
            return "'%s'" % value
        elif self.type.lower() == Enum.TYPE_NAME:
            if value not in self.param.enum:
                value = self.param.enum[0]
            return "%s.%s" % (self.enum_class, self.enum_name(value, self.param.enum.index(value)))
        elif self.type.lower() == _Group.TYPE_NAME:
            return "%s(%s)" % (self.group_class, ', '.join(['%s=%s' % (k, v)for k, v in value.items()]))
        return str(value)

    @property
    def var_name(self):
        return _sanitize_python_variable_name(self.param.name)

    @property
    def arg_value(self):
        if type(self.param.type) == str and self.param.type.lower() == Enum.TYPE_NAME:
            return self.var_name + '.value'
        return 'str(%s)' % self.var_name

    @property
    def arg_def_in_cls(self):
        arg_type = 'Input' if isinstance(self.param, Input) else self.arg_type
        result = "%s: %s" % (self.var_name, arg_type)
        if self.default is not None:
            result += ' = %s' % self.default
        comment = self.param._get_hint(new_line_style=True)
        if comment:
            result += new_line(meta=comment, indent=4)
        return result

    @property
    def arg_def(self):
        result = "%s: %s" % (self.var_name, self.arg_type)
        result += ',' if self.default is None else ' = %s,' % self.default
        return result

    @property
    def enum_class(self):
        return 'Enum%s' % _sanitize_python_class_name(self.var_name)

    @staticmethod
    def enum_name(value, idx):
        name = _sanitize_python_variable_name(str(value))
        if name == '':
            name = 'enum%d' % idx
        return name

    @staticmethod
    def enum_value(value):
        return "'%s'" % value

    @property
    def enum_name_def(self):
        return new_line().join("    %s = %s" % (self.enum_name(option, i), self.enum_value(option))
                               for i, option in enumerate(self.param.enum))

    @property
    def enum_def(self):
        return "class {enum_class}(Enum):\n{enum_value_string}\n".format(
            enum_class=self.enum_class, enum_value_string=self.enum_name_def,
        )

    @property
    def group_class(self):
        return '%sGroup' % _sanitize_python_class_name(self.var_name)

    @property
    def group_cls_fields(self):
        params = [BaseParamGenerator(param) for param in self.param.values.values()]
        ordered_param_def = [''] + [param.arg_def for param in params if param.default is None] + \
            [param.arg_def for param in params if param.default is not None]
        return new_line(indent=4).join(ordered_param_def)

    @property
    def group_def(self):
        return "@dsl.parameter_group\nclass {group_class}:{group_value_string}\n".format(
            group_class=self.group_class, group_value_string=self.group_cls_fields,
        )


class ArgParseParamGenerator(BaseParamGenerator):
    mapping = {str: 'String', int: 'Int', float: 'Float', bool: 'Bool'}
    reverse_mapping = {v: k.__name__ for k, v in mapping.items()}

    @property
    def arg_type(self):
        if isinstance(self.param, (InputPort, OutputPort)):
            desc_str = 'description=%r' % self.description if self.description else ''
            key = 'Input' if isinstance(self.param, InputPort) else 'Output'
            return "%sPath(%s)" % (key, desc_str)
        if not self.description:
            return self.enum_class if self.type.lower() == Enum.TYPE_NAME else self.reverse_mapping[self.type]
        # The placeholders are used to avoid the bug when description contains '{xx}'.
        placeholder_l, placeholder_r = 'L__BRACKET', 'R__BRACKET'
        description = self.description.replace('{', placeholder_l).replace('}', placeholder_r)
        tpl = "EnumParameter(enum={enum_class}, description=%r)" % description\
            if self.type.lower() == Enum.TYPE_NAME else "{type}Parameter(description=%r)" % description
        result = tpl.format(type=self.type, enum_class=self.enum_class)
        return result.replace(placeholder_l, '{').replace(placeholder_r, '}')

    @property
    def argv(self):
        return ["'%s'" % self.param.arg_string, self.arg_value]

    @property
    def is_optional_argv(self):
        return isinstance(self.param, BoolParam) or \
            not isinstance(self.param, OutputPort) and self.param.optional is True and \
            getattr(self.param, 'default', None) is None

    @property
    def append_argv_statement(self):
        if hasattr(self.param, 'append_argv_statement'):
            return self.param.append_argv_statement
        return """    if %s is not None:\n        sys.argv += [%s]""" % (self.var_name, ', '.join(self.argv))


class NotebookParamGenerator(BaseParamGenerator):

    @property
    def arg_type(self):
        return self.param._to_python_code()


class BaseGenerator(ABC):
    """Base generator class to generate code/file based on given template."""
    @property
    @abstractmethod
    def tpl_file(self):
        """Specify the template file for different generator."""
        pass

    @property
    @abstractmethod
    def entry_template_keys(self):
        """Specify the entry keys in template, they will be formatted by value when generate code/file."""
        pass

    def to_component_entry_code(self):
        with open(self.tpl_file) as f:
            entry_template = f.read()
        return entry_template.format(**{key: getattr(self, key) for key in self.entry_template_keys})

    def to_component_entry_file(self, target='entry.py'):
        with open(target, 'w') as fout:
            fout.write(self.to_component_entry_code())


class BaseComponentGenerator(BaseGenerator):
    def __init__(self, name=None, entry=None, description=None):
        self._params = []
        self.name = None
        self.display_name = None
        if name is not None:
            self.set_name(name)
        self.entry = None
        self.entry_type = 'path'
        if entry is not None:
            self.set_entry(entry)
        self.description = description
        self._component_meta = {}
        self.parallel_inputs = []

    @property
    @abstractmethod
    def tpl_file(self):
        pass

    @property
    @abstractmethod
    def entry_template_keys(self):
        pass

    def set_name(self, name):
        if name.endswith('.py'):
            name = name[:-3]
        if name.endswith(NOTEBOOK_EXT):
            name = name[:-6]
        # Use the last piece as the component name.
        self.display_name = _to_camel_case(name.split('/')[-1].split('.')[-1])
        self.name = _sanitize_python_variable_name(self.display_name)

    def set_entry(self, entry):
        self.entry = entry
        if type(entry) == str:
            if is_py_file(entry):
                self.entry_type = 'path'  # python path
            elif is_notebook_file(entry):
                self.entry_type = 'notebook_path'
                suffix = NOTEBOOK_EXT
                self.entry_out = self.entry[:-len(suffix)] + '.out' + suffix
            else:
                self.entry_type = 'module'
        else:
            self.entry_type = 'module'

    @property
    def component_name(self):
        if self.entry_type == 'module':
            return self.entry
        elif self.entry_type == 'path':
            return Path(self.entry).as_posix()[:-3].replace('/', '.')
        else:
            raise TypeError("Entry type %s doesn't have component name." % self.entry_type)

    def assert_valid(self):
        if self.name is None:
            raise ValueError("The name of a component could not be None.")
        if self.entry is None:
            raise ValueError("The entry of the component '%s' could not be None." % self.name)

    @property
    def params(self):
        return self._params

    def to_component_entry_code(self):
        self.assert_valid()
        with open(self.tpl_file) as f:
            entry_template = f.read()
        return entry_template.format(**{key: getattr(self, key) for key in self.entry_template_keys})

    @property
    def func_name(self):
        return _sanitize_python_variable_name(self.name)

    @property
    def func_args(self):
        items = [''] + [param.arg_def for param in self.params if param.default is None] + \
                [param.arg_def for param in self.params if param.default is not None]
        return '\n    '.join(items)

    @property
    def dsl_param_dict(self):
        meta = self.component_meta
        if not meta:
            return ''
        items = [''] + ['%s=%r,' % (k, v) for k, v in meta.items()]
        if self.job_type == 'parallel':
            parallel_inputs_str = "InputPath(name='parallel_input_data')" if not self.parallel_inputs else \
                ', '.join("InputPath(name=%r)" % name
                          for name in self.parallel_inputs)
            items.append('parallel_inputs=[%s]' % parallel_inputs_str)
        return new_line(indent=4).join(items) + new_line()

    @property
    def component_meta(self):
        meta = {**self._component_meta}
        if self.description and 'description' not in meta:
            meta['description'] = self.description
        if self.name and 'name' not in meta:
            meta['name'] = self.name
        if self.display_name and 'display_name' not in meta:
            meta['display_name'] = self.display_name
        return meta

    @property
    def job_type(self):
        return self.component_meta.get('job_type', 'basic').lower()

    def update_component_meta(self, component_meta):
        for k, v in component_meta.items():
            if v is not None:
                self._component_meta[k] = v


class ArgParseComponentGenerator(BaseComponentGenerator):

    @property
    def tpl_file(self):
        return ARGPRASE_ENTRY_TPL_FILE_PARALLEL if self.job_type == 'parallel' else ARGPARSE_ENTRY_TPL_FILE

    @property
    def entry_template_keys(self):
        return [
            'enums', 'imports',
            'entry_type', 'entry',
            'component_name',
            'func_name', 'func_args',
            'sys_argv', 'append_stmt',
            'dsl_param_dict',
        ]

    def add_param(self, param: _Param):
        self._params.append(ArgParseParamGenerator(param))

    @property
    def params(self):
        result = self._params
        if self.job_type.lower() == 'parallel' and not self.has_output():
            # Add an output if output is not set, since parallel component require one output,
            # which may not be from argparse.
            return [ArgParseParamGenerator(OutputPort(
                name='Output', type='AnyDirectory', arg_name='output', arg_string='--output',
            ))] + result
        return result

    @property
    def component_entry_file(self):
        if is_py_file(self.entry):
            return self.entry
        return self.entry.replace('.', '/') + '.py'

    @property
    def spec(self):
        """This spec is directly generated by argument parser arguments,
        it is used to create a module spec without a new entry file.
        """
        params = [param.param for param in self.params if isinstance(param.param, Param)]
        inputs = [param.param for param in self.params if isinstance(param.param, InputPort)]
        outputs = [param.param for param in self.params if isinstance(param.param, OutputPort)]
        args = []
        for param in self.params:
            if not isinstance(param.param, OutputPort) and param.param.optional:
                args.append(param.param.arg_group())
            else:
                args += param.param.arg_group()

        return BaseModuleSpec(
            name=self.name, description=self.description,
            inputs=inputs, outputs=outputs, params=params,
            args=args,
            command=['python', self.component_entry_file],
        )

    @property
    def spec_dict(self):
        return self.spec.spec_dict

    def to_spec_yaml(self, folder, spec_file='spec.yaml'):
        self.assert_valid()
        self.spec._save_to_code_folder(folder, spec_file=spec_file)

    def has_type(self, type):
        return any(param.type == type for param in self._params)

    def has_import_type(self, type):
        return any(param.type == type and param.description is not None for param in self._params)

    def has_input(self):
        return any(isinstance(param.param, InputPort) for param in self._params)

    def has_output(self):
        return any(isinstance(param.param, OutputPort) for param in self._params)

    @property
    def enums(self):
        return CLASS_SEP + CLASS_SEP.join(
            param.enum_def for param in self.params
            if type(param.type) == str and param.type.lower() == Enum.TYPE_NAME) if self.has_type('Enum') else ''

    @property
    def imports(self):
        keys = ['Enum'] + list(ArgParseParamGenerator.reverse_mapping)
        param_imports = [''] + ['%sParameter' % key for key in keys if self.has_import_type(key)]
        # Note that for a parallel component, input/output are required.
        if self.has_input() or self.job_type == 'parallel':
            param_imports.append('InputPath')
        if self.has_output() or self.job_type == 'parallel':
            param_imports.append('OutputPath')
        return ', '.join(param_imports)

    @property
    def sys_argv(self):
        items = ['', "'%s'," % self.entry] + [
            ', '.join(param.argv) + ',' for param in self.params if not param.is_optional_argv
        ]
        return new_line(indent=8).join(items)

    @property
    def append_stmt(self):
        return new_line().join(param.append_argv_statement for param in self.params if param.is_optional_argv)

    def update_spec_param(self, key, is_output=False):
        target = None
        key = key
        for param in self.params:
            # For add_argument('--input-dir'), we could have var_name='input_dir', arg_string='--input-dir'
            # In this case, both 'input_dir' and 'input-dir' is ok to used for finding the param.
            if param.var_name == key or param.arg_string.lstrip('-') == key:
                target = param
                break
        if not target:
            if not is_output and self.job_type == 'parallel':
                self.parallel_inputs.append(key)
            else:
                valid_params = ', '.join('%r' % param.var_name for param in self.params)
                logger.warning("%r not found in params, valid params: %s." % (key, valid_params))
            return
        param = target.param
        if is_output:
            target.param = OutputPort(
                name=param.name, type="path", description=param.description,
                arg_string=param.arg_string,
            )
        else:
            target.param = InputPort(
                name=param.name, type="path",
                description=target.description, optional=param.optional,
                arg_string=param.arg_string,
            )

    def update_spec_params(self, keys, is_output=False):
        for key in keys:
            self.update_spec_param(key, is_output)


class NotebookComponentGenerator(BaseComponentGenerator):

    @property
    def tpl_file(self):
        return NOTEBOOK_ENTRY_TPL_FILE

    @property
    def entry_template_keys(self):
        return [
            'func_name',
            'func_args', 'parameters_dict',
            'entry', 'entry_out',
            'dsl_param_dict',
        ]

    def add_param(self, param: Union[_Param, InputPath, OutputPath]):
        self._params.append(NotebookParamGenerator(param))

    @property
    def parameters_dict(self):
        items = [''] + ['%s=%s,' % (param.param.name, param.param.name) for param in self.params]
        return new_line(indent=12).join(items)


class ModuleParamGenerator(BaseParamGenerator):
    def __init__(self, param, _component_cls_name):
        super().__init__(param)
        self._component_cls_name = _component_cls_name

    @property
    def arg_type(self):
        if isinstance(self.param, _Param):
            _typ = self.type.lower()
            if _typ == Enum.TYPE_NAME:
                return self.enum_class
            if _typ == _Group.TYPE_NAME:
                return self.group_class
            # type not in mapping: group
            return _Param._PARAM_TYPE_STRING_MAPPING[_typ].__name__ \
                if _typ in _Param._PARAM_TYPE_STRING_MAPPING else 'str'
        # set Input annotation as pathlib.Path if on function
        return 'Path' if isinstance(self.param, Input) else 'Output'

    @property
    def default(self):
        default_value = super().default
        # Directly assign if is valid Numeric/bool parameter, else assign str
        # Note: Some embarrassing case, like default value is '010', then:
        # int('010')=10, so we generate line 'var=010', but this will raise an exception if import.
        # Same others case: float('NAN'), float('-Infinity')
        if default_value and default_value != str(None) and self.type.lower() in _Param._PARAM_PARSERS:
            try:
                _Param._PARAM_PARSERS.get(self.type.lower())(default_value)
            except ValueError:
                # Change to str if is not valid numeric string
                default_value = f'{default_value!r}'
        return default_value

    @property
    def docstring(self):
        param_desc = self.param._get_hint()
        if isinstance(self.param, Output):
            return new_line(indent=4).join([':output %s: %s' % (self.var_name, param_desc),
                                            ':type: %s: %s' % (self.var_name, self.arg_type)])
        return new_line(indent=4).join([':param %s: %s' % (self.var_name, param_desc),
                                        ':type %s: %s' % (self.var_name, self.arg_type)])

    @property
    def enum_class(self):
        return '_%s%sEnum' % (self._component_cls_name, _sanitize_python_class_name(self.var_name))

    @property
    def group_class(self):
        return '_%s%sGroup' % (self._component_cls_name, _sanitize_python_class_name(self.var_name))

    @property
    def group_cls_fields(self):
        params = [ModuleParamGenerator(param, self._component_cls_name) for param in self.param.values.values()]
        ordered_param_def = [''] + [param.arg_def_in_cls for param in params if param.default is None] + \
            [param.arg_def_in_cls for param in params if param.default is not None]
        return new_line(indent=4).join(ordered_param_def)


class ModuleRunsettingParamGenerator(ModuleParamGenerator):
    def __init__(self, param, _component_cls_name):
        self._var_name = param.display_argument_name
        param = param.definition.definition

        super().__init__(param, _component_cls_name)
        self._component_cls_name = _component_cls_name
        self._schema_type_converter = {'array': 'list', 'object': 'dict'}

    @property
    def arg_def_in_cls(self):
        # Note: No default value if runsetting parameter arg
        result = "%s: %s" % (self.var_name, self.arg_type)
        # Note: No optional field in hint str
        comment_str = self.param.description.replace('"', '\\"') if self.param.description else self.param.type
        hint_str = ', '.join(['%s: %s' % (key, val) for key, val in zip(
            ['min', 'max', 'enum'], [self.param._min, self.param._max, self.param.enum]) if val])
        comment_str += ' (%s)' % hint_str if hint_str else ''
        result += new_line(meta='"""%s"""' % comment_str, indent=4) if comment_str else ''
        return result

    @property
    def arg_type(self):
        if self.param.json_schema:
            _type = self.param.json_schema.get('type')
            _type = self._schema_type_converter.get(_type, str.__name__)
            return f'Union[str, {_type}]' if _type != str.__name__ else str.__name__
        return self.param.parameter_type_in_py.__name__

    @property
    def var_name(self):
        return self._var_name


class ModuleRunsettingClsGenerator(BaseGenerator):

    def __init__(self, runsettings_param_section, component_type, section_name=None):
        super().__init__()
        section_name = '' if section_name is None else section_name
        self._component_type = component_type
        self._section_name = section_name
        # Replace the top level description
        self._description = runsettings_param_section.description if section_name \
            else f'Run setting configuration for {component_type}'
        self._section_cls_name = _sanitize_python_class_name(section_name)
        self._sections = [ModuleRunsettingClsGenerator(
            section, component_type, section_name=section.display_name)
            for section in runsettings_param_section.sub_sections]
        self._full_cls_name = '_%sRunsetting%s' % (component_type, self._section_cls_name)
        if not self._description:
            self._description = self._full_cls_name
        from azure.ml.component._restclients.designer.models import ModuleRunSettingTypes
        self._params = [ModuleRunsettingParamGenerator(param, self._full_cls_name)
                        for param in runsettings_param_section.parameters
                        if param.definition.definition.module_run_setting_type != ModuleRunSettingTypes.legacy]

    @property
    def tpl_file(self):
        return GENERATE_MOUDLE_SINGLE_RUNSETTING_CLS_TPL_FILE

    @property
    def entry_template_keys(self):
        return ['sections', 'component_type', 'section_cls_name', 'cls_fields']

    @property
    def component_type(self):
        return self._component_type

    @property
    def cls_fields(self):
        # params
        items = [''] + ['"""%s"""' % self._description] + [param.arg_def_in_cls for param in self._params]
        # sections
        for section in self._sections:
            items.append('%s: %s' % (section._section_name, section._full_cls_name))
            items.append('"""%s"""' % (section._description))
        cls_field_string = new_line(indent=4).join(items)
        return cls_field_string if cls_field_string.strip() else new_line(meta='pass', indent=4)

    @property
    def section_cls_name(self):
        return self._section_cls_name

    @property
    def sections(self):
        if not self._sections:
            return ''
        return new_line().join(section.to_component_entry_code() for section in self._sections) + new_line()


class ModuleComponentGenerator(BaseComponentGenerator):

    def __init__(self, definition):
        super().__init__(name=_sanitize_python_variable_name(definition.name), entry=definition)
        self._component_cls_name = _sanitize_python_class_name(_sanitize_python_variable_name(self.name))
        self._params = self.get_component_params()
        self._outputs = self.get_component_outputs()

    @property
    def tpl_file(self):
        return GENERATE_MOUDLE_SINGLE_COMPONENT_TPL_FILE

    @property
    def entry_template_keys(self):
        return [
            'enums', 'groups', 'component_name', 'component_cls_name',
            'runsettings_field', 'component_version', 'component_description',
            'input_cls_fields', 'output_cls_fields',
            'func_name', 'func_args', 'func_docstring', 'func_init_args']

    def get_component_params(self):
        all_component_params = [*self.entry.inputs.values(),
                                *self.entry.parameters.values()]
        return [ModuleParamGenerator(param, self._component_cls_name)
                for param in all_component_params]

    def get_component_outputs(self):
        return [ModuleParamGenerator(param, self._component_cls_name)
                for param in self.entry.outputs.values()]

    @property
    def component_name(self):
        return self.entry.name

    @property
    def component_cls_name(self):
        return self._component_cls_name

    @property
    def runsettings_field(self):
        if not self.entry.runsettings or not self.entry.runsettings.params:
            return '# No runsettings in this component.'
        component_type = self.entry.type.value
        return 'runsettings: _%sRunsetting' % component_type

    @property
    def component_description(self):
        return self.entry.description.replace('"', '\\"') if self.entry.description else self.component_name

    @property
    def component_version(self):
        return self.entry.version

    @property
    def enums(self):
        enum_str = CLASS_SEP.join(
            param.enum_def for param in self.params
            if type(param.type) == str and param.type.lower() == Enum.TYPE_NAME) + new_line()
        return enum_str if enum_str.strip() else ''

    @property
    def groups(self):
        group_str = new_line() + CLASS_SEP.join(
            param.group_def for param in self.params
            if type(param.type) == str and param.type.lower() == _Group.TYPE_NAME) + new_line()
        return group_str if group_str.strip() else ''

    @property
    def input_cls_fields(self):
        items = [''] + [param.arg_def_in_cls for param in self.params if param.default is None] + \
                [param.arg_def_in_cls for param in self.params if param.default is not None]
        cls_field_string = new_line(indent=4).join(items)
        return cls_field_string if cls_field_string.strip() else new_line(meta='pass', indent=4)

    @property
    def output_cls_fields(self):
        items = [''] + [param.arg_def_in_cls for param in self._outputs]
        cls_field_string = new_line(indent=4).join(items)
        return cls_field_string if cls_field_string.strip() else new_line(meta='pass', indent=4)

    @property
    def func_docstring(self):
        items = [''] + [param.docstring for param in self.params if param.default is None] + \
                [param.docstring for param in self.params if param.default is not None] + \
                [param.docstring for param in self._outputs]
        return new_line(indent=4).join(items)

    @property
    def func_init_args(self):
        items = [''] + ['%s=%s,' % (_sanitize_python_variable_name(param.param.name),
                                    _sanitize_python_variable_name(param.param.name)) for param in self.params]
        return new_line(indent=12).join(items)


class ModuleFileGenerator(BaseGenerator):
    def __init__(self, definitions, workspace, components_from_call, module_name_from_call):
        super().__init__()
        self.subscription_id = workspace.subscription_id
        self.resource_group = workspace.resource_group
        self.workspace_name = workspace.name
        self._components = [ModuleComponentGenerator(definition) for definition in definitions]
        self._components_from_call = components_from_call
        self._module_name_from_call = module_name_from_call

    @property
    def tpl_file(self):
        return GENERATE_MOUDLE_TPL_FILE

    @property
    def entry_template_keys(self):
        return [
            'components_from_call', 'module_name_from_call',
            'component_names', 'all_imports', 'subscription_id',
            'resource_group', 'workspace_name',
            'all_type_runsetting_cls', 'all_components_cls']

    @property
    def all_type_runsetting_cls(self):
        type_generator_dict = {}
        for generator in self._components:
            definition = generator.entry
            component_type = definition.type.value
            if component_type in type_generator_dict \
                    or not definition.runsettings or not definition.runsettings.params:
                continue
            runsettings_definition = definition.runsettings
            runsetting_section_list, _ = _RunSettingsInterfaceGenerator._get_runsettings_display_section_list(
                component_type, runsettings_definition, component_name=component_type)
            type_generator_dict[component_type] = \
                ModuleRunsettingClsGenerator(runsetting_section_list, component_type)
        if not type_generator_dict:
            return new_line() + new_line(meta='# No runsetting class is generated.')
        return new_line() + new_line().join(generator.to_component_entry_code()
                                            for generator in type_generator_dict.values())

    @property
    def all_components_cls(self):
        if not self._components:
            return new_line() + new_line(meta='# No component class is generated.') + new_line()
        return new_line() + new_line().join(generator.to_component_entry_code() for generator in self._components)

    @property
    def component_names(self):
        items = ['#  - azureml://%s/%s/%s/components/%s' % (
            self.subscription_id, self.resource_group, self.workspace_name, generator.component_name)
            for generator in self._components]
        return new_line().join(items)

    @property
    def components_from_call(self):
        return new_line(meta='#     ').join(f'{name!r},' for name in self._components_from_call)

    @property
    def module_name_from_call(self):
        return self._module_name_from_call

    @property
    def all_imports(self):
        component_pkg = 'azure.ml.component'
        component_file = 'azure.ml.component.component'
        _imports = {}
        _pkg_imports = {'azureml.core': ['Workspace'], component_pkg: [],
                        component_file: []}
        if self._components:
            _pkg_imports[component_pkg] += ['Component']
        _has_enum, _has_inputs, _has_outputs, _has_group, _has_runsetting = False, False, False, False, False
        for component_generator in self._components:
            if not _has_enum and component_generator.enums:
                _has_enum = True
                _imports['enum'] = ['Enum']
            if not _has_runsetting and component_generator.entry.runsettings \
                    and component_generator.entry.runsettings.params:
                _has_runsetting = True
                _imports['typing'] = ['Union']
            if not _has_inputs and component_generator.entry.inputs:
                _has_inputs = True
                _imports['pathlib'] = ['Path']
                _pkg_imports[component_file] += ['Input']
            if not _has_outputs and component_generator.entry.outputs:
                _has_outputs = True
                _pkg_imports[component_file] += ['Output']
            if not _has_group and component_generator.groups:
                _has_group = True
                _pkg_imports[component_pkg] += ['dsl']

        def _imports_to_str(import_list):
            return new_line().join(['from %s import %s' % (name, ', '.join(values))
                                    for name, values in import_list.items() if values])
        _imports_str = _imports_to_str(_imports)
        if not _imports_str:
            return _imports_to_str(_pkg_imports)
        return CLASS_SEP.join([_imports_str, _imports_to_str(_pkg_imports)])
