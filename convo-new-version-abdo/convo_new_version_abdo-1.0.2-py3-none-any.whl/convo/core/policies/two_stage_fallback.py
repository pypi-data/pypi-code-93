import logging
from typing import List, Text, Optional, Any, TYPE_CHECKING, Dict

from convo.shared.core.events import UserUttered, ActionExecuted

from convo.shared.nlu.interpreter import NaturalLangInterpreter
from convo.core.policies.fallback import PolicyFallback
from convo.core.policies.policy import confidence_scores_for
from convo.shared.core.trackers import DialogueStateTracer
from convo.core.constants import (
    FALLBACK_POLICY_PREFERENCE,
    BY_DEFAULT_NLU_FALL_BACK_THRESHOLD,
    BY_DEFAULT_CORE_FALL_BACK_THRESHOLD,
    BY_DEFAULT_NLU_FALL_BACK_AMBIGUITY_THRESHOLD,
)
from convo.shared.core.constants import (
    USERS_INTENT_OUT_OF_SCOPE  ,
    LISTEN_ACTION_NAME  ,
    ACTION_DEFAULT_FALLBACK_NAME,
    REVERT_FALLBACK_EVENTS_ACTION_NAME   ,
    DEFAULT_ASK_AFFIRMATION_ACTION_NAME   ,
    DEFAULT_ASK_REPHRASE_ACTION_NAME   ,
)
from convo.shared.core.domain import InvalidDomain, Domain
from convo.shared.nlu.constants import ACT_NAME, KEY_INTENT_NAME

if TYPE_CHECKING:
    from convo.core.policies.ensemble import EnsemblePolicy


log = logging.getLogger(__name__)


def had_user_recast(tracker: DialogueStateTracer) -> bool:
    return tracker.last_executed_action_has(DEFAULT_ASK_REPHRASE_ACTION_NAME   )


