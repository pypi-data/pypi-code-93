"""
注解类,用于表名Taskhandler的注解的,TODO 这里肯定是错的
"""

TASK_HANDLERS = dict()


def TaskHandler(name):
    """
    TaskHandler的类注解
    :param name:
    :return:
    """

    def decorate(cls):
        TASK_HANDLERS[name] = cls()
        return cls      # 让装饰器最后还是返回cls. 否则经过装饰器包装的类的返回时None

    return decorate
