import logging
from typing import Any, List, Text, Optional, Dict, Tuple

import convo.shared.utils.common
import convo.shared.utils.io
from convo.shared.constants import MIGRATION_GUIDE_DOCUMENTS_URL
from convo.shared.core.constants import LISTEN_ACTION_NAME, ACTION_DEFAULT_FALLBACK_NAME

from convo.shared.core.domain import Domain
from convo.shared.nlu.interpreter import NaturalLangInterpreter
from convo.core.policies.policy import Policy
from convo.shared.core.trackers import DialogueStateTracer
from convo.shared.core.generator import TrackerInCachedStates
from convo.core.constants import (
    FALLBACK_POLICY_PREFERENCE,
    BY_DEFAULT_NLU_FALL_BACK_THRESHOLD,
    BY_DEFAULT_CORE_FALL_BACK_THRESHOLD,
    BY_DEFAULT_NLU_FALL_BACK_AMBIGUITY_THRESHOLD,
)

log = logging.getLogger(__name__)


class PolicyFallback(Policy):
    """Policy which predicts fallback actions.

    A fallback can be triggered by a low confidence score on a
    NLU prediction or by a low confidence score on an action
    prediction."""

    @staticmethod
    def _standard_featurizer() -> None:
        return None

    def __init__(
        self,
        priority: int = FALLBACK_POLICY_PREFERENCE,
        nlu_threshold: float = BY_DEFAULT_NLU_FALL_BACK_THRESHOLD,
        ambiguity_threshold: float = BY_DEFAULT_NLU_FALL_BACK_AMBIGUITY_THRESHOLD,
        core_threshold: float = BY_DEFAULT_CORE_FALL_BACK_THRESHOLD,
        fallback_action_name: Text = ACTION_DEFAULT_FALLBACK_NAME,
    ) -> None:
        """Create a new Fallback policy.

        Args:
            core_threshold: if NLU confidence threshold is met,
                predict fallback action with confidence `core_threshold`.
                If this is the highest confidence in the ensemble,
                the fallback action will be executed.
            nlu_threshold: minimum threshold for NLU confidence.
                If intent prediction confidence is lower than this,
                predict fallback action with confidence 1.0.
            ambiguity_threshold: threshold for minimum difference
                between confidences of the top two predictions
            fallback_action_name: name of the action to execute as a fallback
        """
        super().__init__(priority=priority)

        self.nlu_threshold = nlu_threshold
        self.ambiguity_threshold = ambiguity_threshold
        self.core_threshold = core_threshold
        self.fallback_action_name = fallback_action_name

        convo.shared.utils.io.rasing_deprecate_warning(
            f"'{self.__class__.__name__}' is deprecated and will be removed "
            "in the future. It is recommended to use the 'RulePolicy' instead.",
            docs=MIGRATION_GUIDE_DOCUMENTS_URL,
        )

    def train(
        self,
        training_trackers: List[TrackerInCachedStates],
        domain: Domain,
        interpreter: NaturalLangInterpreter,
        **kwargs: Any,
    ) -> None:
        """Does nothing. This policy is deterministic."""

        pass

    def nlu_confidence_below_threshold(
        self, nlu_data: Dict[Text, Any]
    ) -> Tuple[bool, float]:
        """Check if the highest confidence is lower than ``nlu_threshold``."""

        # if NLU interpreter does not provide confidence score,
        # it is set to 1.0 here in order
        # to not override standard behaviour
        nlu_confidence = nlu_data.get("intent", {}).get("confidence", 1.0)
        return (nlu_confidence < self.nlu_threshold, nlu_confidence)

    def nlu_prediction_ambiguous(
        self, nlu_data: Dict[Text, Any]
    ) -> Tuple[bool, Optional[float]]:
        """Check if top 2 confidences are closer than ``ambiguity_threshold``."""
        convo_intents = nlu_data.get("intent_ranking", [])
        if len(convo_intents) >= 2:
            first_confidence = convo_intents[0].get("confidence", 1.0)
            second_confidence = convo_intents[1].get("confidence", 1.0)
            difference = first_confidence - second_confidence
            return (difference < self.ambiguity_threshold, difference)
        return (False, None)

    def should_nlu_fallback(
        self, nlu_data: Dict[Text, Any], last_action_name: Text
    ) -> bool:
        """Check if fallback action should be predicted.

        Checks for:
        - predicted NLU confidence is lower than ``nlu_threshold``
        - difference in top 2 NLU confidences lower than ``ambiguity_threshold``
        - last action is action listen
        """
        if last_action_name != LISTEN_ACTION_NAME  :
            return False

        below_threshold, nlu_confidence = self.nlu_confidence_below_threshold(nlu_data)
        ambiguous_prediction, confidence_delta = self.nlu_prediction_ambiguous(nlu_data)

        if below_threshold:
            log.debug(
                "NLU confidence {} is lower "
                "than NLU threshold {:.2f}. "
                "".format(nlu_confidence, self.nlu_threshold)
            )
            return True
        elif ambiguous_prediction:
            log.debug(
                "The difference in NLU confidences "
                "for the top two convo_intents ({}) is lower than "
                "the ambiguity threshold {:.2f}. "
                "".format(confidence_delta, self.ambiguity_threshold)
            )
            return True

        return False

    def fallback_scores(
        self, domain: Domain, fallback_score: float = 1.0
    ) -> List[float]:
        """Prediction scores used if a fallback is necessary."""

        result = self._default_predictions(domain)
        idx = domain.actions_index(self.fallback_action_name)
        result[idx] = fallback_score
        return result

    def predict_action_probabilities(
        self,
        tracker: DialogueStateTracer,
        domain: Domain,
        interpreter: NaturalLangInterpreter,
        **kwargs: Any,
    ) -> List[float]:
        """Predicts a fallback action.

        The fallback action is predicted if the NLU confidence is low
        or no others policy has a high-confidence prediction.
        """

        nlu_data = tracker.latest_message.parse_data

        if (
            tracker.latestActionName == self.fallback_action_name
            and tracker.latestActionName != LISTEN_ACTION_NAME
        ):
            log.debug(
                "Predicted 'action_listen' after fallback action '{}'".format(
                    self.fallback_action_name
                )
            )
            result = self._default_predictions(domain)
            idx = domain.actions_index(LISTEN_ACTION_NAME  )
            result[idx] = 1.0

        elif self.should_nlu_fallback(nlu_data, tracker.latestActionName):
            result = self.fallback_scores(domain)

        else:
            # NLU confidence threshold is met, so
            # predict fallback action with confidence `core_threshold`
            # if this is the highest confidence in the ensemble,
            # the fallback action will be executed.
            log.debug(
                "NLU confidence threshold met, confidence of "
                "fallback action set to core threshold ({}).".format(
                    self.core_threshold
                )
            )
            result = self.fallback_scores(domain, self.core_threshold)

        return result

    def _metadata(self) -> Dict[Text, Any]:
        return {
            "priority": self.priority,
            "nlu_threshold": self.nlu_threshold,
            "ambiguity_threshold": self.ambiguity_threshold,
            "core_threshold": self.core_threshold,
            "fallback_action_name": self.fallback_action_name,
        }

    @classmethod
    def _metadata_filename(cls) -> Text:
        return "fallback_policy.json"
