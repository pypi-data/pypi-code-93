import numpy as np
from extended_preprocessors.preprocessors.categorical_discretizer import CategoricalFeatureDiscretizer
from extended_preprocessors.preprocessors.feature_by_feature_transformer import FeatureByFeatureTransformer
from extended_preprocessors.preprocessors.feature_discretizer import FeatureDiscretizer
from extended_preprocessors.preprocessors.numeric_discretizer import NumericalFeatureDiscretizer


class DatasetBinarizer(FeatureByFeatureTransformer):
    def __init__(
        self,
        categorical_features: np.ndarray = None,
        max_bins: int = 32,
        use_median: bool = True,
    ) -> None:
        super().__init__()
        self.categorical_features = (
            categorical_features if categorical_features is not None else []
        )
        self.transformers = []
        self.max_bins = max_bins
        self.use_median = use_median

    def _get_transformer(self, i: int) -> FeatureDiscretizer:
        if i in self.categorical_features:
            return CategoricalFeatureDiscretizer(use_median=self.use_median)
        return NumericalFeatureDiscretizer(
            max_bins=self.max_bins, use_median=self.use_median
        )

    def set_params(self, **kwargs):
        for k, v in kwargs.items():
            self.__dict__[k] = v
