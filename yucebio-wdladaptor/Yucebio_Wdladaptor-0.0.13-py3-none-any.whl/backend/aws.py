import re
from yucebio_wdladaptor.backend.base import BaseAdaptor
from yucebio_wdladaptor.util.wdl_processor import _TaskItem
import yucebio_wdladaptor.util.wdl_v1_parser as WDL
import click


class Adaptor(BaseAdaptor):
    """转换WORKFLOW到亚马逊平台

    1. input：
        必须提供simg， 类型必须是String
    2. command
        需要将命令包裹到singularity内
    3. runtime
        设置固定的docker和disks， memory设置为带单位的字符串
    """
    PLATFORM = "AWS"
    COMMAND_PREFIX = "singularity exec -W /cromwell_root -B %s,/cromwell_root ~{simg}"
    SUPPORTED_RUNTIME_ATTRIBUTES = ['cpu', 'memory', 'disks', 'docker', 'continueOnReturnCode']

    def convert(self):
        call_tasks = self.workflow_processor.call_tasks

        for ns, import_item in self.workflow_processor.imports.items():
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

                # 检测各种资源值，将cpu和mem转换为字符串值
                self.convert_runtime(wdl_task_item)

    def convert_command(self, ti: _TaskItem):
        tab = ' ' * ti.processor.tab_size
        command_prefix = self.COMMAND_PREFIX % self.bind_path

        new_command_contents = "\n".join([
            f"{tab}{tab}{command_prefix} bash -s <<'ENDOFCMD'",
            *[f"{tab}{tab}{tab}{line}" for line in ti.command_content_lines],
            f"{tab}{tab}ENDOFCMD"
        ])
        ti.update_command(new_command_contents)

    def convert_runtime(self, ti: _TaskItem):
        """检测cpu和memory是否为常量，若为常量，将它修改为字符串，若为变量，需要在后面拼接一个"G"

        docker, disks, cpu, memory
        亚马逊通过queueArn管理实例，作业集群默认设置了竞价或按需模式
        """
        # 1. 增加docker
        if 'docker' in ti.runtime and ti.runtime['docker'].strip("\"'") != "kongdeju/singularity:2.6.1":
            raise RuntimeError(f"{ti.processor.fileWdl}@{ti.name} 不允许自定义docker")
        # runtime_kvs['docker'] = 'docker: "kongdeju/singularity:2.6.1"'
        ti.update_runtime("docker", '"kongdeju/singularity:2.6.1"')

        # 2. 配置disk
        ti.update_runtime("disks", '"/efs 100 SSD"')

        if 'memory' not in ti.runtime:
            return

        # 3. memory修改为带单位的字符串
        input_key_mem = ti.runtime['memory']
        # 若runtime中有默认值：修改为字符串
        if input_key_mem not in ti.inputs:
            ti.update_runtime("memory", f'"{input_key_mem}G"')
        else:
            ti.update_runtime("memory", f'{input_key_mem} + "G"')

        # 移除不支持的RUNTIME属性
        self.filter_or_append_runtime_attributes(ti)
