class FindOne:
    def __init__(self, collection):
        self.collection = collection

    def call(self, query: dict):
        return self.collection.find_one(query)
