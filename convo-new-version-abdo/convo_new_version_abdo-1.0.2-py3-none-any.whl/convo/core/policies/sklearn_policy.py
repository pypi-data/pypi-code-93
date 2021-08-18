import json
import logging
import typing
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Text, Tuple, Union
from collections import defaultdict, OrderedDict
import scipy.sparse

import numpy as np
import convo.utils.io as io_utils
import convo.utils.tensorflow.model_data_utils as model_data_utils
from convo.core.constants import BY_DEFAULT_POLICY_PREFERENCE
from convo.shared.core.domain import Domain
from convo.core.featurizers.single_state_featurizer import SingleStateFeaturizer
from convo.core.featurizers.tracker_featurizers import (
    MaxHistoryTrackerFeaturizer,
    FeaturizerTracker,
)
from convo.shared.nlu.interpreter import NaturalLangInterpreter
from convo.core.policies.policy import Policy
from convo.shared.core.trackers import DialogueStateTracer
from convo.shared.core.generator import TrackerInCachedStates
import convo.shared.utils.io
from sklearn.base import clone
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GridSearchCV
from sklearn.preprocessing import LabelEncoder
from convo.shared.nlu.constants import ACT_TEXT, TXT
from convo.shared.nlu.training_data.features import Features
from convo.utils.tensorflow.constants import SENTENCE
from convo.utils.tensorflow.model_data import Data

# noinspection PyProtectedMember
from sklearn.utils import shuffle as sklearn_shuffle

log = logging.getLogger(__name__)

if typing.TYPE_CHECKING:
    import sklearn