class TwoStageFallbackPolicy(PolicyFallback):
    """This policy handles low NLU confidence in multiple stages.

    If a NLU prediction has a low confidence score,
    the user is asked to affirm whether they really had this intent.
    If they affirm, the story continues as if the intent was classified
    with high confidence from the beginning.
    If they deny, the user is asked to rephrase his intent.
    If the classification for the rephrased intent was confident, the story
    continues as if the user had this intent from the beginning.
    If the rephrased intent was not classified with high confidence,
    the user is asked to affirm the classified intent.
    If the user affirm the intent, the story continues as if the user had
    this intent from the beginning.
    If the user denies, an ultimate fallback action is triggered
    (e.g. a hand-off to a human).
    """

    def __init__(
        self,
        priority: int = FALLBACK_POLICY_PREFERENCE,
        nlu_threshold: float = BY_DEFAULT_NLU_FALL_BACK_THRESHOLD,
        ambiguity_threshold: float = BY_DEFAULT_NLU_FALL_BACK_AMBIGUITY_THRESHOLD,
        core_threshold: float = BY_DEFAULT_CORE_FALL_BACK_THRESHOLD,
        fallback_core_action_name: Text = ACTION_DEFAULT_FALLBACK_NAME,
        fallback_nlu_action_name: Text = ACTION_DEFAULT_FALLBACK_NAME,
        deny_suggestion_name_of_intent: Text = USERS_INTENT_OUT_OF_SCOPE  ,
    ) -> None:
        """Create a new Two-stage Fallback policy.

        Args:
            nlu_threshold: minimum threshold for NLU confidence.
                If intent prediction confidence is lower than this,
                predict fallback action with confidence 1.0.
            ambiguity_threshold: threshold for minimum difference
                between confidences of the top two predictions
            core_threshold: if NLU confidence threshold is met,
                predict fallback action with confidence
                `core_threshold`. If this is the highest confidence in
                the ensemble, the fallback action will be executed.
            fallback_core_action_name: This action is executed if the Core
                threshold is not met.
            fallback_nlu_action_name: This action is executed if the user
                denies the recognised intent for the second time.
            deny_suggestion_name_of_intent: The name of the intent which is used
                 to detect that the user denies the suggested convo_intents.
        """
        super().__init__(
            priority,
            nlu_threshold,
            ambiguity_threshold,
            core_threshold,
            fallback_core_action_name,
        )

        self.fallback_nlu_action_name = fallback_nlu_action_name
        self.deny_suggestion_name_of_intent = deny_suggestion_name_of_intent

    @classmethod
    def validate_against_domain(
        cls, ensemble: Optional["EnsemblePolicy"], domain: Optional[Domain]
    ) -> None:
        if ensemble is None:
            return

        for p in ensemble.policies:
            if not isinstance(p, TwoStageFallbackPolicy):
                continue
            if domain is None or p.deny_suggestion_name_of_intent not in domain.fetch_intents:
                raise InvalidDomain(
                    "The intent '{0}' must be present in the "
                    "domain file to use TwoStageFallbackPolicy. "
                    "Either include the intent '{0}' in your domain "
                    "or exclude the TwoStageFallbackPolicy from your "
                    "policy configuration".format(p.deny_suggestion_name_of_intent)
                )

    def predict_action_probabilities(
        self,
        tracker: DialogueStateTracer,
        domain: Domain,
        interpreter: NaturalLangInterpreter,
        **kwargs: Any,
    ) -> List[float]:
        """Predicts the next action if NLU confidence is low."""

        nlu_data_set = tracker.latest_message.parse_data
        end_intent_name = nlu_data_set["intent"].get(KEY_INTENT_NAME, None)
        shall_nlu_fallback = self.should_nlu_fallback(
            nlu_data_set, tracker.latest_action.get(ACT_NAME)
        )
        user_recast = had_user_recast(tracker)

        if self._is_user_expect_input(tracker):
            output = confidence_scores_for(LISTEN_ACTION_NAME  , 1.0, domain)
        elif self._had_user_refused(end_intent_name, tracker):
            log.debug(f"User '{tracker.sender_id}' denied suggested convo_intents.")
            output = self._results_for_user_refused(tracker, domain)
        elif user_recast and shall_nlu_fallback:
            log.debug(
                "Ambiguous rephrasing of user '{}' "
                "for intent '{}'".format(tracker.sender_id, end_intent_name)
            )
            output = confidence_scores_for(
                DEFAULT_ASK_AFFIRMATION_ACTION_NAME   , 1.0, domain
            )
        elif user_recast:
            log.debug(f"User '{tracker.sender_id}' rephrased intent")
            output = confidence_scores_for(
                REVERT_FALLBACK_EVENTS_ACTION_NAME   , 1.0, domain
            )
        elif tracker.last_executed_action_has(DEFAULT_ASK_AFFIRMATION_ACTION_NAME   ):
            if not shall_nlu_fallback:
                log.debug(
                    "User '{}' affirmed intent '{}'"
                    "".format(tracker.sender_id, end_intent_name)
                )
                output = confidence_scores_for(
                    REVERT_FALLBACK_EVENTS_ACTION_NAME   , 1.0, domain
                )
            else:
                output = confidence_scores_for(
                    self.fallback_nlu_action_name, 1.0, domain
                )
        elif shall_nlu_fallback:
            log.debug(
                "User '{}' has to affirm intent '{}'.".format(
                    tracker.sender_id, end_intent_name
                )
            )
            output = confidence_scores_for(
                DEFAULT_ASK_AFFIRMATION_ACTION_NAME   , 1.0, domain
            )
        else:
            log.debug(
                "NLU confidence threshold met, confidence of "
                "fallback action set to core threshold ({}).".format(
                    self.core_threshold
                )
            )
            output = self.fallback_scores(domain, self.core_threshold)

        return output

    def _is_user_expect_input(self, tracker: DialogueStateTracer) -> bool:
        act_needs_input = tracker.latest_action.get(ACT_NAME) in [
            DEFAULT_ASK_AFFIRMATION_ACTION_NAME   ,
            DEFAULT_ASK_REPHRASE_ACTION_NAME   ,
            self.fallback_action_name,
        ]
        try:
            end_utterance_time = tracker.get_last_event_for(UserUttered).timestamp
            end_act_time = tracker.get_last_event_for(ActionExecuted).timestamp
            input_granted = end_act_time < end_utterance_time
        except AttributeError:
            input_granted = False

        return act_needs_input and not input_granted

    def _had_user_refused(
        self, last_intent: Text, tracker: DialogueStateTracer
    ) -> bool:
        return (
            tracker.last_executed_action_has(DEFAULT_ASK_AFFIRMATION_ACTION_NAME   )
            and last_intent == self.deny_suggestion_name_of_intent
        )

    def _results_for_user_refused(
        self, tracker: DialogueStateTracer, domain: Domain
    ) -> List[float]:
        have_rejected_before = tracker.last_executed_action_has(
            DEFAULT_ASK_REPHRASE_ACTION_NAME   , skip=1
        )

        if have_rejected_before:
            return confidence_scores_for(self.fallback_nlu_action_name, 1.0, domain)
        else:
            return confidence_scores_for(DEFAULT_ASK_REPHRASE_ACTION_NAME   , 1.0, domain)

    def _meta_data_set(self) -> Dict[Text, Any]:
        return {
            "priority": self.priority,
            "nlu_threshold": self.nlu_threshold,
            "ambiguity_threshold": self.ambiguity_threshold,
            "core_threshold": self.core_threshold,
            "fallback_core_action_name": self.fallback_action_name,
            "fallback_nlu_action_name": self.fallback_nlu_action_name,
            "deny_suggestion_name_of_intent": self.deny_suggestion_name_of_intent,
        }

    @classmethod
    def _meta_data_set_file_name(cls) -> Text:
        return "two_stage_fallback_policy.json"
