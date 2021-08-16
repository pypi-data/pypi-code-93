import os
import subprocess

from .ph_ide_base import PhIDEBase, exception_file_not_exist


class PhIDEC9(PhIDEBase):
    """
    针对 C9 环境的执行策略
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.logger.debug('maxauto PhIDEC9 init')
        self.logger.debug(self.__dict__)

    def create(self, **kwargs):
        """
        c9 的创建过程
        """
        self.logger.debug('maxauto ide=c9 的 create 实现')
        self.logger.debug(self.__dict__)

        self.check_path(self.job_path)
        subprocess.call(["mkdir", "-p", self.job_path])

        # 创建 /phconf.yaml file
        input_str = [k.strip() for k in self.inputs.split(',')]
        input_str = ["- key: " + i + "\n        value: \"abc\"" for i in input_str]
        input_str = '\n      '.join(input_str)
        output_str = [k.strip() for k in self.outputs.split(',')]
        output_str = ["- key: " + i + "\n        value: \"abc\"" for i in output_str]
        output_str = '\n      '.join(output_str)
        self.table_driver_runtime_inst(self.runtime)(**self.__dict__).create_phconf_file(self.job_path, input_str=input_str, output_str=output_str, **self.__dict__)

        super().create()

    def complete(self, **kwargs):
        """
        c9 的补全过程
        """
        self.logger.debug('maxauto ide=c9 的 complete 实现')
        self.logger.debug(self.__dict__)
        self.logger.error('maxauto --ide=c9 时，不支持 complete 子命令')
        raise Exception("maxauto --ide=c9 时，不支持 complete 子命令")

    def dag_copy_job(self, **kwargs):
        """
        maxauto dag 时 copy c9 环境下生成的 job
        """
        self.logger.debug('maxauto ide=c9 的 dag_copy_job 实现')
        self.logger.debug(self.__dict__)

        job_name = kwargs['job_name'].replace('.', '_')
        job_full_path = self.project_path + self.job_prefix + kwargs['job_name'].replace('.', '/')

        if not os.path.exists(job_full_path):
            raise exception_file_not_exist

        subprocess.call(["cp", '-r', job_full_path, self.dag_path + job_name])
        self.table_driver_runtime_inst(self.runtime)(**self.__dict__).yaml2args(self.dag_path + job_name)
