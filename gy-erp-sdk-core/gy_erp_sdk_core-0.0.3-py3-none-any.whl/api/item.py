from gyerpsdkcore.api.base import BaseApi


class Item(BaseApi):
    KEY = "gy.erp.item"

    def get(self, key):
        print(key)

    def create(self):
        pass


