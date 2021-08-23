

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

        if 'uid' in data:
            data.update({'_id': data.get('uid')})
            del data['uid']

        try:
            return self.collection.insert_one(data).inserted_id
        except Exception as e:

            # send err msg
            # Log(f'err insert data', 'error').send()

            return None