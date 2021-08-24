# -*- coding:utf-8 -*-
#
# Copyright (C) 2019-2020 Alibaba Group Holding Limited


from __future__ import print_function

import threadpool
from yoctools import *


class Install(Command):
    common = True
    helpSummary = "Install component into project environment"
    helpUsage = """
%prog [option] [<component>...]
"""
    helpDescription = """
Install component into project environment
"""

    def _Options(self, p):
        self.jobs = 1
        p.add_option('-j', '--jobs',
                     dest='jobs', action='store', type='int',
                     help="projects to fetch simultaneously (default %d)" % self.jobs)
        # p.add_option('-f', '--force',
        #              dest='force', action='store_true',
        #              help='install component force if exist already')
        p.add_option('-b', '--branch',
                     dest='branch', action='store', type='string',
                     help='the branch for component to download')
        p.add_option('-s', '--single',
                     dest='single', action='store_true',
                     help='just install one component, exclude its\' dependent components')

    def Execute(self, opt, args):
        if opt.jobs:
            jobs = opt.jobs
        else:
            jobs = 4
        put_string("Start to install components...")
        yoc = YoC()
        components = ComponentGroup()
        if len(args) > 0:
            for name in args:
                update = False
                if name == args[0]:
                    update = True
                cmpt = yoc.check_cmpt_download(name, update=True)
                if cmpt:
                    components.add(cmpt)
        else:
            yoc.update()
            components = yoc.occ_components
        
        exe_dld_cmpt_list = ComponentGroup()
        if len(components) > 0:
            dled_cmpts = []
            dep_list = {}
            vercheck_list = {}
            while len(components) > 0:
                cmpts = components
                self.download(jobs, cmpts, opt.branch)
                if opt.single:
                    exe_dld_cmpt_list = components
                    break
                for c in cmpts:
                    if c.name not in dled_cmpts:
                        dled_cmpts.append(c.name)
                components = ComponentGroup()
                for c in cmpts:
                    exe_dld_cmpt_list.add(c)
                    ret = c.load_package()
                    if ret:
                        yoc.update_version(c.depends) # 更新需要下载的组件的版本号，从父组件的depends字段下的版本号来
                        cmpt_list = self.get_need_download_cmpts(args, dled_cmpts, c, dep_list, vercheck_list)
                        for component in yoc.occ_components:
                            if component.name in cmpt_list:
                                components.add(component)
            # check different version
            self.show_vercheck_list(vercheck_list)
            # check file
            for c in exe_dld_cmpt_list:
                if not c.check_file_integrity():
                    put_string("Component:%s maybe not fetch integrallty(miss `README.md` or `package.yaml`), Please check the branch is right." % c.name, level='warning')
            put_string('Download components finish.')
        else:
            put_string("No component need to install.")

    def get_need_download_cmpts(self, origin_list, downloaded_list, component, dep_list={}, vercheck_list={}):
        cmpt_list = []
        for name in component.depends:
            if type(name) == dict:
                version = list(name.values())[0]
                name = list(name.keys())[0]
                if (name not in origin_list) and (name not in downloaded_list):
                    cmpt_list.append(name)
                ##################################check_depend_version
                for k, v in dep_list.items():
                    son = k.split(':')[0]
                    ver = k.split(':')[1]
                    if son == name and ver != version:
                        vercheck_list["%s:%s" % (name, version)] = {"father":component.name}
                        vercheck_list[k] = v
                key = "%s:%s" % (name, version)
                if key not in dep_list:
                    dep_list[key] = {"father":component.name}
                ##################################
        return cmpt_list

    def show_vercheck_list(self, vercheck_list):
        for k in sorted(vercheck_list):
            son = k.split(':')[0]
            ver = k.split(':')[1]
            father = vercheck_list[k]["father"]
            put_string("version_check: %s: %s in %s's depends." % (son, ver, father), level='warning')

    def download(self, jobs, components, branch):
        task_pool = threadpool.ThreadPool(jobs)
        tasks = []
        for component in components:
            tasks.append(component)

        def thread_execture(component):
            component.download(branch)

        requests = threadpool.makeRequests(thread_execture, tasks)
        for req in requests:
            task_pool.putRequest(req)
        task_pool.wait()
        task_pool.dismissWorkers(jobs, do_join=True)
