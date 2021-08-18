#!/usr/bin/env python
# coding: utf-8

from typing import List, Any
from dsframework.base.common.component import ZIDS_Component
from dsframework.base.pipeline.predictables.predictable import ZIDS_Predictable
from dsframework.base.pipeline.artifacts.shared_artifacts import ZIDS_SharedArtifacts

class ZIDS_Postprocessor(ZIDS_Component):

    def __init__(self, artifacts:ZIDS_SharedArtifacts=None) -> None:
        super().__init__(artifacts)

    def normalize_output(self, predictables:List[ZIDS_Predictable]) -> Any:
        raise NotImplementedError
        # Should return the final output

    def execute(self,  predictables:List[Any]) -> Any:
        return self.normalize_output(super().execute(predictables))
