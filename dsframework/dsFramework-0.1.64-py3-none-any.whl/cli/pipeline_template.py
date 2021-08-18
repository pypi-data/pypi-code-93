import os

__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))

from dsframework.base.pipeline.pipeline import ZIDS_Pipeline

from pipeline.preprocessor.preprocess import generatedProjectNamePreprocess
from pipeline.postprocessor.postprocess import generatedProjectNamePostprocess
from pipeline.predictors.predictor import generatedProjectNamePredictor
from pipeline.forcers.forcer import generatedProjectNameForcer
from pipeline.artifacts.shared_artifacts import generatedProjectNameSharedArtifacts

class generatedClass(ZIDS_Pipeline):

    def __init__(self):
        super().__init__()

    def get_artifacts(self):
        return generatedProjectNameSharedArtifacts()

    def build_pipeline(self):
        self.preprocessor = generatedProjectNamePreprocess(artifacts=self.artifacts)
        self.postprocessor = generatedProjectNamePostprocess(artifacts=self.artifacts)
        self.predictor = generatedProjectNamePredictor()
        self.forcer = generatedProjectNameForcer()
        self.add_component(self.predictor)
        self.add_component(self.forcer)

    def preprocess(self, **kwargs):
        return self.preprocessor(**kwargs)

    def postprocess(self, predictables):
        return self.postprocessor(predictables)
