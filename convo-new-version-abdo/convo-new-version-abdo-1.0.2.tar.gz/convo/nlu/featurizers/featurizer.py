import numpy as np
from typing import Text, Optional, Dict, Any

from convo.nlu.constants import FEATURE_CLASS_AS
from convo.nlu.components import Element
from convo.utils.tensorflow.constants import MEAN_POOL, MAXIMUM_POOLING


class Featurizer(Element):
    def __init__(self, component_configuration: Optional[Dict[Text, Any]] = None) -> None:
        if not component_configuration:
            component_configuration = {}

        # makes sure the alias name is set
        component_configuration.setdefault(FEATURE_CLASS_AS, self.name)

        super().__init__(component_configuration)


class CondensedFeaturizer(Featurizer):
    @staticmethod
    def _calculate_statement_features(
        features: np.ndarray, pooling_operation: Text
    ) -> np.ndarray:
        # take only non zeros feature vectors into account
        not_zero_features = np.array([f for f in features if f.any()])

        # if features are all zero just return a vector with all zeros
        if not_zero_features.size == 0:
            return np.zeros([1, features.shape[-1]])

        if pooling_operation == MEAN_POOL:
            return np.mean(not_zero_features, axis=0, keepdims=True)

        if pooling_operation == MAXIMUM_POOLING:
            return np.max(not_zero_features, axis=0, keepdims=True)

        raise ValueError(
            f"Invalid pooling operation specified. Available operations are "
            f"'{MEAN_POOL}' or '{MAXIMUM_POOLING}', but provided value is "
            f"'{pooling_operation}'."
        )


class InfrequentFeaturizer(Featurizer):
    pass
