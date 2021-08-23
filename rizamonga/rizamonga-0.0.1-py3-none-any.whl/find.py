class Find:
    def __init__(self, collection):
        self.collection = collection

    def call(self, query: dict):
        return list(self.collection.find(query))
