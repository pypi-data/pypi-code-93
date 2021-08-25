from net_models.utils.get_logger import get_logger


class BaseFilter(object):

    def __init__(self):
        self.logger = get_logger(name="NetTemplates-Filter")

    def filters(self):
        filters = {}
        for name, method in self.__class__.__dict__.items():
            if not name.startswith("_") and callable(method):
                filters[name] = getattr(self, name)
        # del filters["filters"]
        return filters