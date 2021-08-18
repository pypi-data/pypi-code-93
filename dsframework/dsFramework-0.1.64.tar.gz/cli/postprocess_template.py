 # !/usr/bin/env python
# coding: utf-8

from dsframework.base.pipeline.predictables.predictable import ZIDS_Predictable
from typing import List, Union

from dsframework.base.pipeline.postprocessor import ZIDS_Postprocessor
from pipeline.artifacts.shared_artifacts import generatedProjectNameSharedArtifacts
from pipeline.schema.outputs import generatedProjectNameOutputs

class generatedClass(ZIDS_Postprocessor):

    def __init__(self, artifacts: generatedProjectNameSharedArtifacts = None) -> None:
        super().__init__(artifacts)

    def config(self):
        pass

    def normalize_output(self, predictables: Union[ZIDS_Predictable, List[ZIDS_Predictable]]) -> Union[generatedProjectNameOutputs, List[generatedProjectNameOutputs]]:
        output: generatedProjectNameOutputs = ''
        isList = isinstance(predictables, list)
        if isList:
            output: List[generatedProjectNameOutputs] = []
        if isList:
            if predictables and len(predictables):
                for item in predictables:
                    output.append(self.get_output_object(item))
        else:
            output = self.get_output_object(predictables)
        return output

    def get_output_object(self, predictable):
        raise NotImplementedError
        pred = predictable[0]
        prob = predictable[-1]

        if(pred >= self.artifacts.threshold):
            prob = True
        else:
            prob = False

        return generatedProjectNameOutputs(pred=pred, prob=prob)
