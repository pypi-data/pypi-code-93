# Monga - MongoDB Client wrapper
#
# Copyright (c) Riza Masykur 2021.
#
# History:
# 0.1   17-08-21 yk     Created

from .find_one import FindOne
from .find import Find
from .aggregate import Aggregate
from .count import Count
from .insert_one import InsertOne
from .find_one_and_update import FindOneAndUpdate


class Monga:
    def __init__(self, collection):
        self.collection = collection

    def find_one(self, query: dict = {}):
        return FindOne(self.collection).call(query)

    def find(self, query: dict = {}):
        return Find(self.collection).call(query)

    def aggregate(self, pipeline: list = []):
        return Aggregate(self.collection).call(pipeline)

    def count(self, query=dict):
        return Count(self.collection).call(query)

    def insert_one(self, data: dict):
        return InsertOne(self.collection).call(data)

    def find_one_and_update(self, query: dict, update: dict):
        return FindOneAndUpdate(self.collection).call(query, update)