import os
import re
import io
import json
import yaml
import gzip
from copy import deepcopy
from .revision import ProjectRevision
from .jobDefinitions import JOB_DEFINITIONS
from ..runner import Runner
from ..utils import request,fileLoad




class Project(object):
    """
        CloudPSS工程类，用于处理加载后的工程数据

        实例变量说明：

        rid         项目的 rid

        name         项目的名称

        description  项目的描述

        revision    当前项目的版本信息

        configs     当前项目的所有参数方案

        jobs        当前项目的所有计算方案

        context     当前项目的上下文相关信息

    """

    def __init__(self, project: dict = {}):
        """
            项目初始化
        """
        for k, v in project.items():
            if k == 'revision':
                self.__dict__[k] = ProjectRevision(v)
            else:
                self.__dict__[k] = v

    def __getitem__(self, attr):
        return super(Project, self).__getattribute__(attr)

    def toJSON(self):
        """
            类对象序列化为 dict
            :return: dict
        """
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

            :params str: 元件类型

            :type rid: str

            :return: 按照元件的 rid 过滤后的 dict<>

            >>> project.getComponentsByRid('project/CloudPSS/newInductorRouter')
            {
                'canvas_0_2': Component 实例
            }

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

    def getComponentByKey(self, componentKey: str):
        """
            通过元件的 key 获取对应的元件

            :params key: key 元件的key

            :Return: Component 实例

            >>> project.getComponentByKey('canvas_0_757')
            Component 实例
        """

        v = self.getAllComponents()
        return v[componentKey]

    def getProjectJob(self, name):
        """
            获取指定名称的计算方案

            :params Name: Name 参数名称

            :return: 同名计算方案数组

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

            :params jobType:  方案类型 
                电磁暂态仿真方案 emtp
                移频电磁暂态仿真方案 sfemt
                潮流计算方案 powerFlow

            :return: 返回一个指定类型的计算方案

            >>> project.createJob('emtp','emtp job')
            计算方案
        """
        job = deepcopy(JOB_DEFINITIONS[jobType])
        job['name'] = name
        return job

    def addJob(self, job: dict):
        """
            将计算方案添加到工程中

            :params job:  计算方案 dict

            >>> job = project.createJob('emtp','emtp job')
                project.addJob(job)
        """

        self.jobs.append(job)

    def getProjectConfig(self, name):
        """
            获取指定名称的参数方案

            :params name:  参数方案名称

            :return: 同名的方案数组

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
            :params name:  参数方案名称

            :return: 返回一个参数方案 dict

            >>> job = project.createConfig('my config')
                参数方案
        """

        config = deepcopy(self.configs[0])
        config['name'] = name
        return config

    def addConfig(self, config):
        """
            将参数方案添加到工程中

            :params config:  参数方案 dict

            >>> config = project.createConfig('my config')
                project.addConfig(config)
        """

        self.configs.append(config)
        return config

    @staticmethod
    def fetchMany(name=None, pageSize=10, pageOffset=0):
        """
            获取用户可以运行的项目列表

            :params name:  查询名称，模糊查询
            :params pageSize:  分页大小
            :params pageOffset:  分页开始位置

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

            :params rid:  项目 rid 

            :return: 返回一个项目实例

            >>> project=Project.fetch('project/Demo/test')

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

    def run(self, job=None, config=None, name=None, **kwargs):
        """

            调用仿真 

            :params job:  调用仿真时使用的计算方案，不指定将使用算例保存时选中的计算方案
            :params config:  调用仿真时使用的参数方案，不指定将使用算例保存时选中的参数方案
            :params name:  任务名称，为空时使用项目的参数方案名称和计算方案名称

            :return: 返回一个运行实例

            >>> runner=project.run(job,config,'')
            runner

        """
        if job is None:
            currentJob = self.context['currentJob']
            job = self.jobs[currentJob]
        if config is None:
            currentConfig = self.context['currentConfig']
            config = self.configs[currentConfig]

        return self.revision.run(job, config, name, self.rid, **kwargs)

    @staticmethod
    def load(filePath):
        """
            加载本地项目文件

            :params file:  文件目录

            :return: 返回一个项目实例

            >>> project = Project.load('filePath')

        """

        if not os.path.exists(filePath):
            raise FileNotFoundError('未找到文件')
        data = fileLoad(filePath)
        return Project(data)

    @staticmethod
    def dump(project, file):
        """
            下载项目文件

            :params project:  项目
            :params file:  文件路径

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
            
            :return: 保存成功/保存失败
            
            >>> project.save(project)
                project.save(project,'newKey') # 另存为新的项目

        """
        username = os.environ.get('USER_NAME')

        if key is not None:
            matchObj = re.match(r'^[-_A-Za-z0-9]+$', key, re.I | re.S)
            if matchObj:
                self.rid = 'project/'+username+'/'+key
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
            通过项目信息，获取当前项目对应的拓扑数据

            :params implementType:  实现类型
            :params config: config 项目参数, 不指定将使用算例保存时选中的参数方案
            :params maximumDepth:  最大递归深度，用于自定义项目中使用 diagram 实现元件展开情况

            :return:  一个拓扑实例

            >>> topology=project.fetchTopology() 
                topology=project.fetchTopology(implementType='powerFlow',config=config) # 获取潮流实现的拓扑数据
                topology=project.fetchTopology(maximumDepth=2) # 获取仅展开 2 层的拓扑数据
        """

        if self.revision is not None:
            if implementType is None:
                implementType = 'emtp'
            if config is None:
                currentConfig = self.context['currentConfig']
                config = self.configs[currentConfig]
            return self.revision.fetchTopology(implementType, config, maximumDepth)
        return None
