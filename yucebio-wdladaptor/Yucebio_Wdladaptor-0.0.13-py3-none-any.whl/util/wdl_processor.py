from __future__ import annotations
from collections import defaultdict
import os
import re
from typing import Any, Dict, List, OrderedDict

import yucebio_wdladaptor.util.wdl_v1_parser as WDL

class WDLProcessor(object):
    # 使用2个空格作为缩进符
    TOKEN_SEP= "  "
    PATTERN_INDENT_DETECT = re.compile(r"{\s*\n(\s+)")

    def __init__(self, fileWDL: str) -> None:
        self.fileWdl = fileWDL

        # 保存文件原始内容
        self.content = ""
        self.line_contents = []
        # wdl文档树
        self.document: WDL.ParseTree = None

        # 保存更新后的内容
        self.replaces = []

        self.tree_version: WDL.ParseTree = None
        self.tree_imports: WDL.ParseTree = None
        self.meta = defaultdict(list)

        self.tab_size = 2
        self._parse()

    def __str__(self):
        if not self.replaces:
            return self.content

        # return "\n".join([line for line in self.replaces if line and line.strip()])
        empty_line = False
        content = []
        for line in self.replaces:
            if line is None:
                continue
            if not line.strip():
                # 跳过连续空行
                if empty_line:
                    continue
                empty_line = True
            else: 
                empty_line = False
            content.append(line)
        return "\n".join(content)

    def _parse(self):
        """解析WDL并转换为指定平台的新数据
        """
        # 1. 加载入口WDL内容
        with open(self.fileWdl, 'r', encoding='utf8') as r:
            self.content = r.read()
            self.tab_size = len(self.PATTERN_INDENT_DETECT.search(self.content).group(1))

            self.line_contents = self.content.split("\n")

        try:
            self.document = WDL.parse(self.content)
        except Exception as e:
            raise RuntimeError(f"解析[ {self.fileWdl} ]异常: {e}")

        # 2. 解析WDL内容为各个不同的代码块
        self.traversal_document(self.document)


    def traversal_document(self, treeDocument: WDL.ParseTree):
        # 从 document中解析出 version, import, body
        self.tree_version, self.tree_imports, tree_wdl_body = treeDocument.children
        self._parse_import()

        for file_body_element in tree_wdl_body.children:
            # 解析出task
            if not file_body_element.children:
                continue

            ele = file_body_element.children[0]
            ele_name = ele.nonterminal.str
            self.meta[ele_name].append(ele)

    def _parse_import(self):
        # $_gen0 = list($import)
        _imported_wdls: Dict[str, _ImportItem] = {}
        if self.tree_imports and self.tree_imports.children:
            for tree_import in self.tree_imports.children:
                import_item = _ImportItem(tree_import, self)
                if import_item.path in _imported_wdls:
                    pre: _ImportItem = _imported_wdls[import_item.path]
                    raise RuntimeError(f"第{pre.line}行和第{import_item.line}行重复导入相同的wdl：{import_item.path}")
                _imported_wdls[import_item.path] = import_item

        self._imports = {item.namespace: item for item in _imported_wdls.values()}

    @property
    def imports(self) -> Dict[str, _ImportItem]:
        """导入内容
        {
            "namespace": _ImportItem
        }
        """
        return self._imports

    def source_string(self, tree: WDL.ParseTree):
        if isinstance(tree, WDL.Terminal):
            return tree.source_string
        start_line, start_col, end_line, end_col = self._get_range(tree)
        if not start_line:
            return ""

        lines = self.line_contents[start_line-1: end_line]
        if start_line == end_line:
            return lines[0][start_col-1: end_col]

        # 复制一份
        lines = [str(l) for l in lines]
        lines[0] = lines[0][start_col-1:]
        lines[-1] = lines[-1][:end_col-1]
        return "\n".join(lines)

    def _get_range(self, tree: WDL.ParseTree):
        start, end = self.first_terminal(tree), self.last_terminal(tree)
        if not start:
            return None, None, None, None

        # command内部的terminal需要进一步处理换行符
        end_code = end.source_string
        end_lines = end_code.split("\n")
        line_count = len(end_lines)

        end_row, enc_col = end.line + line_count - 1, len(end_lines[-1]) + (end.col if line_count == 1 else 0)

        return start.line, start.col, end_row, enc_col

    def first_terminal(self, tree: WDL.ParseTree):
        if isinstance(tree, WDL.Terminal):
            return tree
        for sub in tree.children:
            t = self.first_terminal(sub)
            if t:
                return t
        return None

    def last_terminal(self, tree: WDL.ParseTree):
        if isinstance(tree, WDL.Terminal):
            return tree
        for sub in reversed(tree.children):
            t = self.last_terminal(sub)
            if t:
                return t
        return None

    def get_terminal(self, tree: WDL.ParseTree):
        t = []
        if isinstance(tree, WDL.Terminal):
            return [tree]
        for sub in tree.children:
            t += self.get_terminal(sub)
        return t

    def replace_tree(self, new_code: str, raw: WDL.ParseTree=None, parent: WDL.ParseTree=None):
        if new_code is None:
            return
        if not self.replaces:
            self.replaces = self.content.split("\n")
        
        # 区分插入和替换
        if not raw:
            # TODO: 处理插入代码
            print("暂时不支持插入代码：", new_code)
            return

        start_line, start_col, end_line, end_col = self._get_range(raw)
        if not start_line:
            print("暂时不支持插入代码：", new_code)
            # TODO: 处理插入代码
            return

        # TODO: 校验该区域是否发生过替换

        if start_line == end_line:
            line = self.replaces[start_line-1]
            self.replaces[start_line-1] = line[:start_col-1] + new_code + line[end_col:]
            return

        # 复制一份
        first, last = self.replaces[start_line-1], self.replaces[end_line-1]
        # print("first:", repr(first), "\nlast: ", repr(last), "\nend_col:", end_col, len(self.replaces))
        # 清空原来的数据
        self.replaces[start_line-1: end_line] = [None] * (end_line - start_line +1)
        self.replaces[start_line-1] = first[:start_col-1] + new_code
        # 如果已经发生过替换，该区域内容为None；就不要在替换了
        if last and last[end_col:]:
            self.replaces[end_line-1] = last[end_col:]
        return

