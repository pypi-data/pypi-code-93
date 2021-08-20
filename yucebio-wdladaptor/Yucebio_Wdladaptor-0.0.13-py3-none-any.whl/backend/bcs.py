import click
import datetime
from yucebio_wdladaptor.backend.base import BaseAdaptor
from yucebio_wdladaptor.util.wdl_processor import _TaskItem, _WorkflowCallItem

class Adaptor(BaseAdaptor):
    PLATFORM = "BCS"
    COMMAND_PREFIX = "singularity exec -W /cromwell_root -B %s,/cromwell_root,/cromwell_inputs ~{simg}"
    RUNTIME_RESCOURCE_KEYS = ['cpu', 'memory']
    RUNTIME_RESCOURCE_KEYS2 = ['cpu', 'memory', 'rescource_type']
    SUPPORTED_RUNTIME_ATTRIBUTES = RUNTIME_RESCOURCE_KEYS + ['systemDisk', 'cluster', 'mounts', 'vpc', 'continueOnReturnCode', 'failOnStderr']

    def convert(self):
        """遍历每个import，依次转换每个task

        Description
            1. 常规情况下，input.json无需处理，只有阿里云中涉及到动态资源时，需要添加额外的input
            2. 常规情况下，workflow无需处理，只有阿里云中涉及到动态资源时，可能需要处理call.input和workflow.input
            3. 大部分情况下需要对task的command做转换
        原理
            1. 加载json并解析
            2. 加载workflow.wdl并解析
            3. 遍历workflow.wdl的imports，依次处理每个task
            3.1 根据workflow.calls决定是否需要移除未使用的task
            3.2 阿里云根据task是否存在可变资源决定是否修改input.json和workflow
            3.3 根据平台修改command
        """
        # 遍历calls初始化被调用task对应关系
        call_tasks = self.workflow_processor.call_tasks

        # 1. 遍历每个import
        for ns, import_item in self.workflow_processor.imports.items():
            if ns not in call_tasks:
                raise RuntimeError(f"Line #{import_item.line} 请移除未使用的导入内容 {import_item.path}")
            call_task_info = call_tasks[ns]

            # 2. 依次检测每个子任务，跳过无关的task
            task_processor = import_item.wdl
            click.secho(f"\n########## Process WDL [{task_processor.fileWdl}] ...", fg='yellow')
            for wdl_task_item in task_processor.meta_tasks:
                task_name = wdl_task_item.name
                if task_name not in call_task_info:
                    print(f"########## Task [{wdl_task_item.name}] 未参与本次分析，准备移除...")
                    wdl_task_item.delete_content()
                    continue

                print(f"########## Process Task [{task_name}] ")
                # 无论如何，先处理command
                self.convert_command(wdl_task_item)

                # 移除runtime里面的simg
                if 'simg' in wdl_task_item.runtime:
                    wdl_task_item.delete_runtime('simg')

                task_default_rescource = self.convert_task_rescource(wdl_task_item)

                # 当任务没有可变资源字段时，无需额外处理
                if not wdl_task_item.rescources:
                    continue

                # 存在可变资源字段，需要进一步处理call、workflow_input
                # 5. 继续向上到call中，更新里面的资源字段，可能存在多个call
                call_item: _WorkflowCallItem
                for call_item in call_task_info[task_name]:
                    # 获取当前call所提供的资源，以及来源于workflow_input中的资源变量
                    self.convert_call_input(call_item, wdl_task_item, task_default_rescource)

            # print("in bcs end:", id(self), task_processor.fileWdl, id(task_processor))

    def cluster(self, cpu: int=None, memory: int=None, rescource_type: str='Spot'):
        """根据cpu和mem参数生成可用的cluster

        参考： https://batchcompute.console.aliyun.com/cn-zhangjiakou/quotas

        Args:
            cpu (int): cpu配置
            memory (int): 内存配置， nG

        """
        rescource_type = str(rescource_type).strip('\'"').lower()
        # 确保名词书写正确
        if rescource_type not in ['ondemand', 'spot']:
            raise RuntimeError("阿里云资源类型必须填写为 OnDemand 或 Spot")
        rescource_type = 'OnDemand' if rescource_type != 'spot' else 'Spot'

        image_id = "img-dovfustcp606ko1kpqq000"
        available_bcs_rescource = self.config("available_bcs_rescource")
        if not available_bcs_rescource or not available_bcs_rescource.get("updated_at"):
            raise RuntimeError("阿里云可用实例类型无效，请执行 yucebio_wdl_adaptor update-bcs-instance -i ACCESS_ID_KEY -s ACCESS_ID_SECRECT 来获取最新实例配置")
        last_update_at = datetime.datetime.fromisoformat(available_bcs_rescource["updated_at"])
        if (datetime.datetime.today() - last_update_at).days > 7:
            click.secho("WARNING: 距离上次更新阿里云可用实例类型已经超过7天，为避免实例变更导致任务无法执行，请执行 yucebio_wdl_adaptor update-bcs-instance -i ACCESS_ID_KEY -s ACCESS_ID_SECRECT 来获取最新实例配置", fg="yellow")
            raise RuntimeError("阿里云可用实例类型配置可能已过期，请执行 yucebio_wdl_adaptor update-bcs-instance -i ACCESS_ID_KEY -s ACCESS_ID_SECRECT 来获取最新实例配置")

        expected_key = "AvailableSpotInstanceType" if rescource_type == 'Spot' else "AvailableClusterInstanceType"

        cpu2mem = {}
        for instance_config in available_bcs_rescource[expected_key]:
            # dict_keys(['CpuCore', 'InstanceType', 'MemorySize', 'Network'])
            _cpu, _mem, instance_type = instance_config['CpuCore'], instance_config['MemorySize'], instance_config['InstanceType']
            if _cpu not in cpu2mem:
                cpu2mem[_cpu] = {}
            if _mem not in cpu2mem[_cpu]:
                cpu2mem[_cpu][_mem] = []
            cpu2mem[_cpu][_mem].append(instance_type)

        if not cpu:
            cpu = 2
        if not memory:
            memory = 4

        for c in sorted(cpu2mem.keys()):
            if c < cpu:
                continue
            m2ins = cpu2mem[c]
            for m in sorted(m2ins.keys()):
                if m < memory:
                    continue
                # print(f">>>>>>> CPU({cpu} => {c}) MEM({memory} => {m}) {m2ins[m][0]} <<<<<<<<<")
                return f"{rescource_type} {m2ins[m][0]} {image_id}"


        raise RuntimeError(f"无法找到满足最低需求[cpu: {cpu}, mem: {memory}]的阿里云实例类型")

    def convert_command(self, ti: _TaskItem):
        tab = ' ' * ti.processor.tab_size
        command_prefix = self.COMMAND_PREFIX % self.bind_path

        new_command_contents = "\n".join([
            f"{tab}{tab}{command_prefix} bash -s <<'ENDOFCMD'",
            *[f"{tab}{tab}{tab}{line}" for line in ti.command_content_lines],
            f"{tab}{tab}ENDOFCMD"
        ])
        ti.update_command(new_command_contents)

    def convert_task_rescource(self, wdl_task_item: _TaskItem):
        """处理task中的可变资源，返回该task中计算出的资源默认值

        Args:
            wdl_task_item (_TaskItem): 。。。
        """
        # 无论如何都要先转换下runtime的资源字段
        runtime_default_data = self.convert_runtime(wdl_task_item)
        if not bool(wdl_task_item.rescources):
            return {}

        # 需要转换task_input
        return self.convert_task_input(wdl_task_item, runtime_default_data)

    def convert_runtime(self, wdl_task_item: _TaskItem):
        """转换runtime中的资源值，返回常量资源的默认值

        Args:
            wdl_task_item (_TaskItem): ...
        """
        runtime_resouce_data, runtime_default_data, input_rescource_keys = {}, {}, []

        for k in wdl_task_item.RUNTIME_RESCOURCE_KEYS:
            if k not in wdl_task_item.runtime:
                continue
            v = wdl_task_item.runtime[k]
            runtime_resouce_data[k] = v
            if v in wdl_task_item.inputs:
                input_rescource_keys.append([k, v])
            else:
                if k != 'rescource_type':
                    try:
                        v = int(v)
                    except Exception:
                        raise RuntimeError(f"[{wdl_task_item.processor.fileWdl}@{wdl_task_item.name}] RUNTIME属性[{k}]不是整数或者未找到对应的input变量")
                runtime_default_data[k] = v
            # 移除runtime中的资源字段
            wdl_task_item.delete_runtime(k)

        if not input_rescource_keys:
            default_cluster = self.cluster(**runtime_default_data)
            # print(f"{wdl_task_item.processor.fileWdl}@{wdl_task_item.name} 无可变资源，设置cluster为 '{default_cluster}', 资源量{runtime_default_data}")
            wdl_task_item.update_runtime('cluster', f'"{default_cluster}"')
        else:
            wdl_task_item.update_runtime('cluster', "cluster")
        
        self.filter_or_append_runtime_attributes(wdl_task_item)
        return runtime_default_data

    def convert_task_input(self, wdl_task_item: _TaskItem, runtime_default_data: dict={}):
        """转换task的input中的资源值，只能新增字段，需要校验字段被占用的情况

        Args:
            wdl_task_item (_TaskItem): ...
        """

        input_default_data, shouldCalcCluster = {}, True
        for input_rescource_key, input_rescource_item in wdl_task_item.rescources.items():
            if input_rescource_item.get('default'):
                # 解析过程中已经确保资源字段默认值是数值了
                input_default_data[input_rescource_item['runtime']] = input_rescource_item['default']
            else:
                # 当且仅当input中所有资源字段都有默认值时，需要在input中设置cluster的默认值
                shouldCalcCluster = False

        task_default_rescource = {**runtime_default_data, **input_default_data}
        # # 当input中所有资源字段都有默认值时，需要在input中设置cluster的默认值
        default_cluster = None
        if shouldCalcCluster:
            # click.secho(f"input中的所有资源字段都有默认值，需要计算cluster， {input_default_data}", fg='green')
            default_cluster = '"%s"' % self.cluster(**task_default_rescource)
        wdl_task_item.update_input('cluster', 'String', default = default_cluster)
        return task_default_rescource

    def convert_call_input(self, call_item: _WorkflowCallItem, wdl_task_item: _TaskItem, task_default_rescource: dict = {}):
        """更新指定call的input。 返回需要提供给该call的资源变量及其来源。 @2021年3月25日 call中不允许设置资源变量

        Args:
            call_item (_WorkflowCallItem): ...
            wdl_task_item (_TaskItem): ...
            task_default_rescource (dict, optional): .... Defaults to {}.
        Description
            1. call中指定了task_input中的所有资源变量的默认值 ==> 可以处理：直接在call中处理
            2. call中未指定任何可变资源                      ==> 可以处理：直接到json中处理
            3. 其他情况                                     ==> 无法处理
            3.1 task存在cpu和mem两种可变资源，call中指定了cpu的默认值，json中指定了mem的默认值
                call： 保留cpu默认值，增加cluster变量
                json： 保留mem默认值，增加cluster，设置默认值
            3.2 task存在cpu变量，call中将cpu指向workflow.input的变量，workflow.input中设置了默认值
                call： 保留cpu默认值，增加cluster变量
                workflow.input： 保留mem默认值，增加cluster，设置默认值
            3.3 task存在cpu变量，call中将cpu指向workflow.input的变量，workflow.input中引用了json的值
                call: 保留变量，增加cluster：cluster_{call_alias}
                workflow.input: 保留原变量，增加变量cluster_{call_alias}
                json： 增加workflow级别字段 cluster_{call_alias}并计算默认值
        特殊场景：
            task里面有cpu和mem，其中mem有默认值
            call中设置了cpu的默认值，没有mem
            此时： input.json里面可能设置了mem值，也可能没有
        """
        # 记录该call依赖的json级别的输入：task中声明了资源字段，call中未指定该字段时，需要有json中对应的call_alias提供
        # 特别的，若json级别的依赖在task里面有默认值，此时json级别该参数就变成可选参数了，此时需要根据json中是否提供该数据来决定call中使用变量还是常量的cluster
        required_json_inputs = []
        # 记录该call依赖的workflow级别的输入：task中声明了资源字段，call中设置了对应字段，但不是常量值，此时数据需要有workflow.input提供
        # 特别的，若该依赖在task里有默认值，则无论如何，该默认值需要被屏蔽
        required_workflow_inputs = []

        # 获取并记录json中提供的当前call对应的所有字段以及资源字段
        json_task_inputs, json_task_rescouce_data = self.input_processor.call_input(call_item.alias), {}
        # 获取并记录json中提供的workflow级别的字段以及其中的资源字段
        json_workflow_inputs, json_workflow_rescource_data = self.input_processor.inputs, {}
        workflow_inputs, workflow_defalut_rescource_data = self.workflow_processor.inputs, {}

        # 记录当且call设置的资源字段以及值，若值时常量，记录下默认值
        rescource_data, default_data = {}, {}
        # 检测call.input中是否存在资源变量，若存在则直接报错
        for rescource_key, task_rescource_item in wdl_task_item.rescources.items():
            # 当前资源值在runtime中的key： cpu或mem或rescource_type
            runtime_key = task_rescource_item['runtime']

            if rescource_key not in call_item.inputs:
                required_json_inputs.append(rescource_key)
                # 只要这个字段出现在json中，就不要在call计算cluster
                if rescource_key in json_task_inputs:
                    json_task_rescouce_data[runtime_key] = json_task_inputs[rescource_key]
                else:
                    # 这个值一定要有默认值
                    if runtime_key not in task_default_rescource:
                        raise RuntimeError(f"需要配置{self.workflow_processor.workflow_name}.{call_item.alias}.{rescource_key}")
                continue
            # raise RuntimeError(f"文件：{self.workflow_processor.fileWdl}不允许在流程的Call[{call_item.alias}]中设置资源变量[{rescource_key}]")
            rescource_data[rescource_key] = call_item.inputs[rescource_key]

            # 检测input中的值是常量还是变量： 如果是变量，它一定是workflow.inputs中的变量
            if rescource_data[rescource_key] in workflow_inputs:
                # 需要记录workflow.input中的资源字段与runtime中的字段对应关系
                workflow_rescource_key = rescource_data[rescource_key]
                required_workflow_inputs.append([workflow_rescource_key, runtime_key])
                if workflow_rescource_key in json_workflow_inputs:
                    # 资源值最终从json提取
                    # cpu和mem需要转换为整数
                    if runtime_key != 'rescouce_type':
                        try:
                            json_workflow_rescource_data[runtime_key] = int(json_workflow_inputs[workflow_rescource_key])
                        except Exception:
                            raise RuntimeError(f"字段{self.workflow_processor.workflow_name}.{workflow_rescource_key}无法转换为整数")
                else:
                    # 资源值有默认值
                    workflow_input_item = workflow_inputs[workflow_rescource_key]
                    # 校验：必须提供默认值
                    if not workflow_input_item.get('default'):
                        raise RuntimeError(f"{self.workflow_processor.fileWdl}@{self.workflow_processor.workflow_name} 未配置INPUT中参数[{workflow_rescource_key}]的值")
                    # TODO: 需要校验默认值格式！
                    workflow_defalut_rescource_data[runtime_key] = workflow_input_item['default']
                # raise RuntimeError(f"[{self.workflow_processor.fileWdl}@{self.workflow_processor.workflow_name}]流程的CALL[{call_item.alias}]中的资源变量[{rescource_key}]只能设置常量")
                continue
            try:
                default_data[runtime_key] = int(rescource_data[rescource_key]) if runtime_key != 'rescouce_type' else rescource_data[rescource_key]
            except Exception:
                raise RuntimeError(f"{self.workflow_processor.fileWdl}@{self.workflow_processor.workflow_name} CALL[{call_item.alias}] input中的资源字段[{rescource_key}]的默认值必须是整数")

        # 1. call中未定义资源字段，即所有资源字段都依赖于json。此时只需要在input的当前call中增加cluster，并根据json中的数据和task中的数据计算出实际值
        if not rescource_data:
            # print("需要在json中配置资源值", required_json_inputs)
            # 根据当前call对应的json中的资源值，计算出cluster，添加到input中
            args = {**task_default_rescource, **json_task_rescouce_data}
            cluster = self.cluster(**args)
            self.input_processor.update_task_input(call_item.alias, 'cluster', cluster)
            return []
        
        # 存在资源字段
        # 2 资源字段都有默认值
        if not required_workflow_inputs and not required_json_inputs:
            # 此时只需要在call.input中增加cluster，并根据call的资源数据和task中的默认值计算出实际值
            # print("直接使用call中的数据计算出cluster", rescource_data, default_data)
            args = {**task_default_rescource, **json_task_rescouce_data}
            cluster = self.cluster(**args)
            # TODO： 支持修改call的input属性
            # call_item.up
            raise RuntimeError(f"{self.workflow_processor.fileWdl}@{self.workflow_processor.workflow_name} CALL[{call_item.alias}] 暂时不支持修改input值")
            return []

        # 需要额外的来源： 如cpu来源于json， mem来源于workflow.input
        # 3 仅需要json来源：call中不需要增加变量，json中增加cluster变量，根据call默认值+task默认值+json数据计算出实际值
        if not required_workflow_inputs:
            # print("call中有默认值，同时依赖json数据", rescource_data, default_data, task_default_rescource, json_task_rescouce_data)
            args = {**task_default_rescource, **default_data, **json_task_rescouce_data}
            cluster = self.cluster(**args)
            self.input_processor.update_task_input(call_item.alias, 'cluster', cluster)
            return []

        # 4 仅需要workflow.input： 此时需要根据task默认值+call默认值+workflow默认值+json_workflwo数据计算cluster
        if not required_json_inputs:

            # 4.1 若仅需要workflow默认值：在workflow中增加cluster， call中同样增加cluster
            if not json_workflow_rescource_data:
                # print("从workflow.input中提取资源值")
                # TODO: call中增加自定义input， workflow.input中增加自定义input
                raise RuntimeError(f"{self.workflow_processor.fileWdl}@{self.workflow_processor.workflow_name} 不支持自动修改call和workflow的input内容")
                # auto_add_cluster_key = f"cluster_{call_item.alias}"
                # # call_item.add_input('cluster', auto_add_cluster_key)
                # args = {**task_default_rescource, **default_data, **workflow_defalut_rescource_data}
                # cluster = self.cluster(**args)
                # self.workflow_processor.add_input(auto_add_cluster_key, 'String', f'"{cluster}"')
            # 4.2 workflow中的资源值同时来源于json中：此时直接根据各种数据计算出task的cluster值统一为task的cluster输入写入json中
            else:
                # print("资源值来源于workflow以及json")
                args = {**task_default_rescource, **default_data, **workflow_defalut_rescource_data, **json_workflow_rescource_data}
                cluster = self.cluster(**args)
                self.input_processor.update_task_input(call_item.alias, 'cluster', cluster)
            return []

        # 3.3 全都需要
        raise RuntimeError(f"{self.workflow_processor.fileWdl}@{self.workflow_processor.workflow_name} 可变资源来源过于复杂，暂不支持")

