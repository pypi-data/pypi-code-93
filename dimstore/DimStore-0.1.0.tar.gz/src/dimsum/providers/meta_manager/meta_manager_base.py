"""
    base class of meta manager class
"""


class MetaManagerBase():

    def __init__(self, config):
        pass

    def get_valid_operations(self, feature):
        raise NotImplementedError('Meta Manager valid_operations method implementation error!')

    def register(self, feature):
        raise NotImplementedError('Meta Manager register method implementation error!')

    def read(self, namespace='default', match_child=True, **kwargs):
        raise NotImplementedError('Meta Manager read method implementation error!')

    def namespaces(self, **kwargs):
        raise NotImplementedError('Meta Manager namespace method implementation error!')

    def delete(self, ufd, verbose=True, **kwargs):
        raise NotImplementedError('Meta Manager delete method implementation error!')
    
    def update(self, ufd, verbose=True, **kwargs):
        raise NotImplementedError('Meta Manager update method implementation error!')