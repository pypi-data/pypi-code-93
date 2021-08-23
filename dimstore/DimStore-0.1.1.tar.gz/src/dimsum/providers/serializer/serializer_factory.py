"""
    serializer factory
"""
from dimsum.providers.serializer.dill_serializer import DillSerializer

class SerializerFactory():

    # book keeper factory
    @staticmethod
    def get_serializer(config):
        if config['type'] == 'dill':
            return DillSerializer(config)
        else:
            raise Exception('> serializer provider: %s is not supported' % (config['type']))

    # return supported serializer info
    @staticmethod
    def info():
        return ['dill_serializer: dill Serializer.']