'''
======================================================================
Error classses for carte blanche_utils serializers
----------------------------------------------------------------------
'''


class CarteBlancheSerializerException(Exception):
    """docstring for CarteBlancheSerializerException"""
    def __init__(self):
        super(CarteBlancheSerializerException, self).__init__()
        self.code = 1000
        self.exception = {
            'code': self.code,
            'title': 'CarteBlancheSerializerException',
            'message': 'Base Exception for the CarteBlanche serializers. You fucked up'
        }


class CarteBlancheSerializerUnHashableDataTypeException(CarteBlancheSerializerException):
    """docstring for CarteBlancheSerializerUnHashableDataTypeException"""
    def __init__(self, args):
        super(CarteBlancheSerializerUnHashableDataTypeException, self).__init__()
        self.args = args
        self.code = 1001
        self.exception = {
            'code': self.code,
            'title': 'CarteBlancheSerializerUnHashableDataTypeException',
            'message': '{0} is not currently supported by this serializer'
                        .format(args['message']),
            'detail': args['message']
        }
