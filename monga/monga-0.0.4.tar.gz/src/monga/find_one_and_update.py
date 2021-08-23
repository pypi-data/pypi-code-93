from pymongo import ReturnDocument


class FindOneAndUpdate:
    def __init__(self, collection):
        self.collection = collection

    def call(self, query: dict, update: dict):
        return self.collection.find_one_and_update(
            query,  #
            update,
            return_document=ReturnDocument.BEFORE)