class _ImportItem(object):
    """管理import的辅助类: 不考虑alias, 需要有as

    $import = :import $static_string $_gen5 $_gen6 -> Import( uri=$1, namespace=$2, aliases=$3 )
    $import = :import $static_string optional($import_namespace) list($import_alias)

    $import_namespace = :as :identifier -> $1
    $import_alias = :alias :identifier :as :identifier -> ImportAlias( old_name=$1, new_name=$3 )
    """
    def __init__(self, tree_import: WDL.ParseTree, processor: WDLProcessor) -> None:
        self.tree = tree_import
        self.processor = processor

        # 自定义属性
        self.path = ""
        self.line = 0
        self.namespace = ""
        self.wdl = None

        self._parse()

    @property
    def meta(self):
        return {
            "line": self.line,
            "path": self.path,
            "namespace": self.namespace
        }
    
    def _parse(self):
        _str, _static_string, _gen5, _gen6 = self.tree.children
        # 包含引号的内容
        self.line = _str.line
        self.path = self.processor.source_string(_static_string.children[1]).strip(' \'"')
        
        relpath = os.path.join(os.path.dirname(self.processor.fileWdl), self.path)
        self.wdl = TaskProcessor(relpath)

        if not _gen5.children:
            raise RuntimeError(f"line #{self.line} 导入wdl时需要指定as内容")

        _import_namespace: WDL.ParseTree = _gen5.children[0]
        identifier: WDL.Terminal = _import_namespace.children[1]
        self.namespace = identifier.source_string

