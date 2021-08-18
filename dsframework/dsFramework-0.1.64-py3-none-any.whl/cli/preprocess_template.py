# !/usr/bin/env python
# coding: utf-8

from typing import List, Any

from dsframework.base.pipeline.preprocessor import ZIDS_Preprocessor
from pipeline.schema.inputs import generatedProjectNameInputs
from pipeline.schema.outputs import generatedProjectNameOutputs
from pipeline.artifacts.shared_artifacts import generatedProjectNameSharedArtifacts


class generatedClass(ZIDS_Preprocessor):

    def __init__(self, artifacts: generatedProjectNameSharedArtifacts = None):
        super().__init__(artifacts)

    def normalize_input(self, **kwargs: Any) -> generatedProjectNameInputs:
        return generatedProjectNameInputs(**kwargs)

    def config(self):
        pass

    def connect(self):
        super().connect()

    def reset(self, text: str = '', hints: List[Any] = []):
        pass

    def get_from_regex(self):
        pass

    def preprocess(self, raw_input: Any):
        raise NotImplementedError
