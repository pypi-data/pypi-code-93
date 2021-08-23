import copy
import re
from .storage import Storage


class Result(object):
    """
        结果处理类，从消息存储库中获取数据，并进行简单的整理

        可迭代器，迭代时按接收顺序返回数据

        >>> for data in result:
                print(data)

        也可以从类的 db 变量，获取数据存储类实例进行操作
    """

    def __init__(self, db):
        """
            初始化
        """
        self.n = 0
        self.db = db
        self.__logsIndex = 0

    @classmethod
    def load(cls, filePath):
        """
            加载本地结果文件

            :params: file 文件目录

            :return: 返回一个结果实例

            >>> result = Result.load('C:\\Users\\dps-dm\\cloudpss-sdk\\result\\424111.cjob')

        """
        db = Storage.load(filePath)

        return cls(db)

    @staticmethod
    def dump(result, file):
        '''
            保存结果到本地文件

            :params: file 保存文件的目录

            >>> Result.dump(file)
            {...}
        '''

        Storage.dump(result.db, file)

    def __iter__(self):
        return self

    def __next__(self):
        maxLength = self.db.getMessageLength()
        if self.n < maxLength:
            message = self.db.getMessage(self.n)
            self.n += 1
            return message
        raise StopIteration()

    def getLogs(self):
        '''
            获取当前任务的日志

            >>>logs= result.getLogs()
            {...}
        '''
        result = []
        length = self.db.getMessageLength()
        if(length > self.__logsIndex):
            for num in range(self.__logsIndex, length):
                val = self.db.getMessage(num)
                if val['type'] == 'log':
                    result.append(val)
            self.__logsIndex = length
        return result

    def __deepModify(self, dict1, dict2):

        for key, val in dict1.items():
            if type(val) is dict:
                self.__deepModify(val, dict2[key])
            else:
                dict2[key] = val

    def getMessagesByType(self, type):
        """
            获取指定类型的消息数据

             >>> message= result.getMessagesByType('log')
        """

        return self.db.getMessagesByType(type)


class EMTResult(Result):
    """
        电磁暂态结果处理类，继承 Result， 

        提供快捷 plot 数据的接口函数，获取到的 plot 数据为合并后的数据格式，不在是接收时分段的数据

        该类只提供 EMT 仿真使用

    """

    def __init__(self, *args, **kwargs):
        """
            初始化
        """
        Result.__init__(self, *args, **kwargs)
        self.result = {}
        self.__plotIndex = 0

    def getPlots(self):
        '''
            获取所有的 plots 数据

            >>> result.getPlots()
            {...}
        '''

        length = self.db.getMessageLength()
        if(length > self.__plotIndex):
            for num in range(self.__plotIndex, length):
                val = self.db.getMessage(num)
                if val['type'] == 'plot':
                    key = val['key']
                    if self.result.get(key, None) is None:
                        self.result[key] = copy.deepcopy(val)
                    else:
                        traces = val['data']['traces']
                        for i in range(len(traces)):
                            v = traces[i]
                            self.result[key]['data']['traces'][i]['x'].extend(
                                v['x'])
                            self.result[key]['data']['traces'][i]['y'].extend(
                                v['y'])
            self.__plotIndex = length
        return self.result.values()

    def getPlot(self, index: int):
        '''
            获取指定序号的数据分组

            :params: index 图表位置

            >>> result.getPlot(0)
            {...}
        '''
        self.getPlots()
        if self.result is not None:
            return self.result.get('plot-{0}'.format(int(index)), None)

    def getPlotChannelNames(self, index):
        '''
            获取一组输出分组下的所有通道名称

            :params: index 输出通道位置

            :return: 通道名称数组

            >>>names= result.getPlotChannelNames(0)
            []
        '''
        plot = self.getPlot(int(index))
        if plot is None:
            return None

        return [val['name'] for val in plot['data']['traces']]

    def getPlotChannelData(self, index, channelName):
        '''
            获取一组输出分组下指定通道名称的数据

            :params: index 输出通道位置
            :params: channelName 输出通道名称

            :return: 通道数据, 一个 trace 数据

            >>>channel= result.getPlotChannelData(0，'')
            {...}
        '''
        plot = self.getPlot(int(index))
        if plot is None:
            return None
        for val in plot['data']['traces']:
            if val['name'] == channelName:
                return val
        return val


class PowerFlowResult(Result):
    """
        潮流结果处理类，继承 Result， 

        提供快速获取 buses 和 branches 的接口，并提供潮流写入项目的接口

        该类只提供潮流仿真时使用

    """

    def __init__(self, *args, **kwargs):
        """
            初始化
        """
        Result.__init__(self, *args, **kwargs)

    def getBuses(self):
        """
            获取潮流结果 buses 数据

            >>> channel= result.getBuses()
            [...]
        """

        result = []
        pattern = re.compile("value=\"(.*)\"")
        data = self.db.getMessagesByType('buses-table')
        table = copy.deepcopy(data)
        columns = table['data']['columns']
        for column in columns:
            if column['type'] == 'html':
                data = column['data']
                for i in range(len(data)):
                    if data[i] != '':
                        s = pattern.findall(data[i])
                        data[i] = s[0].replace('/', '')

        result.append(table)
        return result

    def getBranches(self):
        """
            获取潮流结果 branches 数据

            >>> channel= result.getBranches()
            [...]
        """

        result = []
        pattern = re.compile("value=\"(.*)\"")
        data = self.db.getMessagesByType('branches-table')
        table = copy.deepcopy(data)

        columns = table['data']['columns']
        for column in columns:
            if column['type'] == 'html':
                data = column['data']
                for i in range(len(data)):
                    if data[i] != '':
                        s = pattern.findall(data[i])
                        data[i] = s[0].replace('/', '')

        result.append(table)
        return result

    def powerFlowModify(self, project):
        """
            潮流数据写入 project

            >>> channel= result.powerFlowModify(project)
        """

        data = self.db.getMessagesByType('power-flow-modify')

        modifyData = data['data']
        payload = modifyData['payload']
        self.__deepModify(payload, project)