class WorkflowProcess(WDLProcessor):
    """Workflow处理器

    1. 有且只能由1个workflow
    2. 只支持version, imports, workflow元素
    3. workflow中仅支持inputs, scatter, call
    """

    def __init__(self, fileWDL: str) -> None:
        self.tree_workflow: WDL.ParseTree = None
        self.workflow_meta = {
            "inputs": {},
            "calls": {}
        }

        super().__init__(fileWDL)

    def _parse(self):
        super()._parse()

        if self.meta.get('task'):
            raise RuntimeError("请不要在workflow中定义task")

        # 校验1： 存在且只能存在1个workflow
        if not self.meta.get('workflow'):
            raise RuntimeError("未定义workflow")
        if len(self.meta['workflow']) != 1:
            raise RuntimeError("不允许同时定义多个workflow")

        self.tree_workflow = self.meta['workflow'][0]

        self._traversal_workflow(self.tree_workflow)

    def _traversal_workflow(self, tree_workflow: WDL.ParseTree):
        """解析workflow，生成input对应关系

        Args:
            tree_workflow (WDL.ParseTree)

        1. workflow中可能存在input
        2. call中可能存在重新赋值

        Return：
        {
            "name": "{workflow_name}",
            "input": {},
            "tasks": [
                {"name": "", "inputs": {}}, ...
            ]
        }
        """
        supported_elements = ['call', 'scatter', 'inputs']
        self.tree_workflow = tree_workflow

        # $workflow = :workflow :identifier :lbrace $_gen15 :rbrace -> Workflow( name=$1, body=$3 )
        self.workflow_name = tree_workflow.children[1].source_string.strip()
        tree_gen15: WDL.ParseTree = tree_workflow.children[3]

        # $_gen15 = list($wf_body_element)
        for wf_body_element in tree_gen15.children:
            element_name = wf_body_element.children[0].nonterminal.str
            if element_name not in supported_elements:
                raise RuntimeError(f"检测到不支持的元素{element_name}, workflow中仅支持{supported_elements}")

            parse_func = getattr(self, f"_parse_workflow_{element_name}", None)
            if not parse_func:
                continue

            parse_func(wf_body_element.children[0])

        # 所有call处理完之后，生成call vs task对应关系
        # 遍历calls初始化被调用task对应关系
        call_tasks = {}
        for wp_call_item in self.calls.values():
            # wp_call_item.inputs
            ns = wp_call_item.namespace
            task_name = wp_call_item.task_name

            if ns not in call_tasks:
                call_tasks[ns] = {}
            # 同一个task可能重复调用，并赋予不同的alias
            if task_name not in call_tasks[ns]:
                call_tasks[ns][task_name] = []
            call_tasks[ns][task_name].append(wp_call_item)
        self.call_tasks = call_tasks

        # 检测是否存在未使用的import内容
        for ns, import_item in self.imports.items():
            if ns not in call_tasks:
                raise RuntimeError(f"Line #{import_item.line} 请移除未使用的导入内容 {import_item.path}")

    def _parse_workflow_call(self, tree_call: WDL.ParseTree):
        """解析workflow中出现的call内容"""
        # $call = :call :fqn optional($alias) optional($call_brace_block) -> Call(task=$1, alias=$2, body=$3)
        item = _WorkflowCallItem(tree_call, self)
        self.workflow_meta['calls'][item.alias] = item

    @property
    def name(self):
        return self.workflow_name

    @property
    def inputs(self) -> dict:
        """workflow级别的输入数据

        Returns:
            dict: { key: {type, identifier, defalut?}}
        """
        return self.workflow_meta['inputs']

    @property
    def calls(self) -> Dict[str, _WorkflowCallItem]:
        return self.workflow_meta['calls']

    def _parse_workflow_inputs(self, tree_inputs: WDL.ParseTree):
        """解析workflow中的input内容，后期可以与输入文件中的workflow_inputs做校验
        """
        # $inputs = :input :lbrace $_gen10 :rbrace -> Inputs( inputs=$2 )
        if not tree_inputs.children:
            return

        tree_gen10 = tree_inputs.children[2]
        # $_gen10 = list($input_declaration)
        for input_declaration in tree_gen10.children:
            # $input_declaration = $type_e :identifier $_gen13
            type_e, indetifier, tree_gen13 = input_declaration.children
            # TODO: 找到与资源相关的变量, 考虑call中可能使用了其他参数名来管理资源
            # 提取变量名 类型 和 默认值
            _meta = {
                "type": self.source_string(type_e),
                "identifier": self.source_string(indetifier).strip(),
            }
            if tree_gen13.children:
                # 提取默认值 
                # $_gen13 = optional($setter) 
                # $setter = :equal $e -> $1
                _meta['default'] = self.source_string(tree_gen13.children[0].children[1])
            self.workflow_meta['inputs'][_meta['identifier']] = _meta

    def _parse_workflow_scatter(self, tree_scatter: WDL.ParseTree):
        # $scatter = :scatter :lparen :identifier :in $e :rparen :lbrace $_gen15 :rbrace
        tree_gen15 = tree_scatter.children[-2]

        # $_gen15 = list($wf_body_element)
        for wf_body_element in tree_gen15.children:
            element_name = wf_body_element.children[0].nonterminal.str
            if element_name not in ['call', 'scatter', 'declaration']:
                raise RuntimeError(f"检测到不支持的元素{element_name}, scatter中仅支持call")

            parse_func = getattr(self, f"_parse_workflow_{element_name}", None)
            if not parse_func:
                continue

            parse_func(wf_body_element.children[0])

