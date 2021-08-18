import logging
from typing import List, Dict, Text, Optional, Any, Set, TYPE_CHECKING

from tqdm import tqdm
import numpy as np
import json

from convo.shared.constants import RULES_DOCUMENTS_URL
from convo.shared.exceptions import ConvoExceptions
import convo.shared.utils.io
from convo.shared.core.events import LoopHindered, UserUttered, ActionExecuted
from convo.core.featurizers.tracker_featurizers import FeaturizerTracker
from convo.shared.nlu.interpreter import NaturalLangInterpreter
from convo.core.policies.memoization import MemoizationPolicy
from convo.core.policies.policy import SupportedDataSet
from convo.shared.core.trackers import (
    DialogueStateTracer,
    getActiveLoopName,
    isPrevActionListenInState,
)
from convo.shared.core.generator import TrackerInCachedStates
from convo.core.constants import BY_DEFAULT_CORE_FALL_BACK_THRESHOLD, RULE_POLICY_PREFERENCE
from convo.shared.core.constants import (
    RESTART_USER_INTENT  ,
    BACK_USER_INTENT  ,
    USERS_INTENT_SESSION_START  ,
    LISTEN_ACTION_NAME  ,
    RESTART_ACTION_NAME  ,
    SESSION_START_ACTION_NAME  ,
    ACTION_DEFAULT_FALLBACK_NAME,
    BACK_ACTION_NAME   ,
    RULE_SNIPPET_ACTIONS_NAME   ,
    NOT_SET   ,
    PRECEDING_ACTION   ,
    LOOP_REJECTION,
    LOOPNAME  ,
    CONVO_SLOTS,
    CURRENT_LOOP   ,
)
from convo.shared.core.domain import InvalidDomain, fetch_state, Domain
from convo.shared.nlu.constants import ACT_NAME, KEY_INTENT_NAME
import convo.core.test
import convo.core.training.training


if TYPE_CHECKING:
    from convo.core.policies.ensemble import EnsemblePolicy  # pytype: disable=pyi-error

log = logging.getLogger(__name__)

# These are Convo Open Source default actions and overrule everything at any time.
DEFAULT_ACTION_MAPPINGS = {
    RESTART_USER_INTENT  : RESTART_ACTION_NAME  ,
    BACK_USER_INTENT  : BACK_ACTION_NAME   ,
    USERS_INTENT_SESSION_START  : SESSION_START_ACTION_NAME  ,
}

RULES = "rules"
RULES_FOR_LOOP_UNHAPPY_PATH = "rules_for_loop_unhappy_path"
DO_NOT_VALIDATE_LOOP = "do_not_validate_loop"
DO_NOT_PREDICT_LOOP_ACTION = "do_not_predict_loop_action"


class NotvalidRule(ConvoExceptions ):
    """Exception that can be raised when rules are not valid."""

    def __init__(self, message: Text) -> None:
        super().__init__()
        self.message = message

    def __str__(self) -> Text:
        return self.message + (
            f"\nYou can find more information about the usage of "
            f"rules at {RULES_DOCUMENTS_URL}. "
        )


