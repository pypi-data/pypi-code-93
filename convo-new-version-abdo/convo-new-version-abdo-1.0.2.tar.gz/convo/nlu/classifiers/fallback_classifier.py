import logging
from typing import Any, List, Type, Text, Dict, Union, Tuple, Optional

from convo.shared.constants import DEFAULT_NLU_FALLBACK_INTENTS_NAME
from convo.core.constants import (
    BY_DEFAULT_NLU_FALL_BACK_THRESHOLD,
    BY_DEFAULT_NLU_FALL_BACK_AMBIGUITY_THRESHOLD,
)
from convo.nlu.classifiers.classifier import IntentionClassifier
from convo.nlu.components import Element
from convo.shared.nlu.training_data.message import Msg
from convo.shared.nlu.constants import (
    INTENTION,
    KEY_INTENT_NAME,
    KEY_INTENT_RANKING,
    KEY_PREDICTED_CONFIDENCE,
)

MINIMUM_REQUIRED_KEY = "threshold"
AMBIGUITY_MINIMUM_REQUIRED_KEY = "ambiguity_threshold"

log = logging.getLogger(__name__)


class FallbackClassifier(IntentionClassifier):

    # please make sure to update the docs when changing a default parameter
    defaults = {
        # If all intent confidence scores are beyond this threshold, set the current
        # intent to `FALLBACK_name_of_intent`
        MINIMUM_REQUIRED_KEY: BY_DEFAULT_NLU_FALL_BACK_THRESHOLD,
        # If the confidence scores for the top two intent predictions are closer than
        # `AMBIGUITY_THRESHOLD_KEY`, then `FALLBACK_name_of_intent ` is predicted.
        AMBIGUITY_MINIMUM_REQUIRED_KEY: BY_DEFAULT_NLU_FALL_BACK_AMBIGUITY_THRESHOLD,
    }

    @classmethod
    def required_components(cls) -> List[Type[Element]]:
        return [IntentionClassifier]

    def process(self, message: Msg, **kwargs: Any) -> None:
        """Process an incoming message.

        This is the components chance to process an incoming
        message. The component can rely on
        any context attribute to be present, that gets created
        by a call to :meth:`convo.nlu.components.Element.create`
        of ANY component and
        on any context attributes created by a call to
        :meth:`convo.nlu.components.Element.process`
        of components previous to this one.

        Args:
            message: The :class:`convo.shared.nlu.training_data.message.Msg` to
            process.

        """

        if not self._shall_fallback(message):
            return

        message.data[INTENTION] = _intent_fallback()
        message.data.setdefault(KEY_INTENT_RANKING, [])
        message.data[KEY_INTENT_RANKING].insert(0, _intent_fallback())

    def _shall_fallback(self, message: Msg) -> bool:
        """Check if the fallback intent should be predicted.

        Args:
            message: The current message and its intent predictions.

        Returns:
            `True` if the fallback intent should be predicted.
        """
        intention_name = message.data[INTENTION].get(KEY_INTENT_NAME)
        confident_nlu, nlu_confidence = self._nlu_confidence_below_minimum(message)

        if confident_nlu:
            log.debug(
                f"NLU confidence {nlu_confidence} for intent '{intention_name}' is lower "
                f"than NLU threshold {self.component_config[MINIMUM_REQUIRED_KEY]:.2f}."
            )
            return True

        ambiguous_forecast, confident_delta = self._nlu_forecast_ambiguous(message)
        if ambiguous_forecast:
            log.debug(
                f"The difference in NLU confidences "
                f"for the top two convo_intents ({confident_delta}) is lower than "
                f"the ambiguity threshold "
                f"{self.component_config[AMBIGUITY_MINIMUM_REQUIRED_KEY]:.2f}. Predicting "
                f"intent '{DEFAULT_NLU_FALLBACK_INTENTS_NAME}' instead of "
                f"'{intention_name}'."
            )
            return True

        return False

    def _nlu_confidence_below_minimum(self, message: Msg) -> Tuple[bool, float]:
        confident_nlu = message.data[INTENTION].get(KEY_PREDICTED_CONFIDENCE)
        return confident_nlu < self.component_config[MINIMUM_REQUIRED_KEY], confident_nlu

    def _nlu_forecast_ambiguous(
        self, message: Msg
    ) -> Tuple[bool, Optional[float]]:
        intentions = message.data.get(KEY_INTENT_RANKING, [])
        if len(intentions) >= 2:
            initial_confidence = intentions[0].get(KEY_PREDICTED_CONFIDENCE, 1.0)
            secondary_confidence = intentions[1].get(KEY_PREDICTED_CONFIDENCE, 1.0)
            diff = initial_confidence - secondary_confidence
            return (
                diff < self.component_config[AMBIGUITY_MINIMUM_REQUIRED_KEY],
                diff,
            )
        return False, None


def _intent_fallback() -> Dict[Text, Union[Text, float]]:
    return {
        KEY_INTENT_NAME: DEFAULT_NLU_FALLBACK_INTENTS_NAME,
        # TODO: Re-consider how we represent the confidence here
        KEY_PREDICTED_CONFIDENCE: 1.0,
    }
