class AlgoOutWrapper:
    t = None            #这两个对象名字是为了兼容java的ficus那边
    subPath: str = None

    def __init__(self, content, sub_path: str):
        self.t = content
        self.subPath = sub_path

    def content(self):
        return self.t

    def sub_path(self):
        return self.subPath


def WITH(content, sub_path: str):
    """
    封装输出操作，一般是放在OutPutPipe里面使用，如output_stream.output_for_insert(AlgoOutWrapper.WITH('need_insert_data', 'sub_path'))
    :param content: 被操作的内容
    :param sub_path: 子文件，即往outputFd所定义的文件夹下面的子文件里面写数据
    :return: AlgoOutWrapper的dict对象，是为了兼容java的ficus，因为那边接收的是json
    """
    wrapper = AlgoOutWrapper(content, sub_path)
    return wrapper.__dict__
