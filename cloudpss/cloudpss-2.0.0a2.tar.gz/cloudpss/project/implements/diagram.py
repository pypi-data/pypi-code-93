from .component import Component
class DiagramImplement(object):
    """
        Diagram 实现
    """
    def __init__(self, diagram: dict = {}):
        """
            初始化
        """
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
        """
            类对象序列化为 dict
            :return: dict
        """
        cells = {}
        for key, val in self.cells.items():
            cells[key] = val.toJSON()
        diagram = {**self.__dict__, 'cells': cells}
        return diagram

    def getAllComponents(self):

        """
            获取所有元件

            :return: dict<Component>

        """

        return self.cells