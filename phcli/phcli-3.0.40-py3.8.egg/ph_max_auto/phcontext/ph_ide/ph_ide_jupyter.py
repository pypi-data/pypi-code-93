import os
from .ph_ide_base import PhIDEBase, PhCompleteStrategy


class PhIDEJupyter(PhIDEBase):
    """
    针对 Jupyter 环境的执行策略
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.logger.debug('maxauto PhIDEJupyter init')
        self.logger.debug(self.__dict__)

    def create(self, **kwargs):
        """
        jupyter 的创建过程
        """
        self.logger.debug('maxauto ide=jupyter 的 create 实现')
        self.logger.debug(self.__dict__)

        self.check_path(self.job_path)

        super().create()

    def complete(self, **kwargs):
        """
        jupyter 的补全过程
        """
        self.logger.debug('maxauto ide=jupyter 的 complete 实现')
        self.logger.debug(self.__dict__)

        def single_complete(job_path, exts):
            require_cs = self.choice_complete_strategy(job_path + ".ipynb", job_path)
            if self.strategy == "s2c":
                actual_cs = PhCompleteStrategy.S2C
            elif self.strategy == 'c2s':
                actual_cs = PhCompleteStrategy.C2S
            else:
                actual_cs = require_cs

            if require_cs != actual_cs:
                self.logger.warn("actual [" + str(actual_cs) + "] != require [" + str(require_cs) + "], in " + job_path)

            if actual_cs == PhCompleteStrategy.S2C:
                self.logger.info("S2C: " + job_path)
                runtime_inst = self.table_driver_runtime_inst(self.runtime)(**self.__dict__)
                if not os.path.exists(job_path + ".ipynb"):
                    self.logger.warn("source path is not exists: " + job_path + ".ipynb")
                    return
                runtime_inst.jupyter_to_c9(job_path + ".ipynb", job_path, exts)
            elif actual_cs == PhCompleteStrategy.C2S:
                self.logger.info("C2S: " + job_path)
                runtime_inst = self.table_driver_runtime_inst(self.runtime)(**self.__dict__)
                if not os.path.exists(job_path):
                    self.logger.warn("source path is not exists: " + job_path)
                    return
                runtime_inst.c9_to_jupyter(job_path, job_path + ".ipynb", exts)
            else:
                self.logger.info("KEEP COMPLETE: " + job_path)

        def recursive_complete_path(path):
            def get_group_job_by_path(path):
                if path.endswith('.ipynb'):
                    tmp = path.split("phjobs/")[-1].split("/")
                    group = tmp[0] if len(tmp) == 2 else 'null'
                    job = tmp[-1].split('.')[0]
                else:
                    tmp = path.split("phjobs/")[-1].split("/")[:-1]
                    group = tmp[0] if len(tmp) == 2 else 'null'
                    job = tmp[-1]
                return group, job

            result = {}
            for root, dirs, files in os.walk(path):
                for file in files:
                    group, job = get_group_job_by_path(os.path.join(root, file))
                    if group in result:
                        jobs = result[group]
                        if job not in jobs:
                            jobs.append(job)
                    else:
                        jobs = [job]
                    result[group] = jobs
            return result

        if self.group == "ALL":
            recursive_path = self.get_workspace_dir() + '/' + self.get_current_project_dir() + self.job_prefix
            gj_map = recursive_complete_path(recursive_path)
        elif self.name == "ALL":
            recursive_path = self.get_workspace_dir() + '/' + self.get_current_project_dir() + self.job_prefix + self.group
            gj_map = recursive_complete_path(recursive_path)
        else:
            group = self.group if self.group else 'null'
            gj_map = {group: [self.name]}

        for group in gj_map:
            for job in gj_map[group]:
                project_path = self.get_workspace_dir() + '/' + self.get_current_project_dir()
                job_path = project_path + self.job_prefix + (group + '/' if group != 'null' else '') + job
                single_complete(job_path, {"group": (group if group != 'null' else ''), "ide": self.ide})
