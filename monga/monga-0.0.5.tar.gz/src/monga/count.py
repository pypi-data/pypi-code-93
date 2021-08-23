class Count:
    def __init__(self, collection):
        self.collection = collection

    def call(self, query: dict):
        if query:
            return self.collection.count_documents(query)
        else:
            return self.collection.count_documents({})
