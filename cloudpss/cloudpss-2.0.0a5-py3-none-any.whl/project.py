# coding=UTF-8
import sys
import os
import re
import io
import json
from .jobDefinitions import JOB_DEFINITIONS
from copy import deepcopy
from .runner import Runner
from .httprequests import request
import yaml
import gzip
from .yamlLoader import fileLoad


class ProjectTopology():
    def __init__(self, topology: dict = {}):
        self.__dict__.update(topology)

    def toJSON(self):
        data = {**self.__dict__}

        return data

    @staticmethod
    def dump(topology, filePath, indent=None):
        """
            保存拓扑文件

            :params: topology 拓扑实例
            :params: file 文件路径
        """
        data = topology.toJSON()
        f = open(filePath, 'w', encoding='utf-8')
        json.dump(data, f, indent=indent)
        f.close()

    @staticmethod
    def fetch(hash, implementType, config, maximumDepth):
        """
            获取拓扑

            :params: hash 
            :params: implementType 实现类型
            :params: config 参数方案

            : return: 拓扑实例

            >>> data = ProjectTopology.fetch('','emtp',{})

        """

        args = {} if config is not None else config['args']
        query = """
            query t($hash:String,$args: JSONObject!,$implementType:String,$maximumDepth:Int) {
                    
                topology(hash:$hash,args: $args,implementType:$implementType,maximumDepth:$maximumDepth) {
                    components
                    mappings
                }
            }
        """
        payload = {
            'query': query,
            'variables': {
                'hash': hash,
                'args': args,
                'implementType': implementType,
                'maximumDepth': maximumDepth
            }
        }
        r = request('POST', 'graphql', data=json.dumps(payload))
        data = json.loads(r.text)
        return ProjectTopology(data['data']['topology'])


class Component(object):
    def __init__(self, diagram: dict = {}):
        self.__dict__.update(diagram)

    def __getitem__(self, attr):
        return super(Component, self).__getattribute__(attr)

    def toJSON(self):
        cells = {**self.__dict__}

        return cells


class DiagramImplement(object):
    def __init__(self, diagram: dict = {}):
        # self.__dict__.update(diagram)
        for k, v in diagram.items():
            if k == 'cells':
                self.__dict__[k] = v
                for key, val in v.items():
                    v[key] = Component(val)
            else:
                self.__dict__[k] = v

    def __getitem__(self, attr):
        return super(DiagramImplement, self).__getattribute__(attr)

    def toJSON(self):
        cells = {}
        for key, val in self.cells.items():
            cells[key] = val.toJSON()
        diagram = {**self.__dict__, 'cells': cells}
        return diagram

    def getAllComponents(self):
        return self.cells


class ProjectImplement(object):
    def __init__(self, implements: dict = {}):
        for k, v in implements.items():
            if k == 'diagram':
                self.__dict__[k] = DiagramImplement(v)
            else:
                self.__dict__[k] = v

    def __getitem__(self, attr):
        return super(ProjectImplement, self).__getattribute__(attr)

    def toJSON(self):
        implements = {**self.__dict__, 'diagram': self.diagram.toJSON()}
        return implements

    def getDiagram(self):
        return getattr(self, 'diagram', None)


