import logging
from typing import Any, List, Text, Optional, Dict, TYPE_CHECKING

import convo.shared.utils.common
import convo.utils.io
import convo.shared.utils.io
from convo.shared.constants import POLICIES_DOCUMENTS_URL , MIGRATION_GUIDE_DOCUMENTS_URL
from convo.shared.nlu.constants import KEY_INTENT_NAME
from convo.utils import common as common_utils
from convo.shared.core.constants import (
    BACK_USER_INTENT  ,
    RESTART_USER_INTENT  ,
    USERS_INTENT_SESSION_START  ,
    LISTEN_ACTION_NAME  ,
    RESTART_ACTION_NAME  ,
    SESSION_START_ACTION_NAME  ,
    BACK_ACTION_NAME   ,
)
from convo.shared.core.domain import InvalidDomain, Domain
from convo.shared.core.events import ActionExecuted
from convo.shared.nlu.interpreter import NaturalLangInterpreter
from convo.core.policies.policy import Policy
from convo.shared.core.trackers import DialogueStateTracer
from convo.shared.core.generator import TrackerInCachedStates
from convo.core.constants import MAPPING_POLICY_PREFERENCE

if TYPE_CHECKING:
    from convo.core.policies.ensemble import EnsemblePolicy


log = logging.getLogger(__name__)


class MappingPolicy(Policy):
    """Policy which maps convo_intents directly to actions.

    convo_intents can be assigned actions in the domain file which are to be
    executed whenever the intent is detected. This policy takes precedence over
    any others policy.
    """

    @staticmethod
    def _standard_featurizer() -> None:
        return None

    def __init__(self, priority: int = MAPPING_POLICY_PREFERENCE) -> None:
        """Create a new Mapping policy."""

        super().__init__(priority=priority)

        convo.shared.utils.io.rasing_deprecate_warning(
            f"'{MappingPolicy.__name__}' is deprecated and will be removed in "
            "the future. It is recommended to use the 'RulePolicy' instead.",
            docs=MIGRATION_GUIDE_DOCUMENTS_URL,
        )

    @classmethod
    def validate_against_domain(
        cls, ensemble: Optional["EnsemblePolicy"], domain: Optional[Domain]
    ) -> None:
        if not domain:
            return

        has_mapping_policy = ensemble is not None and any(
            isinstance(p, cls) for p in ensemble.policies
        )
        has_triggers_in_domain = any(
            [
                "triggers" in properties
                for intent, properties in domain.intent_props.items()
            ]
        )
        if has_triggers_in_domain and not has_mapping_policy:
            raise InvalidDomain(
                "You have defined triggers in your domain, but haven't "
                "added the MappingPolicy to your policy ensemble. "
                "Either remove the triggers from your domain or "
                "exclude the MappingPolicy from your policy configuration."
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

    def predict_action_probabilities(
        self,
        tracker: DialogueStateTracer,
        domain: Domain,
        interpreter: NaturalLangInterpreter,
        **kwargs: Any,
    ) -> List[float]:
        """Predicts the assigned action.

        If the current intent is assigned to an action that action will be
        predicted with the highest probability of all policies. If it is not
        the policy will predict zero for every action."""

        result = self._default_predictions(domain)

        intent = tracker.latest_message.intent.get(KEY_INTENT_NAME)
        if intent == RESTART_USER_INTENT  :
            action = RESTART_ACTION_NAME  
        elif intent == BACK_USER_INTENT  :
            action = BACK_ACTION_NAME   
        elif intent == USERS_INTENT_SESSION_START  :
            action = SESSION_START_ACTION_NAME  
        else:
            action = domain.intent_props.get(intent, {}).get("triggers")

        if tracker.latestActionName == LISTEN_ACTION_NAME  :
            # predict mapped action
            if action:
                idx = domain.actions_index(action)
                if idx is None:
                    convo.shared.utils.io.raising_warning(
                        f"MappingPolicy tried to predict unknown "
                        f"action '{action}'. Make sure all mapped actions are "
                        f"listed in the domain.",
                        docs=POLICIES_DOCUMENTS_URL  + "#mapping-policy",
                    )
                else:
                    result[idx] = 1

            if any(result):
                log.debug(
                    "The predicted intent '{}' is mapped to "
                    " action '{}' in the domain."
                    "".format(intent, action)
                )
        elif tracker.latestActionName == action and action is not None:
            # predict next action_listen after mapped action
            latest_action = tracker.get_last_event_for(ActionExecuted)
            assert latest_action.action_name == action
            if latest_action.policy and latest_action.policy.endswith(
                type(self).__name__
            ):
                # this ensures that we only predict listen,
                # if we predicted the mapped action
                log.debug(
                    "The mapped action, '{}', for this intent, '{}', was "
                    "executed last so MappingPolicy is returning to "
                    "action_listen.".format(action, intent)
                )

                idx = domain.actions_index(LISTEN_ACTION_NAME  )
                result[idx] = 1
            else:
                log.debug(
                    "The mapped action, '{}', for the intent, '{}', was "
                    "executed last, but it was predicted by another policy, '{}', "
                    "so MappingPolicy is not predicting any action.".format(
                        action, intent, latest_action.policy
                    )
                )
        elif action == RESTART_ACTION_NAME  :
            log.debug("Restarting the conversation with action_restart.")
            idx = domain.actions_index(RESTART_ACTION_NAME  )
            result[idx] = 1
        else:
            log.debug(
                "There is no mapped action for the predicted intent, "
                "'{}'.".format(intent)
            )
        return result

    def _metadata(self) -> Dict[Text, Any]:
        return {"priority": self.priority}

    @classmethod
    def _metadata_filename(cls) -> Text:
        return "mapping_policy.json"