class _WorkflowCallItem(object):
    """Workflow Call管理工具：支持修改input内容

    Args:
        object ([type]): [description]
    """

    def __init__(self, tree: WDL.ParseTree, processor: WorkflowProcess) -> None:
        self.tree = tree
        self.processor = processor

        # 自定义属性
        self.namespace = ""
        self.task_name = ""
        self.alias = ""
        self.inputs = OrderedDict()

        self._parse()

    def _parse2(self):
        ast = self.tree.ast()

        # {import_namespace}.{task_name}
        ast_task: WDL.Terminal = ast.attr('task')
        # import_namespace, task_name = ast_task.source_string.strip().split('.')
        self.namespace, self.task_name = ast_task.source_string.strip().split('.')

        # as {alias}
        ast_alias: WDL.Terminal = ast.attr('alias')
        # alias = ast_alias.source_string.strip()
        self.alias = ast_alias.source_string.strip()
        if not self.alias:
            raise RuntimeError(f"[{self.processor.fileWdl}@{self.processor.workflow_name}] [{self.namespace}.{self.task_name}] 需要指定AS")

        # $call_body = :input :colon list($input_kv, :comma) -> CallBody(inputs=$2)
        ast_call_body: WDL.Ast = ast.attr('body')
        list_ast_call_input: List[WDL.Ast] = ast_call_body.attr('inputs')

        # $input_kv = :identifier :equal $e -> ObjectKV(key=$0, value=$2)
        for objectkv in list_ast_call_input:
            key = objectkv.attr('key').source_string
            value = objectkv.attr('value').source_string
            # self.inputs.append([key, value])
            self.inputs[key] = value

    def _parse(self):
        # $call = :call :fqn $_gen16 $_gen17 -> Call( task=$1, alias=$2, body=$3 )
        _, name, gen16, gen17 = self.tree.children
        self.namespace, self.task_name = self.processor.source_string(name).strip().split('.')

        # $gen16 = optional($alias)
        # $alias = :as :identifier
        if not gen16.children:
            raise RuntimeError(f"[{self.processor.fileWdl}@{self.processor.workflow_name}] [{self.namespace}.{self.task_name}] 需要指定AS")
        self.alias = self.processor.source_string(gen16.children[0].children[1]).strip()

        self.inputs = {}
        # $gen17 = optional($call_brace_block)
        if not gen17.children:
            return
        call_brace_block = gen17.children[0]
        # $call_brace_block = :lbrace $gen18 :rbrace
        gen18 = call_brace_block.children[1]
        # $gen18 = optional($call_body)
        if not gen18.children:
            return

        call_body = gen18.children[0]
        # $call_body = :input :colon $_gen19
        gen19 = call_body.children[2]

        # gen19 = list(input_kv :colon)
        for child in gen19.children:
            if isinstance(child, WDL.Terminal):
                continue
            # $input_kv = :identifier :equal $e
            identifier, _, expr = child.children
            self.inputs[identifier.source_string.strip()] = self.processor.source_string(expr).strip()

    def __str__(self):
        return self.tree.ast().dumps(indent=1)