class ProjectRevision(object):
    def __init__(self, revision: dict = {}):
        for k, v in revision.items():
            if k == 'implements':
                self.__dict__[k] = ProjectImplement(v)
            else:
                self.__dict__[k] = v

    def __getitem__(self, attr):
        return super(ProjectRevision, self).__getattribute__(attr)

    def toJSON(self):
        revision = {**self.__dict__, 'implements': self.implements.toJSON()}
        return revision

    def getImplements(self):
        return self.implements

    def run(self, taskId, job, config, name=None, rid='', **kwargs):
        """
            运行某个指定版本的项目

            :params: taskId taskId 任务id，运行中的任务id唯一，
            :params: revision 项目版本号
            :params: job 调用仿真时使用的计算方案，为空时使用项目的第一个计算方案
            :params: config 调用仿真时使用的参数方案，为空时使用项目的第一个参数方案
            :params: name 任务名称，为空时使用项目的参数方案名称和计算方案名称
            :params: rid 项目rid，可为空

            :return: 返回一个运行实例

            >>> revision.run(revision,job,config,'')
            runner
        """

        revision = ProjectRevision.create(self, self.hash)
        return Runner.create(taskId, revision['hash'], job, config, name, rid, **kwargs)

    @staticmethod
    def create(revision, parentHash=None):
        """
            保存一个项目版本

            :params: revision 版本数据

            :return: 项目版本hash

            >>> ProjectRevision.create(project.revision)
            {hash:'4043acbddb9ce0c6174be65573c0380415bc48186c74a459f88865313743230c'}
        """

        if parentHash:
            revision.parentHash = parentHash
        query = """
            mutation t($parameters:[JSONObject!]!,$graphic:JSONObject!,$pins:[JSONObject!]!,$implements:ProjectImplementInputDto!,$implementType:JSONObject!,$documentation:String!,$parentHash:String){
                addRevision( revision:{author:"CloudPSS",parameters:$parameters,committer: "CloudPSS" ,message:"add",graphic:$graphic,implements:$implements,pins:$pins,documentation:$documentation,implementType:$implementType,parentHash:$parentHash}) {
                    hash  
                }
        }"""
        implementType = {}
        payload = {
            'query': query,
            'variables': {
                **revision.toJSON(),
                'parentHash': parentHash,
                'implementType': implementType

            }
        }
        r = request('POST', 'graphql', data=json.dumps(payload))
        r = json.loads(r.text)
        return r['data']['addRevision']

    def fetchTopology(self, implementType, config, maximumDepth):
        """
            获取项目拓扑

            :params: implementType 实现类型
            :params: config 项目参数

            :return: 保存成功/保存失败

            >>> topology=project.fetchTopology(project)
            保存成功
        """

        if self.hash is not None:
            return ProjectTopology.fetch(self.hash, implementType, config, maximumDepth)
        return None


