from extended_preprocessors.preprocessors.bins_linearizer import BinsLinearizer
from extended_preprocessors.preprocessors.feature_by_feature_transformer import FeatureByFeatureTransformer


class DatasetLinearizer(FeatureByFeatureTransformer):
    def __init__(self):
        super().__init__()
        self.transformers = []

    def _get_transformer(self, i: int) -> BinsLinearizer:
        return BinsLinearizer()
