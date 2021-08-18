#!/usr/bin/env python
# coding: utf-8

from typing import List
from dsframework.base.common.component import ZIDS_Component
from dsframework.base.pipeline.predictables.predictable import ZIDS_Predictable
from dsframework.base.pipeline.artifacts.shared_artifacts import ZIDS_SharedArtifacts

class ZIDS_Pipeline():

    def __init__(self):
        self.components:List[ZIDS_Component] = []
        self.predictables:List[ZIDS_Predictable] = []
        self.artifacts = self.get_artifacts()
        self.build_pipeline()
        self.configure_pipeline()
        self.connect_pipeline()

    def get_artifacts(self):
        return ZIDS_SharedArtifacts()
    
    def build_pipeline(self):
        raise NotImplementedError
        # Should use add_component to build the stack
    
    def configure_pipeline(self, **kwargs):
        pass

    def connect_pipeline(self):
        for c in self.components:
            c.artifacts = self.artifacts

    def preprocess(self, **kwargs) -> List[ZIDS_Predictable]:
        raise NotImplementedError
        # Should return a list of predictable objects
  
    def postprocess(self, predictables):
        raise NotImplementedError
        # Should return an output

    def add_component(self, component:ZIDS_Component):
        self.components.append(component)

    def __call__(self,  **kwargs):
        return self.execute( **kwargs)

    def execute(self, **kwargs):
        self.predictables = self.preprocess(**kwargs)
        for c in self.components:
            self.predictables = c.execute(self.predictables)
        return self.postprocess(self.predictables)
