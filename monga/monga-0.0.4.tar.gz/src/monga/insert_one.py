# from libs.logs import Exc, Log


class InsertOne:
    def __init__(self, collection):
        self.collection = collection

    def call(self, data: dict):
        if type(data) is not dict:
            data = data.dict()
        '''
        data dengan variabel {uid} akan dihapus
        dan diubah menjadi _id
        '''
        exc = Exc.create_exception()

        if 'uid' in data:
            data.update({'_id': data.get('uid')})
            del data['uid']

        try:
            return self.collection.insert_one(data).inserted_id
        except Exception as e:

            # send err msg
            exc.exception(e)

            # send log msg to stdout
            # Log(f'err insert data', 'error').send()

            return None