import copy
import json
import logging
from enum import Enum
from pathlib import Path
from typing import (
    Any,
    List,
    Optional,
    Text,
    Dict,
    Callable,
    Type,
    Union,
    Tuple,
    TYPE_CHECKING,
)
import numpy as np

import convo.shared.utils.common
import convo.utils.common
import convo.shared.utils.io
from convo.shared.core.domain import Domain
from convo.core.featurizers.single_state_featurizer import SingleStateFeaturizer
from convo.core.featurizers.tracker_featurizers import (
    FeaturizerTracker,
    MaxHistoryTrackerFeaturizer,
    FEATURIZER_FILENAME,
)
from convo.shared.nlu.interpreter import NaturalLangInterpreter
from convo.shared.core.trackers import DialogueStateTracer
from convo.shared.core.generator import TrackerInCachedStates
from convo.core.constants import BY_DEFAULT_POLICY_PREFERENCE

if TYPE_CHECKING:
    from convo.shared.nlu.training_data.features import Features


logger = logging.getLogger(__name__)


class SupportedDataSet(Enum):
    """Enumeration of a policy's supported training data type."""

    # policy only supports ML-based training data ("stories")
    MACHINELEARNING_DATA_SET = 1

    # policy only supports rule-based data ("rules")
    RULE_DATA_SET = 2

    # policy supports both ML-based and rule-based data ("stories" as well as "rules")
    ML_AND_RULE_DATA = 3

    @staticmethod
    def trackers_for_policy(
        policy: Union["Policy", Type["Policy"]],
        trackers: Union[List[DialogueStateTracer], List[TrackerInCachedStates]],
    ) -> Union[List[DialogueStateTracer], List[TrackerInCachedStates]]:
        """Return trackers for a given policy.

        Args:
            policy: Policy or policy type to return trackers for.
            trackers: Trackers to split.

        Returns:
            Trackers from ML-based training data and/or rule-based data.
        """
        supported_data = policy.supported_data()

        if supported_data == SupportedDataSet.RULE_DATA_SET:
            return [tracker for tracker in trackers if tracker.is_rule_tracker]

        if supported_data == SupportedDataSet.MACHINELEARNING_DATA_SET:
            return [tracker for tracker in trackers if not tracker.is_rule_tracker]

        # `supported_data` is `SupportedDataSet.ML_AND_RULE_DATA`
        return trackers