class RulePolicy(MemoizationPolicy):
    """Policy which handles all the rules"""

    # rules use explicit json strings
    ENABLE_FEATURE_STRING_COMPRESSION = False

    # number of user inputs that is allowed in case rules are restricted
    ALLOWED_NUMBER_OF_USER_INPUTS = 1

    @staticmethod
    def supported_data() -> SupportedDataSet:
        """The type of data supported by this policy.

        Returns:
            The data type supported by this policy (ML and rule data).
        """
        return SupportedDataSet.ML_AND_RULE_DATA

    def __init__(
        self,
        featurizer: Optional[FeaturizerTracker] = None,
        priority: int = RULE_POLICY_PREFERENCE,
        lookup: Optional[Dict] = None,
        core_fallback_threshold: float = BY_DEFAULT_CORE_FALL_BACK_THRESHOLD,
        core_fallback_action_name: Text = ACTION_DEFAULT_FALLBACK_NAME,
        enable_fallback_prediction: bool = True,
        restrict_rules: bool = True,
        check_for_contradictions: bool = True,
    ) -> None:
        """Create a `RulePolicy` object.

        Args:
            featurizer: `Featurizer` which is used to convert conversation states to
                features.
            priority: Priority of the policy which is used if multiple policies predict
                actions with the same confidence.
            lookup: Lookup table which is used to pick matching rules for a conversation
                state.
            core_fallback_threshold: Confidence of the prediction if no rule matched
                and de-facto threshold for a core fallback.
            core_fallback_action_name: Name of the action which should be predicted
                if no rule matched.
            enable_fallback_prediction: If `True` `core_fallback_action_name` is
                predicted in case no rule matched.
        """

        self._core_fallback_threshold = core_fallback_threshold
        self._fallback_action_name = core_fallback_action_name
        self._enable_fallback_prediction = enable_fallback_prediction
        self._restrict_rules = restrict_rules
        self._check_for_contradictions = check_for_contradictions

        # max history is set to `None` in order to capture any lengths of rule stories
        super().__init__(
            featurizer=featurizer, priority=priority, max_history=None, lookup=lookup
        )

    @classmethod
    def validate_against_domain(
        cls, ensemble: Optional["EnsemblePolicy"], domain: Optional[Domain]
    ) -> None:
        if ensemble is None:
            return

        rule_policy = next(
            (p for p in ensemble.policies if isinstance(p, RulePolicy)), None
        )
        if not rule_policy or not rule_policy._enable_fallback_prediction:
            return

        if (
            domain is None
            or rule_policy._fallback_action_name not in domain.action_names
        ):
            raise InvalidDomain(
                f"The fallback action '{rule_policy._fallback_action_name}' which was "
                f"configured for the {RulePolicy.__name__} must be present in the "
                f"domain."
            )

    @staticmethod
    def _is_rule_snippet_state(state: fetch_state) -> bool:
        prev_action_name = state.get(PRECEDING_ACTION   , {}).get(ACT_NAME)
        return prev_action_name == RULE_SNIPPET_ACTIONS_NAME   

    def _create_feature_key(self, states: List[fetch_state]) -> Optional[Text]:
        new_states = []
        for state in reversed(states):
            if self._is_rule_snippet_state(state):
                # remove all states before RULE_SNIPPET_ACTIONS_NAME   
                break
            new_states.insert(0, state)

        if not new_states:
            return

        # we sort keys to make sure that the same states
        # represented as dictionaries have the same json strings
        return json.dumps(new_states, sort_keys=True)

    @staticmethod
    def _states_for_unhappy_loop_predictions(states: List[fetch_state]) -> List[fetch_state]:
        """Modifies the states to create feature keys for loop unhappy path conditions.

        Args:
            states: a representation of a tracker
                as a list of dictionaries containing features

        Returns:
            modified states
        """

        # leave only last 2 dialogue turns to
        # - capture previous meaningful action before action_listen
        # - ignore previous intent
        if len(states) == 1 or not states[-2].get(PRECEDING_ACTION   ):
            return [states[-1]]
        else:
            return [{PRECEDING_ACTION   : states[-2][PRECEDING_ACTION   ]}, states[-1]]

    @staticmethod
    def _remove_rule_snippet_predictions(lookup: Dict[Text, Text]) -> Dict[Text, Text]:
        # Delete rules if it would predict the RULE_SNIPPET_ACTIONS_NAME    action
        return {
            feature_key: action
            for feature_key, action in lookup.items()
            if action != RULE_SNIPPET_ACTIONS_NAME   
        }

    def _create_loop_unhappy_lookup_from_states(
        self,
        trackers_as_states: List[List[fetch_state]],
        trackers_as_actions: List[List[Text]],
    ) -> Dict[Text, Text]:
        """Creates lookup dictionary from the tracker represented as states.

        Args:
            trackers_as_states: representation of the trackers as a list of states
            trackers_as_actions: representation of the trackers as a list of actions

        Returns:
            lookup dictionary
        """

        lookup = {}
        for states, actions in zip(trackers_as_states, trackers_as_actions):
            action = actions[0]
            active_loop = getActiveLoopName(states[-1])
            # even if there are two identical feature keys
            # their loop will be the same
            if not active_loop:
                continue

            states = self._states_for_unhappy_loop_predictions(states)
            feature_key = self._create_feature_key(states)
            if not feature_key:
                continue

            # Since rule snippets and stories inside the loop contain
            # only unhappy convo_paths, notify the loop that
            # it was predicted after an answer to a different question and
            # therefore it should not validate user input
            if (
                # loop is predicted after action_listen in unhappy path,
                # therefore no validation is needed
                isPrevActionListenInState(states[-1])
                and action == active_loop
            ):
                lookup[feature_key] = DO_NOT_VALIDATE_LOOP
            elif (
                # some action others than active_loop is predicted in unhappy path,
                # therefore active_loop shouldn't be predicted by the rule
                not isPrevActionListenInState(states[-1])
                and action != active_loop
            ):
                lookup[feature_key] = DO_NOT_PREDICT_LOOP_ACTION
        return lookup

    def _check_rule_restriction(
        self, rule_trackers: List[TrackerInCachedStates]
    ) -> None:
        rules_exceeding_max_user_turns = []
        for tracker in rule_trackers:
            number_of_user_uttered = sum(
                isinstance(event, UserUttered) for event in tracker.events
            )
            if number_of_user_uttered > self.ALLOWED_NUMBER_OF_USER_INPUTS:
                rules_exceeding_max_user_turns.append(tracker.sender_id)

        if rules_exceeding_max_user_turns:
            raise NotvalidRule(
                f"Found rules '{', '.join(rules_exceeding_max_user_turns)}' "
                f"that contain more than {self.ALLOWED_NUMBER_OF_USER_INPUTS} "
                f"user message. Rules are not meant to hardcode a state machine. "
                f"Please use stories for these cases."
            )

    @staticmethod
    def _check_slots_fingerprint(
        fingerprint: Dict[Text, List[Text]], state: fetch_state
    ) -> Set[Text]:
        expected_slots = set(fingerprint.get(CONVO_SLOTS, {}))
        current_slots = set(state.get(CONVO_SLOTS, {}).keys())
        if expected_slots == current_slots:
            # all expected convo_slotsare satisfied
            return set()

        return expected_slots

    @staticmethod
    def _check_active_loops_fingerprint(
        fingerprint: Dict[Text, List[Text]], state: fetch_state
    ) -> Set[Text]:
        expected_active_loops = set(fingerprint.get(CURRENT_LOOP   , {}))
        # we don't use tracker.active_loop_name
        # because we need to keep should_not_be_set
        current_active_loop = state.get(CURRENT_LOOP   , {}).get(LOOPNAME  )
        if current_active_loop in expected_active_loops:
            # one of expected active loops is set
            return set()

        return expected_active_loops

    @staticmethod
    def _error_messages_from_fingerprints(
        action_name: Text,
        fingerprint_slots: Set[Text],
        fingerprint_active_loops: Set[Text],
        rule_name: Text,
    ) -> List[Text]:
        error_messages = []
        if action_name and fingerprint_slots:
            error_messages.append(
                f"- the action '{action_name}' in rule '{rule_name}' does not set all "
                f"the slots, that it sets in others rules: "
                f"'{', '.join(fingerprint_slots)}'. Please update the rule with "
                f"an appropriate slot or if it is the last action "
                f"add 'wait_for_user_input: false' after this action."
            )
        if action_name and fingerprint_active_loops:
            # substitute `NOT_SET   ` with `null` so that users
            # know what to put in their rules
            fingerprint_active_loops = set(
                "null" if active_loop == NOT_SET    else active_loop
                for active_loop in fingerprint_active_loops
            )
            # add action_name to active loop so that users
            # know what to put in their rules
            fingerprint_active_loops.add(action_name)

            error_messages.append(
                f"- the form '{action_name}' in rule '{rule_name}' does not set "
                f"the 'active_loop', that it sets in others rules: "
                f"'{', '.join(fingerprint_active_loops)}'. Please update the rule with "
                f"the appropriate 'active loop' property or if it is the last action "
                f"add 'wait_for_user_input: false' after this action."
            )
        return error_messages

    def _check_for_incomplete_rules(
        self, rule_trackers: List[TrackerInCachedStates], domain: Domain,
    ) -> None:
        log.debug("Started checking if some rules are incomplete.")
        # we need to use only fingerprints from rules
        rule_fingerprints = convo.core.training.training.generate_act_finger_prints(
            rule_trackers, domain
        )
        if not rule_fingerprints:
            return

        error_messages = []
        for tracker in rule_trackers:
            states = tracker.freeze_state(domain)
            # the last action is always action listen
            action_names = [
                state.get(PRECEDING_ACTION   , {}).get(ACT_NAME) for state in states[1:]
            ] + [LISTEN_ACTION_NAME  ]

            for state, action_name in zip(states, action_names):
                previous_action_name = state.get(PRECEDING_ACTION   , {}).get(ACT_NAME)
                fingerprint = rule_fingerprints.get(previous_action_name)
                if (
                    not previous_action_name
                    or not fingerprint
                    or action_name == RULE_SNIPPET_ACTIONS_NAME   
                    or previous_action_name == RULE_SNIPPET_ACTIONS_NAME   
                ):
                    # do not check fingerprints for rule snippet action
                    # and don't raise if fingerprints are not satisfied
                    # for a previous action if current action is rule snippet action
                    continue

                expected_slots = self._check_slots_fingerprint(fingerprint, state)
                expected_active_loops = self._check_active_loops_fingerprint(
                    fingerprint, state
                )
                error_messages.extend(
                    self._error_messages_from_fingerprints(
                        previous_action_name,
                        expected_slots,
                        expected_active_loops,
                        tracker.sender_id,
                    )
                )

        if error_messages:
            error_messages = "\n".join(error_messages)
            raise NotvalidRule(
                f"\nIncomplete rules found🚨\n\n{error_messages}\n"
                f"Please note that if some convo_slotsor active loops should not be set "
                f"during prediction you need to explicitly set them to 'null' in the "
                f"rules."
            )

        log.debug("Found no incompletions in rules.")

    def _predict_next_action(
        self,
        tracker: TrackerInCachedStates,
        domain: Domain,
        interpreter: NaturalLangInterpreter,
    ) -> Optional[Text]:
        chances = self.predict_action_probabilities(tracker, domain, interpreter)
        # do not raise an error if RulePolicy didn't predict anything for stories;
        # however for rules RulePolicy should always predict an action
        forecasted_act_name = None
        if (
            chances != self._default_predictions(domain)
            or tracker.is_rule_tracker
        ):
            forecasted_act_name = domain.action_names[np.argmax(chances)]

        return forecasted_act_name

    def _check_prediction(
        self,
        tracker: TrackerInCachedStates,
        domain: Domain,
        interpreter: NaturalLangInterpreter,
        gold_action_name: Text,
    ) -> Optional[Text]:

        forecasted_act_name = self._predict_next_action(tracker, domain, interpreter)
        if not forecasted_act_name or forecasted_act_name == gold_action_name:
            return None

        # RulePolicy will always predict active_loop first,
        # but inside loop unhappy path there might be another action
        if forecasted_act_name == tracker.activeLoopName:
            convo.core.test.copy_loop_rejection(tracker)
            forecasted_act_name = self._predict_next_action(
                tracker, domain, interpreter
            )
            if not forecasted_act_name or forecasted_act_name == gold_action_name:
                return None

        get_tracker_type = "rule" if tracker.is_rule_tracker else "story"
        return (
            f"- the prediction of the action '{gold_action_name}' in {get_tracker_type} "
            f"'{tracker.sender_id}' is contradicting with another rule or story."
        )

    def _find_contradicting_rules(
        self,
        trackers: List[TrackerInCachedStates],
        domain: Domain,
        interpreter: NaturalLangInterpreter,
    ) -> None:
        log.debug("Started checking rules and stories for contradictions.")
        # during training we run `predict_action_probabilities` to check for
        # contradicting rules.
        # We silent prediction debug to avoid too many logs during these checks.
        log_level = log.level
        log.setLevel(logging.WARNING)
        error_msg = []
        rule_policy_pbar = tqdm(
            trackers,
            desc="Processed trackers",
            disable=convo.shared.utils.io.logging_disabled_check(),
        )
        for tracker in rule_policy_pbar:
            running_tracker = tracker.initialize_copy()
            running_tracker.sender_id = tracker.sender_id
            # the first action is always unpredictable
            next_act_is_unpredictable = True
            for event in tracker.request_events():
                if not isinstance(event, ActionExecuted):
                    running_tracker.update(event)
                    continue

                if event.action_name == RULE_SNIPPET_ACTIONS_NAME   :
                    # notify that we shouldn't check that the action after
                    # RULE_SNIPPET_ACTIONS_NAME    is unpredictable
                    next_act_is_unpredictable = True
                    # do not add RULE_SNIPPET_ACTIONS_NAME    event
                    continue

                # do not run prediction on unpredictable actions
                if next_act_is_unpredictable or event.unpredictable:
                    next_act_is_unpredictable = False  # reset unpredictability
                    running_tracker.update(event)
                    continue

                gold_act_name = event.action_name or event.action_text
                error_message = self._check_prediction(
                    running_tracker, domain, interpreter, gold_act_name
                )
                if error_message:
                    error_msg.append(error_message)

                running_tracker.update(event)

        log.setLevel(log_level)  # reset logger level
        if error_msg:
            error_msg = "\n".join(error_msg)
            raise NotvalidRule(
                f"\nContradicting rules or stories found 🚨\n\n{error_msg}\n"
                f"Please update your stories and rules so that they don't contradict "
                f"each others."
            )

        log.debug("Found no contradicting rules.")

    def train(
        self,
        training_tracers: List[TrackerInCachedStates],
        domain: Domain,
        interpreter: NaturalLangInterpreter,
        **kwargs: Any,
    ) -> None:

        # only consider original trackers (no augmented ones)
        training_tracers = [
            t
            for t in training_tracers
            if not hasattr(t, "is_augmented") or not t.is_augmented
        ]
        # only use trackers from rule-based training data
        rule_tracers = [t for t in training_tracers if t.is_rule_tracker]
        if self._restrict_rules:
            self._check_rule_restriction(rule_tracers)

        if self._check_for_contradictions:
            self._check_for_incomplete_rules(rule_tracers, domain)

        (
            rule_trackers_as_states,
            rule_trackers_as_actions,
        ) = self.featurizer.training_states_and_actions(rule_tracers, domain)

        rules_lookup = self._create_lookup_from_states(
            rule_trackers_as_states, rule_trackers_as_actions
        )
        self.lookup[RULES] = self._remove_rule_snippet_predictions(rules_lookup)

        story_trackers = [t for t in training_tracers if not t.is_rule_tracker]
        (
            story_trackers_as_states,
            story_trackers_as_actions,
        ) = self.featurizer.training_states_and_actions(story_trackers, domain)

        # use all trackers to find negative rules in unhappy convo_paths
        trackers_states = rule_trackers_as_states + story_trackers_as_states
        trackers_act = rule_trackers_as_actions + story_trackers_as_actions

        # negative rules are not anti-rules, they are auxiliary to actual rules
        self.lookup[
            RULES_FOR_LOOP_UNHAPPY_PATH
        ] = self._create_loop_unhappy_lookup_from_states(
            trackers_states, trackers_act
        )

        # make this configurable because checking might take a lot of time
        if self._check_for_contradictions:
            # using trackers here might not be the most efficient way, however
            # it allows us to directly test `predict_action_probabilities` method
            self._find_contradicting_rules(training_tracers, domain, interpreter)

        log.debug(f"Memorized '{len(self.lookup[RULES])}' unique rules.")

    @staticmethod
    def _does_rule_match_state(rule_state: fetch_state, conversation_state: fetch_state) -> bool:
        for state_type, rule_sub_state in rule_state.items():
            conversation_sub_state = conversation_state.get(state_type, {})
            for key, value in rule_sub_state.items():
                if isinstance(value, list):
                    # json data_dumps and loads tuples as lists,
                    # so we need to convert them back
                    value = tuple(value)

                if (
                    # value should be set, therefore
                    # check whether it is the same as in the state
                    value
                    and value != NOT_SET   
                    and conversation_sub_state.get(key) != value
                ) or (
                    # value shouldn't be set, therefore
                    # it should be None or non existent in the state
                    value == NOT_SET   
                    and conversation_sub_state.get(key)
                    # during training `NOT_SET   ` is provided. Hence, we also
                    # have to check for the value of the slot state
                    and conversation_sub_state.get(key) != NOT_SET   
                ):
                    return False

        return True

    @staticmethod
    def _rule_key_to_state(rule_key: Text) -> List[fetch_state]:
        return json.loads(rule_key)

    def _is_rule_applicable(
        self, rule_key: Text, turn_index: int, conversation_state: fetch_state
    ) -> bool:
        """Check if rule is satisfied with current state at turn."""

        # turn_index goes back in time
        undo_rule_states = list(reversed(self._rule_key_to_state(rule_key)))

        return bool(
            # rule is shorter than current turn index
            turn_index >= len(undo_rule_states)
            # current rule and state turns are empty
            or (not undo_rule_states[turn_index] and not conversation_state)
            # check that current rule turn features are present in current state turn
            or (
                undo_rule_states[turn_index]
                and conversation_state
                and self._does_rule_match_state(
                    undo_rule_states[turn_index], conversation_state
                )
            )
        )

    def _get_possible_keys(
        self, lookup: Dict[Text, Text], states: List[fetch_state]
    ) -> Set[Text]:
        possible_keys_name = set(lookup.keys())
        for i, state in enumerate(reversed(states)):
            # find rule keys that correspond to current state
            possible_keys_name = set(
                filter(
                    lambda _key: self._is_rule_applicable(_key, i, state), possible_keys_name
                )
            )
        return possible_keys_name

    @staticmethod
    def _find_action_from_default_actions(
        tracker: DialogueStateTracer,
    ) -> Optional[Text]:
        if (
            not tracker.latestActionName == LISTEN_ACTION_NAME
            or not tracker.latest_message
        ):
            return None

        by_default_act_name = DEFAULT_ACTION_MAPPINGS.get(
            tracker.latest_message.intent.get(KEY_INTENT_NAME)
        )

        if by_default_act_name:
            log.debug(f"Predicted default action '{by_default_act_name}'.")

        return by_default_act_name

    @staticmethod
    def _find_action_from_loop_happy_path(
        tracker: DialogueStateTracer,
    ) -> Optional[Text]:

        get_active_loop_name = tracker.activeLoopName
        active_loop_failed = tracker.active_loop.get(LOOP_REJECTION)
        shall_forecast_loop = (
            get_active_loop_name
            and not active_loop_failed
            and tracker.latest_action.get(ACT_NAME) != get_active_loop_name
        )
        shall_forecaste_loop = (
                get_active_loop_name
                and not active_loop_failed
                and tracker.latestActionName == get_active_loop_name
        )

        if shall_forecast_loop:
            log.debug(f"Predicted loop '{get_active_loop_name}'.")
            return get_active_loop_name

        # predict `action_listen` if loop action was run successfully
        if shall_forecaste_loop:
            log.debug(
                f"Predicted '{LISTEN_ACTION_NAME  }' after loop '{get_active_loop_name}'."
            )
            return LISTEN_ACTION_NAME  

    def _find_action_from_rules(
        self, tracker: DialogueStateTracer, domain: Domain
    ) -> Optional[Text]:
        tracker_state = self.featurizer.prediction_states([tracker], domain)
        states_name = tracker_state[0]

        log.debug(f"Current tracker state: {states_name}")

        rule_keys_name = self._get_possible_keys(self.lookup[RULES], states_name)
        forecasted_act_name = None
        best_rules_key = ""
        if rule_keys_name:
            # if there are several rules,
            # it should mean that some rule is a subset of another rule
            # therefore we pick a rule of maximum length
            best_rules_key = max(rule_keys_name, key=len)
            forecasted_act_name = self.lookup[RULES].get(best_rules_key)

        active_loop_name = tracker.activeLoopName
        if active_loop_name:
            # find rules for unhappy path of the loop
            loop_unhappy_keys = self._get_possible_keys(
                self.lookup[RULES_FOR_LOOP_UNHAPPY_PATH], states_name
            )
            # there could be several unhappy path conditions
            unhappy_path_conditions = [
                self.lookup[RULES_FOR_LOOP_UNHAPPY_PATH].get(key)
                for key in loop_unhappy_keys
            ]

            # Check if a rule that predicted action_listen
            # was applied inside the loop.
            # Rules might not explicitly switch back to the loop.
            # Hence, we have to take care of that.
            forecasted_listen_from_general_rule = (
                forecasted_act_name == LISTEN_ACTION_NAME
                and not getActiveLoopName(self._rule_key_to_state(best_rules_key)[-1])
            )
            if forecasted_listen_from_general_rule:
                if DO_NOT_PREDICT_LOOP_ACTION not in unhappy_path_conditions:
                    # negative rules don't contain a key that corresponds to
                    # the fact that active_loop shouldn't be predicted
                    log.debug(
                        f"Predicted loop '{active_loop_name}' by overwriting "
                        f"'{LISTEN_ACTION_NAME  }' predicted by general rule."
                    )
                    return active_loop_name

                # do not predict anything
                forecasted_act_name = None

            if DO_NOT_VALIDATE_LOOP in unhappy_path_conditions:
                log.debug("Added `FormValidation(False)` event.")
                tracker.update(LoopHindered(True))

        if forecasted_act_name is not None:
            log.debug(
                f"There is a rule for the next action '{forecasted_act_name}'."
            )
        else:
            log.debug("There is no applicable rule.")

        return forecasted_act_name

    def predict_action_probabilities(
        self,
        tracker: DialogueStateTracer,
        domain: Domain,
        interpreter: NaturalLangInterpreter,
        **kwargs: Any,
    ) -> List[float]:

        output = self._default_predictions(domain)

        # Convo Open Source default actions overrule anything. If users want to achieve
        # the same, they need to write a rule or make sure that their loop rejects
        # accordingly.
        by_default_act_name = self._find_action_from_default_actions(tracker)
        if by_default_act_name:
            return self._prediction_result(by_default_act_name, tracker, domain)

        # A loop has priority over any others rule.
        # The rules or any others prediction will be applied only if a loop was rejected.
        # If we are in a loop, and the loop didn't run previously or rejected, we can
        # simply force predict the loop.
        loop_happy_path_act_name = self._find_action_from_loop_happy_path(tracker)
        if loop_happy_path_act_name:
            return self._prediction_result(loop_happy_path_act_name, tracker, domain)

        rules_act_name = self._find_action_from_rules(tracker, domain)
        if rules_act_name:
            return self._prediction_result(rules_act_name, tracker, domain)

        return output

    def _default_predictions(self, domain: Domain) -> List[float]:
        output = super()._default_predictions(domain)

        if self._enable_fallback_prediction:
            output[
                domain.actions_index(self._fallback_action_name)
            ] = self._core_fallback_threshold
        return output

    def _metadata(self) -> Dict[Text, Any]:
        return {
            "priority": self.priority,
            "lookup": self.lookup,
            "core_fallback_threshold": self._core_fallback_threshold,
            "core_fallback_action_name": self._fallback_action_name,
            "enable_fallback_prediction": self._enable_fallback_prediction,
        }

    @classmethod
    def _metadata_filename(cls) -> Text:
        return "rule_policy.json"