class Project(object):
    """CloudPSS工程类,用于处理加载后的工程数据"""

    def __init__(self, project: dict = {}):
        for k, v in project.items():
            if k == 'revision':
                self.__dict__[k] = ProjectRevision(v)
            else:
                self.__dict__[k] = v

    def __getitem__(self, attr):
        return super(Project, self).__getattribute__(attr)

    def toJSON(self):
        project = {**self.__dict__, 'revision': self.revision.toJSON()}
        return project

    def getAllComponents(self):
        """
            获取实现

            :return: 所有元件信息

            >>> project.getAllComponents()
            {
                'canvas_0_2': Component 实例
            }
        """
        diagramImplement = self.revision.getImplements().getDiagram()
        if diagramImplement is None:
            raise ValueError('不存在拓扑实现')
        return diagramImplement.getAllComponents()

    def getComponentsByRid(self, rid: str):
        """
            通过指定元件类型获取元件

            :params: classname 元件类型

            :return: 元件信息

            >>> project.getComponentsByRid('project/CloudPSS/newInductorRouter')
            {...}

        """

        v = self.getAllComponents()

        cells = {}
        for key, val in v.items():

            if val.shape.endswith('edge'):
                continue
            if val.shape != 'diagram-component':
                continue
            if val.definition == rid:
                cells[key] = val
        return cells

    def getComponentsByKey(self, componentKey: str):
        """
            通过元件的 key 获取对应的元件

            :params: key 元件的key

            >>> project.getComponentsByKey('canvas_0_757')
        """

        v = self.getAllComponents()
        return v[componentKey]

    def getProjectJob(self, name):
        """
            获取指定名称的计算方案

            :params: Name 参数名称

            :return: 同名

            >>> project.getProjectJob('电磁暂态方案 1')
        """
        jobs = []

        for val in self.jobs:
            if val['name'] == name:
                jobs.append(val)

        return jobs

    def createJob(self, jobType: str, name):
        """
            创建一个计算方案
            创建出的方案默认不加入到项目中，需要加入请调用 addJob

            :params: jobType 方案类型 
                电磁暂态仿真方案 emtp
                移频电磁暂态仿真方案 emtp
                潮流计算方案 emtp

            :return: 返回一个指定类型的计算方案
        """
        job = deepcopy(JOB_DEFINITIONS[jobType])
        job['name'] = name
        return job

    def addJob(self, job: dict):
        """
            将计算方案添加到工程中

            :params: job 计算方案 dict
        """

        self.jobs.append(job)

    def getProjectConfig(self, name):
        """
            获取指定名称的参数方案

            :params: name 参数方案名称

            :return: 无

            >>> project.getProjectConfig('参数方案 1')
        """
        configs = []

        for val in self.configs:
            if val['name'] == name:
                configs.append(val)

        return configs

    def createConfig(self, name):
        """
            创建一个参数方案
            根据项目的第一个参数方案生成一个方案
            创建出的方案默认不加入到项目中，需要加入请调用 addConfig
            :params: name 参数方案名称

            :return: 返回一个参数方案 dict
        """

        config = deepcopy(self.configs[0])
        config['name'] = name
        return config

    def addConfig(self, config):
        """
            将参数方案添加到工程中

            :params: config 参数方案 dict
        """

        self.configs.append(config)
        return config

    @staticmethod
    def fetchMany(name=None, pageSize=10, pageOffset=0):
        """
            获取用户可以运行的项目列表

            :params: name 查询名称，模糊查询
            :params: pageSize 分页大小
            :params: pageOffset 分页开始位置
            :return: 按分页信息返回项目列表

            >>> data=Project.fetchMany()
            [
                {'rid': 'project/admin/share-test', 'name': '1234', 'description': '1234'}
                ...
            ]
        """

        r = request('GET', 'api/resources/type/project/permission/read',
                    params={'page_offset': pageOffset, 'page_size': pageSize, 'search': name})
        projectList = json.loads(r.text)

        return [{'rid': '/'.join([val['type'], val['owner'], val['key']]), 'name':val['name'], 'description':val['description']} for val in projectList]

    @staticmethod
    def fetch(rid):
        """
            获取项目

            :params: rid 项目rid 

            :return: 返回一个项目实例

            >>> project=Project.fetch('project/admin/share-test')

        """
        query = """
            query  t($rid:String!){
                project(rid: $rid) {
                    rid
                    name
                    revisionHash
                    jobs
                    configs
                    context
                    tags
                    description
                    revision {
                        hash
                        graphic
                        documentation
                        author
                        committer
                        implements {
                            diagram
                        }
                        message
                        parameters
                        pins
                    }
                }
            }
        """
        payload = {
            'query': query,
            'variables': {
                'rid': rid
            }
        }
        r = request('POST', 'graphql', data=json.dumps(payload))

        data = json.loads(r.text)

        if data['data'] is None:

            raise Exception(data['errors'][0]['message'])

        return Project(data['data']['project'])

    def run(self, taskId, job=None, config=None, name=None, **kwargs):
        """

            调用仿真 

            :params: taskId 任务id，运行中的任务id唯一，
            :params: project 项目
            :params: job 调用仿真时使用的计算方案，为空时使用项目的第一个计算方案
            :params: config 调用仿真时使用的参数方案，为空时使用项目的第一个参数方案
            :params: name 任务名称，为空时使用项目的参数方案名称和计算方案名称

            :return: 返回一个运行实例

            >>> runner=project.run(taskId,project,job,config,'')
            runner

        """
        if job is None:
            job = self.jobs[0]
        if config is None:
            config = self.configs[0]

        return self.revision.run(taskId, job, config, name, self.rid, **kwargs)

    @staticmethod
    def load(file):
        """
            加载本地项目文件

            :params: file 文件目录

            :return: 返回一个项目实例

            >>> project = Project.load('E:\project\cloudpss\cloudpss-sdk\python\simulation\\aaa\\3845.cproj')
            <sdk.project.Project object at 0x0E75A0B0>
        """

        if not os.path.exists(file):
            raise FileNotFoundError('未找到文件')
        data = fileLoad(file)
        return Project(data)

    @staticmethod
    def dump(project, file):
        """
            下载项目文件

            :params: project 项目
            :params: file 文件路径

            :return: 无

            >>> Project.dump(project,file)
        """

        data = project.toJSON()

        yamlData = yaml.dump(data)
        with gzip.open(file, 'w') as output:
            with io.TextIOWrapper(output, encoding='utf-8') as enc:
                enc.write(yamlData)

    def save(self, key=None):
        """
            保存/创建项目 

            key 不为空时如果远程存在相同的资源名称时将覆盖远程项目。
            key 为空时如果项目 rid 不存在则抛异常，需要重新设置 key。
            如果保存时，当前用户不是该项目的拥有者时，将重新创建项目，重建项目时如果参数的 key 为空将使用当前当前项目的 key 作为资源的 key ，当资源的 key 和远程冲突时保存失败


            :params: project 项目
            :params: key 资源 id 的唯一标识符，



            >>> project.save(project)
            保存成功

        """
        username = os.environ.get('USER_NAME')

        if key is not None:
            matchObj = re.match(r'^[-_A-Za-z0-9]+$', key, re.I | re.S)
            if matchObj:
                self.rid = 'project/'+username+'/'+key
                # Project.create(self)
                try:
                    r = request('GET', 'resources/' + self.rid)
                    return Project.update(self)
                except:
                    return Project.create(self)
            else:
                raise Exception('key 能包含字母数子和下划线')
        else:
            t = '(?<=/)\\S+(?=/)'
            owner = re.search(t, self.rid)
            if owner is None:
                raise Exception('rid 错误，请传入 key')
            elif owner[0] != username:
                rid = re.sub(t, username, self.rid)
                try:
                    r = request('GET', 'resources/' + self.rid)
                    return Project.create(self)
                except:
                    raise Exception(rid+' 该资源已存在，无法重复创建,请修改 key')

        return Project.update(self)

    @staticmethod
    def create(project):
        """
            新建项目 

            :params: project 项目

            :return: 保存成功/保存失败

            >>> Project.create(project)
            保存成功
        """
        Project.update(project)

    @staticmethod
    def update(project):
        """
            更新项目 

            :params: project 项目

            :return: 保存成功/保存失败

            >>> Project.update(project)
            保存成功
        """

        t = '(?<=/)\\S+(?=/)'
        username = os.environ.get('USER_NAME')
        owner = re.search(t, project.rid)

        if owner is None:
            raise Exception('rid 错误，无法保存')
        elif owner[0] != username:
            raise Exception('rid 错误，无法保存')
        revision = ProjectRevision.create(
            project.revision, project.revision.hash)
        projectQuery = """
            mutation t(
                $rid: String!,
                $revisionHash: String!,
                $context: JSONObject,
                $configs: [JSONObject!]!,
                $jobs: [JSONObject!]!,
                $info:ProjectInfoInput!
            ){
                addProject( project:{rid: $rid,revisionHash:$revisionHash,configs:$configs,context:$context,jobs:$jobs},info:$info) {
                    rid  
                }
            }
        """
        isPublic = project.context.get('auth', '') != 'private'
        isComponent = project.context.get('category', '') == 'component'
        publicRead = project.context.get('publicRead', '') != False
        auth = {
            'read': isPublic and (publicRead if isComponent else True),
            'execute': isPublic,
        }
        payload = {
            'query': projectQuery,
            'variables': {
                'rid': project.rid,
                'revisionHash': revision['hash'],
                'context': project.context,
                'configs': project.configs,
                'jobs': project.jobs,
                'info': {
                    'name': project.name,
                    'description': project.description,
                    'tags': project.tags,
                    'auth': auth,
                },
            }
        }
        r = request('POST', 'graphql', data=json.dumps(payload))
        r = json.loads(r.text)
        return r

    def fetchTopology(self, implementType=None, config=None, maximumDepth=None,):
        """
            获取项目拓扑

            :params: implementType 实现类型
            :params: config 项目参数

            :return: 保存成功/保存失败

            >>> topology=project.fetchTopology(project)
            保存成功
        """

        if self.revision is not None:
            if implementType is None:
                implementType = 'emtp'
            if config is None:
                config = self.configs[0]
            return self.revision.fetchTopology(implementType, config, maximumDepth)
        return None