class TaskProcessor(WDLProcessor):

    def __init__(self, fileWDL: str) -> None:
        self.meta_tasks: List[_TaskItem] = []
        self.tree_tasks = []
        super().__init__(fileWDL)

    def _parse(self):
        super()._parse()

        if self.meta.get('workflow'):
            raise RuntimeError("请不要在task中定义workflow")

        if self.meta.get('imports'):
            raise RuntimeError("请不要在task中使用imports")

        # 依次处理每个task
        for task_tree in self.meta['task']:
            self.meta_tasks.append(_TaskItem(task_tree, self))

    def __str__(self):
        # 依次对每个子task执行__str__
        for ti in self.meta_tasks:
            ti.do_update()

        return super().__str__()

class _TaskItem(object):
    # input中的保留字段
    RESERVED_INPUT_TOKENS = ['cluster']
    # 需要增加一个资源类型： 按需还是竞价
    RUNTIME_RESCOURCE_KEYS = ['cpu', 'memory', 'rescource_type']

    def __init__(self, tree_task:WDL.ParseTree, processor: TaskProcessor) -> None:
        super().__init__()
        self.tree = tree_task
        self.processor = processor
        self.token_tab = " " * self.processor.tab_size

        # 自定义属性
        self.name = ""
        self.meta: Dict[str, WDL.ParseTree] = {}
        self._inputs = {}
        self._runtime = {}
        # 当前任务的可变资源
        self.rescources = {}

        self._dirty = {}
        self._parse()

    def do_update(self):
        """依次检查每个关键元素是否发生变更，若有变更，则执行替换
        """
        # 1. 处理input
        if self._dirty.get('input'):
            # new_input = f"\n{self.token_tab}input " + '{'
            new_input = f"input " + '{'
            for k, item in self.inputs.items():
                new_input += "\n" + self.token_tab * 2 + "{type} {name}".format(**item)
                if item.get('default'):
                    new_input += f" = {item['default']}"
            new_input += "\n" + self.token_tab + '}'
            self.processor.replace_tree(new_input, self.meta['inputs'], parent=self.tree)

        # 2. 处理runtime
        if self._dirty.get('runtime'):
            new_runtime = "runtime {"
            # new_runtime = "\n" + self.token_tab + "runtime {"
            for k,v in self.runtime.items():
                new_runtime += '\n' + self.token_tab*2 + f"{k}: {v}"
            new_runtime += '\n' + self.token_tab + '}'
            self.processor.replace_tree(new_runtime, self.meta['runtime'], parent=self.tree)

        # 3. 处理command
        if self._dirty.get('command'):
            new_command = "command <<<\n" + self._new_command_content + "\n" + self.token_tab + ">>>"
            self.processor.replace_tree(new_command, self.meta['command'], parent=self.tree)

    @property
    def inputs(self):
        return self._inputs

    @property
    def runtime(self) -> dict:
        return self._runtime

    def _parse(self):
        task_name: WDL.Terminal = self.tree.children[1]
        tree_task_body: WDL.ParseTree = self.tree.children[3]

        task = {"tree": self.tree, "name": task_name.source_string, "simg": "", "e_simg": False}

        self.name: str = task_name.source_string

        for task_section in tree_task_body.children:
            # outputs
            if not (task_section.children and task_section.children[0].nonterminal.str in ["runtime", "command", "inputs"]):
                continue

            tree_section = task_section.children[0]
            section_name = tree_section.nonterminal.str
            self.meta[section_name] = tree_section

        # print(">>>>>> parse", self.processor.fileWdl, self.name)

        self._parse_inputs()
        self._parse_runtime()
        self._parse_command()

        # 根据 runtime 和 inputs 计算当前任务的可变资源字段
        for k in self.RUNTIME_RESCOURCE_KEYS:
            if k not in self.runtime:
                continue
            runtime_value = self.runtime[k]
            if runtime_value in self.inputs:
                input_resource_item = self.inputs[runtime_value]
                # 若资源变量有默认值，则将CPU和MEM默认值转换为数值
                if input_resource_item.get('default'):
                    if k != 'rescource_type':
                        try:
                            input_resource_item['default'] = int(input_resource_item['default'])
                        except Exception:
                            raise RuntimeError(f"{self.processor.fileWdl}@{self.name} INPUT中的字段[{runtime_value}]的默认值必须是整数")
                self.rescources[runtime_value] = {**input_resource_item, "runtime": k}

    def _parse_inputs(self):
        tree_inputs = self.meta['inputs']
        # $inputs = :input :lbrace $_gen10 :rbrace -> Inputs( inputs=$2 )
        tree_gen10 = tree_inputs.children[2]
        # $_gen10 = list($input_declaration)
        if not tree_gen10.children:
            return

        for tree_input_declaration in tree_gen10.children:
            _meta = {}
            # $input_declaration = $type_e :identifier $_gen13
            _type, identifier, gen13 = tree_input_declaration.children
            _meta['type'] = self.processor.source_string(_type).strip()
            _meta['name'] = self.processor.source_string(identifier).strip()
            # _meta['type'] = self.processor.source_string(_type).strip()
            if gen13.children:
                # $gen13 = optional($setter)
                # $setter = :equal $e -> $1
                _, expr = gen13.children[0].children
                _meta['default'] = self.processor.source_string(expr).strip()
            self._inputs[_meta['name']] = _meta

        if 'simg' not in self.inputs or self.inputs['simg']['type'] != 'String':
            raise RuntimeError(f"{self.processor.fileWdl}@{self.name} INPUT中必须提供[String simg]")


    def _parse_runtime2(self):
        # $runtime = :runtime $rt_map -> Runtime(map=$1)
        ast = self.meta['runtime'].ast()

        runtime_maps: List[WDL.Ast] = ast.attr('map')
        for runtime_map in runtime_maps:
            # $kv = :identifier :colon $e -> RuntimeAttribute(key=$0, value=$2)
            key = runtime_map.attr('key').source_string.strip()
            value = runtime_map.attr('value')
            if isinstance(value, WDL.Terminal):
                value = value.source_string.strip()
            self._runtime[key] = value

        # validate 1: 必须提供simg
        if 'simg' not in self._runtime:
            raise RuntimeError(f"{self.processor.fileWdl}@{self.name} runtime中必须提供simg")

        # validate 2: 只能使用memory
        if 'mem' in self._runtime:
            raise RuntimeError(f"{self.processor.fileWdl}@{self.name} runtime中请使用memory代替mem")

    def _parse_runtime(self):
        tree = self.meta['runtime']
        # $runtime = :runtime $rt_map -> Runtime(map=$1)
        tree_rt_map: WDL.ParseTree = tree.children[1]
        # $rt_map = :lbrace $_gen11 :rbrace
        gen11: WDL.ParseTree = tree_rt_map.children[1]
        # $_gen11 = list($kv)
        for tree_kv in gen11.children:
            # $kv = :identifier :colon $e
            identifier: WDL.Terminal = tree_kv.children[0]
            tree_expr: WDL.ParseTree = tree_kv.children[2]
            key = identifier.source_string.strip()
            value = self.processor.source_string(tree_expr)
            self._runtime[key] = value

        if 'simg' not in self._runtime:
            raise RuntimeError(f"{self.processor.fileWdl}@{self.name} runtime中必须提供simg")

        # validate 2: 只能使用memory
        if 'mem' in self._runtime:
            raise RuntimeError(f"{self.processor.fileWdl}@{self.name} runtime中请使用memory代替mem")

    def _parse_command(self):
        # runtime中必须提供simg
        if 'simg' not in self.runtime:
            raise RuntimeError(f"{self.processor.fileWdl}@{self.name} RUNTIME中必须提供simg参数")
        simg = self.runtime['simg']
        # runtime的simg必须是变量
        if simg not in self.inputs:
            raise RuntimeError(f"{self.processor.fileWdl}@{self.name} RUNTIME中的simg参数不是变量或找不到input中对应的simg变量")

        tree_gen8: WDL.ParseTree = self.meta['command'].children[2]
        self.command_content = self.processor.source_string(tree_gen8).strip('\n')

        if not re.search(r"set\s+-e\s*\n", self.command_content):
            raise RuntimeError(f"{self.processor.fileWdl}@{self.name} COMMAND必须以set -e开头，且必须换行")

        self._check_command_indent_size(self.command_content)

    def _check_command_indent_size(self, command_content: str):
        """以命令的第一行为基准，后续行按照第一行的缩进格式进行调整
        """
        min_space = self.processor.tab_size * 2
        first_line, line_index = True, 0
        self.command_content_lines = []
        for line in command_content.split('\n'):
            line_index += 1
            tmp = line.lstrip()
            self.command_content_lines.append(tmp)
            # 跳过空行
            if not tmp:
                continue
            space = len(line) - len(tmp)
            if first_line:
                # 首行缩进必须正确
                if space != min_space:
                    raise RuntimeError(f"{self.processor.fileWdl}@{self.name} COMMAND首行缩进({space}个空格)不正确，请按照{min_space}个空格(2个tab)设置首行缩进")
                # 首行必须是set -e
                if 'set -e' not in tmp:
                    raise RuntimeError(f"{self.processor.fileWdl}@{self.name} COMMAND必须以set -e开头 {repr(tmp)}")

                first_line = False
            if space < min_space:
                raise RuntimeError(f"{self.processor.fileWdl}@{self.name} COMMAND 第{line_index}行缩进不正确({tmp[:10]}...)")


    def update_input(self, key: str, value_type: str = None, default: Any = None):
        """更新input内容，当value_type为None时，表示删除该key

        Args:
            key (str): 待更新的input内容
            value_type (str, optional): 新的字段类型，设置为None时表示删除字段
            default (Any, optional): 设置新字段默认值. Defaults to None.
        """
        self._dirty['input'] = True
        # value_type未设置时，表示删除字段
        if not value_type:
            if key in self._inputs:
                del self._inputs[key]
        # 否则，更新为新的类型，并设置默认值
        else:
            self._inputs[key] = {"type": value_type, 'name': key}
            if default:
                self._inputs[key]['default'] = default

    def delete_input(self, key: str):
        return self.update_input(key, value_type=None)

    def update_runtime(self, key: str, value: Any = None):
        """更新或删除runtime内容，当value为None时，删除对应的key

        Args:
            key (str): 待更新或删除的runtime键
            value (Any, optional): 更新后的值. Defaults to None.
        """
        self._dirty['runtime'] = True
        # value设置为None时，删除对应的key
        if not value:
            if key in self._runtime:
                del self._runtime[key]
        # 否则，直接更新为新的数据
        else:
            self._runtime[key] = value

    def delete_runtime(self, key: str):
        return self.update_runtime(key, None)

    def delete_content(self):
        self.processor.replace_tree("\n", self.tree)

    def update_command(self, new_command: str):
        self._new_command_content = new_command
        self._dirty['command'] = True
