class Datasource:
    def columns(self):
        raise NotImplementedError

    def create_one(self, data):
        raise NotImplementedError

    def select_one(self, id):
        raise NotImplementedError

    def delete_one(self, id):
        raise NotImplementedError

    def update_one(self, id, data):
        raise NotImplementedError

    def select_many(self, query):
        raise NotImplementedError
