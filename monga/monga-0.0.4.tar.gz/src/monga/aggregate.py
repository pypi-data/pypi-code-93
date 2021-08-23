class Aggregate:
    def __init__(self, collection):
        self.collection = collection

    def call(self, pipeline: list):
        return list(self.collection.aggregate(pipeline, allowDiskUse=True))
