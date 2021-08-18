#!/usr/bin/env python
# coding: utf-8

from typing import List, Any

class ZIDS_Component:

    def __init__(self, artifacts=None) -> None:
        self.artifacts = artifacts
        self.build()
        self.config()
        self.config_from_json()
        self.connect()

    def __call__(self, predictables:List[Any], **kwargs):
        return self.execute(predictables, **kwargs)
    
    def execute(self, predictables:List[Any], **kwargs) -> List[Any]:
        self.reset(predictables)
        self.pre_run(predictables)
        self.run(predictables)
        self.post_run(predictables)
        self.evaluate(predictables)
        return predictables

    def build(self):
        pass

    def config(self):
        pass

    def config_from_json(self):
        pass

    def connect(self):
        pass

    def reset(self,  predictables:List[Any]):
        pass
    
    def pre_run(self,  predictables:List[Any]):
        pass

    def run(self,  predictables:List[Any]):
        pass

    def post_run(self,  predictables:List[Any]):
        pass

    def evaluate(self,  predictables:List[Any]):
        pass