class Policy:
    @staticmethod
    def supported_data() -> SupportedDataSet:
        """The type of data supported by this policy.

        By default, this is only ML-based training data. If policies support rule data,
        or both ML-based data and rule data, they need to override this method.

        Returns:
            The data type supported by this policy (ML-based training data).
        """
        return SupportedDataSet.MACHINELEARNING_DATA_SET

    @staticmethod
    def _standard_featurizer() -> MaxHistoryTrackerFeaturizer:
        return MaxHistoryTrackerFeaturizer(SingleStateFeaturizer())

    @classmethod
    def _create_featurizer(
        cls, featurizer: Optional[FeaturizerTracker] = None
    ) -> FeaturizerTracker:
        if featurizer:
            return copy.deepcopy(featurizer)
        else:
            return cls._standard_featurizer()

    def __init__(
        self,
        featurizer: Optional[FeaturizerTracker] = None,
        priority: int = BY_DEFAULT_POLICY_PREFERENCE,
    ) -> None:
        self.__featurizer = self._create_featurizer(featurizer)
        self.priority = priority

    @property
    def featurizer(self):
        return self.__featurizer

    @staticmethod
    def _get_valid_params(func: Callable, **kwargs: Any) -> Dict:
        """Filters out kwargs that cannot be passed to func.

        Args:
            func: a callable function

        Returns:
            the dictionary of parameters
        """

        valid_keys = convo.shared.utils.common.args_of(func)

        params = {key: kwargs.get(key) for key in valid_keys if kwargs.get(key)}
        ignored_params = {
            key: kwargs.get(key) for key in kwargs.keys() if not params.get(key)
        }
        logger.debug(f"Parameters ignored by `model.fit(...)`: {ignored_params}")
        return params

    def featurize_for_training(
        self,
        training_trackers: List[DialogueStateTracer],
        domain: Domain,
        interpreter: NaturalLangInterpreter,
        **kwargs: Any,
    ) -> Tuple[List[List[Dict[Text, List["Features"]]]], np.ndarray]:
        """Transform training trackers into a vector representation.

        The trackers, consisting of multiple turns, will be transformed
        into a float vector which can be used by a ML model.

        Args:
            training_trackers:
                the list of the :class:`convo.core.trackers.DialogueStateTracer`
            domain: the :class:`convo.shared.core.domain.Domain`
            interpreter: the :class:`convo.core.interpreter.NaturalLangInterpreter`

        Returns:
            - a dictionary of attribute (INTENTION, TXT, ACT_NAME, ACT_TEXT,
              ENTITIES_NAME, CONVO_SLOTS, FORM) to a list of features for all dialogue turns in
              all training trackers
            - the label ids (e.g. action ids) for every dialogue turn in all training
              trackers
        """

        state_features, label_ids = self.featurizer.featurize_trackers(
            training_trackers, domain, interpreter
        )

        max_training_samples = kwargs.get("max_training_samples")
        if max_training_samples is not None:
            logger.debug(
                "Limit training data to {} training samples."
                "".format(max_training_samples)
            )
            state_features = state_features[:max_training_samples]
            label_ids = label_ids[:max_training_samples]

        return state_features, label_ids

    def train(
        self,
        training_trackers: List[TrackerInCachedStates],
        domain: Domain,
        interpreter: NaturalLangInterpreter,
        **kwargs: Any,
    ) -> None:
        """Trains the policy on given training trackers.

        Args:
            training_trackers:
                the list of the :class:`convo.core.trackers.DialogueStateTracer`
            domain: the :class:`convo.shared.core.domain.Domain`
            interpreter: Interpreter which can be used by the polices for featurization.
        """

        raise NotImplementedError("Policy must have the capacity to train.")

    def predict_action_probabilities(
        self,
        tracker: DialogueStateTracer,
        domain: Domain,
        interpreter: NaturalLangInterpreter,
        **kwargs: Any,
    ) -> List[float]:
        """Predicts the next action the bot should take after seeing the tracker.

        Args:
            tracker: the :class:`convo.core.trackers.DialogueStateTracer`
            domain: the :class:`convo.shared.core.domain.Domain`
            interpreter: Interpreter which may be used by the policies to create
                additional features.

        Returns:
             the list of probabilities for the next actions
        """

        raise NotImplementedError("Policy must have the capacity to predict.")

    def _metadata(self) -> Optional[Dict[Text, Any]]:
        """Returns this policy's attributes that should be persisted.

        Policies following the default `persist()` and `load()` templates must
        implement the `_metadata()` method."

        Returns:
            The policy metadata.
        """
        pass

    @classmethod
    def _metadata_filename(cls) -> Optional[Text]:
        """Returns the filename of the persisted policy metadata.

        Policies following the default `persist()` and `load()` templates must
        implement the `_metadata_filename()` method.

        Returns:
            The filename of the persisted policy metadata.
        """
        pass

    def persist(self, path: Union[Text, Path]) -> None:
        """Persists the policy to storage.

        Args:
            path: Path to persist policy to.
        """
        # not all policies have a featurizer
        if self.featurizer is not None:
            self.featurizer.persist(path)

        file = Path(path) / self._metadata_filename()

        convo.shared.utils.io.create_dir_from_file(file)
        convo.shared.utils.io.dump_object_as_json_to_file(file, self._metadata())

    @classmethod
    def load(cls, path: Union[Text, Path]) -> "Policy":
        """Loads a policy from path.

        Args:
            path: Path to load policy from.

        Returns:
            An instance of `Policy`.
        """
        meta_data_set_file = Path(path) / cls._metadata_filename()

        if meta_data_set_file.is_file():
            data_set = json.loads(convo.shared.utils.io.read_file(meta_data_set_file))

            if (Path(path) / FEATURIZER_FILENAME).is_file():
                featurizer = FeaturizerTracker.load(path)
                data_set["featurizer"] = featurizer

            return cls(**data_set)

        logger.info(
            f"Couldn't load metadata for policy '{cls.__name__}'. "
            f"File '{meta_data_set_file}' doesn't exist."
        )
        return cls()

    @staticmethod
    def _default_predictions(domain: Domain) -> List[float]:
        """Creates a list of zeros.

        Args:
            domain: the :class:`convo.shared.core.domain.Domain`
        Returns:
            the list of the length of the number of actions
        """

        return [0.0] * domain.number_of_actions


def confidence_scores_for(
    action_name: Text, value: float, domain: Domain
) -> List[float]:
    """Returns confidence scores if a single action is predicted.

    Args:
        action_name: the name of the action for which the score should be set
        value: the confidence for `action_name`
        domain: the :class:`convo.shared.core.domain.Domain`

    Returns:
        the list of the length of the number of actions
    """

    results = [0.0] * domain.number_of_actions
    idx = domain.actions_index(action_name)
    results[idx] = value

    return results
