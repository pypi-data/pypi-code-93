#!/usr/bin/env python
# coding: utf-8

from typing import List, Any
from dsframework.base.common.component import ZIDS_Component
from dsframework.base.pipeline.predictables.predictable import ZIDS_Predictable
from dsframework.base.pipeline.artifacts.shared_artifacts import ZIDS_SharedArtifacts

class ZIDS_Preprocessor(ZIDS_Component):

    def __init__(self, artifacts:ZIDS_SharedArtifacts=None):
        super().__init__(artifacts)
        self.input = None

    def __call__(self, **kwargs: Any) -> Any:
        return self.execute(**kwargs)

    def normalize_input(self, **kwargs: Any) -> Any:
        raise NotImplementedError

    def preprocess(self, raw_input:Any):
        raise NotImplementedError
        # Should return a list of predictable objects

    def execute(self, **kwargs: Any) -> List[ZIDS_Predictable]:
        self.input = self.normalize_input(**kwargs)
        return self.preprocess(self.input)

