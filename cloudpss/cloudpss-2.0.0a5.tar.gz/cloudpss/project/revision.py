

import json
from .topology import ProjectTopology 
from .implements import ProjectImplement
from ..utils import request
from ..runner import Runner
class ProjectRevision(object):
    """
        表示一个项目的版本数据

        实例变量说明：

        implements          项目当前版本的实现数据

        parameters          项目当前版本的参数结果

        pins                项目当前版本的引脚信息

        documentation       项目当前版本的文档信息



    """
    def __init__(self, revision: dict = {}):
        """
            初始化
        """
        for k, v in revision.items():
            if k == 'implements':
                self.__dict__[k] = ProjectImplement(v)
            else:
                self.__dict__[k] = v

    def __getitem__(self, attr):
        return super(ProjectRevision, self).__getattribute__(attr)

    def toJSON(self):

        """
            类对象序列化为 dict
            :return: dict
        """

        revision = {**self.__dict__, 'implements': self.implements.toJSON()}
        return revision

    def getImplements(self):
        """
            获取当前版本的实现

            :return: 实现实例

            >>> revision.getImplements()
        """

        return self.implements

    def run(self,job, config, name=None, rid='', **kwargs):
        """
            运行某个指定版本的项目

            :params job:  调用仿真时使用的计算方案，为空时使用项目的第一个计算方案
            :params config:  调用仿真时使用的参数方案，为空时使用项目的第一个参数方案
            :params name:  任务名称，为空时使用项目的参数方案名称和计算方案名称
            :params rid:  项目rid，可为空

            :return: 返回一个运行实例

            >>> revision.run(revision,job,config,'')
        """
        
        revision = ProjectRevision.create(self, self.hash)
        return Runner.create( revision['hash'], job, config, name, rid, **kwargs)

    @staticmethod
    def create(revision, parentHash=None):
        """
            创建一个新版本

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
            获取当前项目版本的拓扑数据

            :params implementType:  实现类型
            :params config:  项目参数
            :params maximumDepth:  最大递归深度，用于自定义项目中使用 diagram 实现元件展开情况

            :return:  一个拓扑实例

            >>> topology=revision.fetchTopology()
                topology=revision.fetchTopology(implementType='powerFlow',config=config) # 获取潮流实现的拓扑数据
                topology=revision.fetchTopology(maximumDepth=2) # 获取仅展开 2 层的拓扑数据

        """

        if self.hash is not None:
            return ProjectTopology.fetch(self.hash, implementType, config, maximumDepth)
        return None