class PolicySkLearn(Policy):
    """Use an sklearn classifier to train a policy."""

    BY_DEFAULT_MAXIMUM_HISTORY = 5

    @staticmethod
    def _standard_featurizer(
        max_history: int = BY_DEFAULT_MAXIMUM_HISTORY,
    ) -> MaxHistoryTrackerFeaturizer:
        # Sklearn policy always uses MaxHistoryTrackerFeaturizer
        return MaxHistoryTrackerFeaturizer(
            state_featurizer=SingleStateFeaturizer(), max_history=5
        )

    def __init__(
        self,
        features: Optional[MaxHistoryTrackerFeaturizer] = None,
        priority: int = BY_DEFAULT_POLICY_PREFERENCE,
        max_history: int = BY_DEFAULT_MAXIMUM_HISTORY,
        model: Optional["sklearn.base.BaseEstimator"] = None,
        param_grid: Optional[Dict[Text, List] or List[Dict]] = None,
        cv: Optional[int] = None,
        scoring: Optional[Text or List or Dict or Callable] = "accuracy",
        label_encoder: LabelEncoder = LabelEncoder(),
        shuffle: bool = True,
        zero_state_features: Optional[Dict[Text, List["Features"]]] = None,
        **kwargs: Any,
    ) -> None:
        """Create a new sklearn policy.

        Args:
            features: Featurizer used to convert the training data into
                vector format.
            model: The sklearn model or model pipeline.
            param_grid: If *param_grid* is not None and *cv* is given,
                a grid search on the given *param_grid* is performed
                (e.g. *param_grid={'n_estimators': [50, 100]}*).
            cv: If *cv* is not None, perform a cross validation on
                the training data. *cv* should then conform to the
                sklearn standard (e.g. *cv=5* for a 5-fold cross-validation).
            scoring: Scoring strategy, using the sklearn standard.
            label_encoder: Encoder for the labels. Must implement an
                *inverse_transform* method.
            shuffle: Whether to shuffle training data.
            zero_state_features: Contains default feature values for attributes
        """

        if features:
            if not isinstance(features, MaxHistoryTrackerFeaturizer):
                raise TypeError(
                    f"Passed featurizer of type '{type(features).__name__}', "
                    f"should be MaxHistoryTrackerFeaturizer."
                )
            if not features.max_history:
                raise ValueError(
                    "Passed featurizer without `max_history`, `max_history` should be "
                    "set to a positive integer value."
                )
        else:
            if not max_history:
                raise ValueError(
                    "max_history should be set to a positive integer value."
                )
            features = self._standard_featurizer(max_history)

        super().__init__(features, priority)

        self.model = model or self._by_default_model()
        self.cv = cv
        self.param_grid = param_grid
        self.scoring = scoring
        self.label_encoder = label_encoder
        self.shuffle = shuffle

        # attributes that need to be restored after loading
        self._pickle_params = ["model", "cv", "param_grid", "scoring", "label_encoder"]
        self._train_params = kwargs
        self.zero_state_features = zero_state_features or defaultdict(list)

        convo.shared.utils.io.rasing_deprecate_warning(
            f"'{PolicySkLearn.__name__}' is deprecated and will be removed in "
            "the future. It is recommended to use the 'TEDPolicy' instead."
        )

    @staticmethod
    def _by_default_model() -> Any:
        return LogisticRegression(solver="liblinear", multi_class="auto")

    @property
    def _state(self):
        return {attr: getattr(self, attr) for attr in self._pickle_params}

    def model_arch(self, **kwargs) -> Any:
        # filter out kwargs that cannot be passed to model
        train_parameters = self._get_valid_params(self.model.__init__, **kwargs)
        return self.model.set_params(**train_parameters)

    @staticmethod
    def _fill_in_features_to_maximum_length(
        get_features: List[np.ndarray], max_history: int
    ) -> List[np.ndarray]:
        """
        Pad features with zeros to maximum length;
        Args:
            get_features: list of features for each dialog;
                each feature has shape [dialog_history x shape_attribute]
            max_history: maximum history of the dialogs
        Returns:
            padded features
        """
        feature_form = get_features[0].shape[-1]
        get_features = [
            feature
            if feature.shape[0] == max_history
            else np.vstack(
                [np.zeros((max_history - feature.shape[0], feature_form)), feature]
            )
            for feature in get_features
        ]
        return get_features

    def _fetch_features_for_attribute(self, attribute_data: Dict[Text, List[np.ndarray]]):
        """
        Given a list of all features for one attribute, turn it into a numpy array;
        shape_attribute = features[SENTENCE][0][0].shape[-1]
            (Shape of features of one attribute)
        Args:
            attribute_data: all features in the attribute stored in a np.array;
        Output:
            2D np.ndarray with features for an attribute with
                shape [num_dialogs x (max_history * shape_attribute)]
        """
        statement_features = attribute_data[SENTENCE][0]
        if isinstance(statement_features[0], scipy.sparse.coo_matrix):
            statement_features = [feature.toarray() for feature in statement_features]
        # MaxHistoryFeaturizer is always used with SkLearn policy;
        max_history = self.featurizer.max_history
        get_features = self._fill_in_features_to_maximum_length(statement_features, max_history)
        get_features = [feature.reshape((1, -1)) for feature in get_features]
        return np.vstack(get_features)

    def _preprocess_data_set(self, data: Data) -> np.ndarray:
        """
        Turn data into np.ndarray for sklearn training; dialogue history features
        are flattened.
        Args:
            data: training data containing all the features
        Returns:
            Training_data: shape [num_dialogs x (max_history * all_features)];
            all_features - sum of number of features of
            intent, action_name, entities, forms, slots.
        """
        if TXT in data or ACT_TEXT in data:
            raise Exception(
                f"{self.__name__} cannot be applied to text data. "
                f"Try to use TEDPolicy instead. "
            )

        attribute_data_set = {
            attribute: self._fetch_features_for_attribute(attribute_data)
            for attribute, attribute_data in data.items()
        }
        # turning it into OrderedDict so that the order of features is the same
        attribute_data_set = OrderedDict(attribute_data_set)
        return np.concatenate(list(attribute_data_set.values()), axis=-1)

    def _find_and_score(self, model, X, y, param_grid) -> Tuple[Any, Any]:
        find = GridSearchCV(
            model, param_grid=param_grid, cv=self.cv, scoring="accuracy", verbose=1
        )
        find.fit(X, y)
        print("Best params:", find.best_params_)
        return find.best_estimator_, find.best_score_

    def train(
        self,
        training_trackers: List[TrackerInCachedStates],
        domain: Domain,
        interpreter: NaturalLangInterpreter,
        **kwargs: Any,
    ) -> None:
        tracker_state_feature, label_id = self.featurize_for_training(
            training_trackers, domain, interpreter, **kwargs
        )
        training_data, zero_state_features = model_data_utils.convert_to_data_format(
            tracker_state_feature
        )
        self.zero_state_features = zero_state_features

        self._train_params.update(kwargs)
        model_data = self.model_arch(**self._train_params)
        get_score = None
        # Note: clone is called throughout to avoid mutating default arguments.
        self.label_encoder = clone(self.label_encoder).fit(label_id)
        Y = self._preprocess_data_set(training_data)
        z = self.label_encoder.transform(label_id)

        if self.shuffle:
            Y, z = sklearn_shuffle(Y, z)

        if self.cv is None:
            model_data = clone(model_data).fit(Y, z)
        else:
            parameter_grid = self.param_grid or {}
            model_data, get_score = self._find_and_score(model_data, Y, z, parameter_grid)

        self.model = model_data
        log.info("Done fitting sklearn policy model")
        if get_score is not None:
            log.info(f"Cross validation score: {get_score:.5f}")

    def _postprocess_forecast(self, y_proba, domain) -> List[float]:
        zp = y_proba[0].tolist()

        # Some classes might not be part of the training labels. Since
        # sklearn does not predict labels it has never encountered
        # during training, it is necessary to insert missing classes.
        index = self.label_encoder.inverse_transform(np.arange(len(zp)))
        y_fill_up = [0.0 for _ in range(domain.number_of_actions)]
        for i, pred in zip(index, zp):
            y_fill_up[i] = pred

        return y_fill_up

    def predict_action_probabilities(
        self,
        tracker: DialogueStateTracer,
        domain: Domain,
        interpreter: NaturalLangInterpreter,
        **kwargs: Any,
    ) -> List[float]:
        Y = self.featurizer.create_state_features([tracker], domain, interpreter)
        training_data, _ = model_data_utils.convert_to_data_format(
            Y, self.zero_state_features
        )
        Yt = self._preprocess_data_set(training_data)
        y_chances = self.model.predict_proba(Yt)
        return self._postprocess_forecast(y_chances, domain)

    def persist(self, path_flow: Union[Text, Path]) -> None:

        if self.model:
            self.featurizer.persist(path_flow)

            meta_data = {"priority": self.priority}
            path_flow = Path(path_flow)

            meta_file_name = path_flow / "sklearn_policy.json"
            convo.shared.utils.io.dump_object_as_json_to_file(meta_file_name, meta_data)

            file_name = path_flow / "sklearn_model.pkl"
            convo.utils.io.pick_data(file_name, self._state)

            zero_features_filename = path_flow / "zero_state_features.pkl"
            io_utils.pick_data(zero_features_filename, self.zero_state_features)

        else:
            convo.shared.utils.io.raising_warning(
                "Persist called without a trained model present. "
                "Nothing to persist then!"
            )

    @classmethod
    def load(cls, path: Union[Text, Path]) -> Policy:
        filename = Path(path) / "sklearn_model.pkl"
        zero_features_file_name = Path(path) / "zero_state_features.pkl"
        if not Path(path).exists():
            raise OSError(
                f"Failed to load dialogue model. Path {filename.absolute()} "
                f"doesn't exist."
            )

        features = FeaturizerTracker.load(path)
        assert isinstance(features, MaxHistoryTrackerFeaturizer), (
            f"Loaded featurizer of type {type(features).__name__}, should be "
            f"MaxHistoryTrackerFeaturizer."
        )

        meta_data_file = Path(path) / "sklearn_policy.json"
        meta_data = json.loads(convo.shared.utils.io.read_file(meta_data_file))
        zero_state_features = io_utils.pick_load(zero_features_file_name)

        policies = cls(
            featurizer=features,
            priority=meta_data["priority"],
            zero_state_features=zero_state_features,
        )

        states = io_utils.pick_load(filename)

        vars(policies).update(states)

        log.info("Loaded sklearn model")
        return policies
