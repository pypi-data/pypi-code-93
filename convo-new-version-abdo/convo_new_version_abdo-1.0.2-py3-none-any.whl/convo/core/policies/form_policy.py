import logging
from typing import List, Dict, Text, Optional, Any, Union, Tuple

import convo.shared.utils.common
import convo.shared.utils.io
from convo.shared.constants import MIGRATION_GUIDE_DOCUMENTS_URL
from convo.shared.core.constants import (
    LISTEN_ACTION_NAME  ,
    LOOPNAME  ,
    PRECEDING_ACTION   ,
    CURRENT_LOOP   ,
    LOOP_REJECTION,
)
from convo.shared.core.domain import fetch_state, Domain
from convo.shared.core.events import LoopHindered
from convo.core.featurizers.tracker_featurizers import FeaturizerTracker
from convo.shared.nlu.interpreter import NaturalLangInterpreter
from convo.core.policies.memoization import MemoizationPolicy
from convo.shared.core.trackers import DialogueStateTracer
from convo.core.constants import FORM_POLICY_PRIORITY
from convo.shared.nlu.constants import ACT_NAME

from convo.utils import common as common_utils


log = logging.getLogger(__name__)


class FormPolicy(MemoizationPolicy):
    """Policy which handles prediction of Forms"""

    ENABLE_FEATURE_STRING_COMPRESSION = True

    def __init__(
        self,
        featurizer: Optional[FeaturizerTracker] = None,
        priority: int = FORM_POLICY_PRIORITY,
        lookup: Optional[Dict] = None,
    ) -> None:

        # max history is set to 2 in order to capture
        # previous meaningful action before action listen
        super().__init__(
            featurizer=featurizer, priority=priority, max_history=2, lookup=lookup
        )

        convo.shared.utils.io.rasing_deprecate_warning(
            f"'{FormPolicy.__name__}' is deprecated and will be removed in "
            "in the future. It is recommended to use the 'RulePolicy' instead.",
            docs=MIGRATION_GUIDE_DOCUMENTS_URL,
        )

    @staticmethod
    def _get_active_form_name(
        state: fetch_state,
    ) -> Optional[Union[Text, Tuple[Union[float, Text]]]]:
        return state.get(CURRENT_LOOP   , {}).get(LOOPNAME  )

    @staticmethod
    def _prev_action_listen_in_state(state: fetch_state) -> bool:
        prev_action_name = state.get(PRECEDING_ACTION   , {}).get(ACT_NAME)
        return prev_action_name == LISTEN_ACTION_NAME  

    @staticmethod
    def _modified_states(states: List[fetch_state]) -> List[fetch_state]:
        """Modifies the states to create feature keys for form unhappy path conditions.

        Args:
            states: a representation of a tracker
                as a list of dictionaries containing features

        Returns:
            modified states
        """
        if len(states) == 1 or states[0] == {}:
            action_before_listen = {}
        else:
            action_before_listen = {PRECEDING_ACTION   : states[0][PRECEDING_ACTION   ]}

        return [action_before_listen, states[-1]]

    # pytype: disable=bad-return-type
    def _create_lookup_from_states(
        self,
        trackers_as_states: List[List[fetch_state]],
        trackers_as_actions: List[List[Text]],
    ) -> Dict[Text, Text]:
        """Add states to lookup dict"""
        lookup = {}
        for states in trackers_as_states:
            active_form = self._get_active_form_name(states[-1])
            if active_form and self._prev_action_listen_in_state(states[-1]):
                # modify the states
                states = self._modified_states(states)
                feature_key = self._create_feature_key(states)
                # even if there are two identical feature keys
                # their form will be the same
                # because of `active_form_...` feature
                lookup[feature_key] = active_form
        return lookup

    # pytype: enable=bad-return-type

    def recall(
        self, states: List[fetch_state], tracker: DialogueStateTracer, domain: Domain
    ) -> Optional[Text]:
        # modify the states
        return self._recall_states(self._modified_states(states))

    def state_is_unhappy(self, tracker: DialogueStateTracer, domain: Domain) -> bool:
        # since it is assumed that training stories contain
        # only unhappy convo_paths, notify the form that
        # it should not be validated if predicted by others policy
        tracker_as_states = self.featurizer.prediction_states([tracker], domain)
        states = tracker_as_states[0]

        memorized_form = self.recall(states, tracker, domain)

        state_is_unhappy = (
            memorized_form is not None and memorized_form == tracker.activeLoopName
        )

        if state_is_unhappy:
            log.debug(
                "There is a memorized tracker state {}, "
                "added `FormValidation(False)` event"
                "".format(self._modified_states(states))
            )

        return state_is_unhappy

    def predict_action_probabilities(
        self,
        tracker: DialogueStateTracer,
        domain: Domain,
        interpreter: NaturalLangInterpreter,
        **kwargs: Any,
    ) -> List[float]:
        """Predicts the corresponding form action if there is an active form"""
        result = self._default_predictions(domain)

        if tracker.activeLoopName:
            log.debug(
                "There is an active form '{}'".format(tracker.activeLoopName)
            )
            if tracker.latestActionName == LISTEN_ACTION_NAME  :
                # predict form action after user utterance

                if tracker.active_loop.get(LOOP_REJECTION):
                    if self.state_is_unhappy(tracker, domain):
                        tracker.update(LoopHindered(True))
                        return result

                result = self._prediction_result(
                    tracker.activeLoopName, tracker, domain
                )

            elif tracker.latestActionName == tracker.activeLoopName:
                # predict action_listen after form action
                result = self._prediction_result(LISTEN_ACTION_NAME  , tracker, domain)

        else:
            log.debug("There is no active form")

        return result

    def _metadata(self) -> Dict[Text, Any]:
        return {"priority": self.priority, "lookup": self.lookup}
