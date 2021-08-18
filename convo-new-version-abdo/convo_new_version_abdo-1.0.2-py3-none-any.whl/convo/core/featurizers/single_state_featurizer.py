import logging
import numpy as np
import scipy.sparse
from typing import List, Optional, Dict, Text, Set
from collections import defaultdict

import convo.shared.utils.io
from convo.shared.core.domain import Sub_State, fetch_state, Domain
from convo.shared.nlu.interpreter import NaturalLangInterpreter
from convo.shared.core.constants import PRECEDING_ACTION   , CURRENT_LOOP   , CONVO_USER, CONVO_SLOTS
from convo.shared.constants import MIGRATION_GUIDE_DOCUMENTS_URL
from convo.shared.core.trackers import isPrevActionListenInState
from convo.shared.nlu.constants import (
    ENTITIES_NAME,
    FEATURED_TYPE_SENTENCE,
    ACT_TEXT,
    ACT_NAME,
    INTENTION,
)
from convo.shared.nlu.training_data.features import Features
from convo.shared.nlu.training_data.message import Msg

log = logging.getLogger(__name__)


class SingleStateFeaturizer:
    """Base class to transform the dialogue state into an ML format.

    Subclasses of SingleStateFeaturizer will decide how a bot will
    transform the dialogue state into a dictionary mapping an attribute
    to its features. Possible attributes are: INTENTION, TXT, ACT_NAME,
    ACT_TEXT, ENTITIES_NAME, CONVO_SLOTS and CURRENT_LOOP   . Each attribute will be
    featurized into a list of `convo.utils.features.Features`.
    """

    def __init__(self) -> None:
        self._default_feature_states = {}
        self.action_texts = []

    def prepare_from_domain(self, domain: Domain) -> None:
        """Gets necessary information for featurization from domain.

        Args:
            domain: An instance of :class:`convo.shared.core.domain.Domain`.
        """
        # store feature states for each attribute in order to create binary features
        def convert_to_dictionary(feature_states: List[Text]) -> Dict[Text, int]:
            return {
                feature_state: idx for idx, feature_state in enumerate(feature_states)
            }

        self._default_feature_states[INTENTION] = convert_to_dictionary(domain.fetch_intents)
        self._default_feature_states[ACT_NAME] = convert_to_dictionary(domain.action_names)
        self._default_feature_states[ENTITIES_NAME] = convert_to_dictionary(domain.entities)
        self._default_feature_states[CONVO_SLOTS] = convert_to_dictionary(domain.states_slot)
        self._default_feature_states[CURRENT_LOOP   ] = convert_to_dictionary(domain.form_names)
        self.action_texts = domain.action_texts

    # pytype: disable=bad-return-type
    def get_state_features_for_attribute(
        self, sub_state: Sub_State, attribute: Text
    ) -> Dict[Text, int]:
        if attribute in {INTENTION, ACT_NAME}:
            return {sub_state[attribute]: 1}
        elif attribute == ENTITIES_NAME:
            return {entity: 1 for entity in sub_state.get(ENTITIES_NAME, [])}
        elif attribute == CURRENT_LOOP   :
            return {sub_state["name"]: 1}
        elif attribute == CONVO_SLOTS:
            return {
                f"{slot_name}_{i}": value
                for slot_name, slot_as_feature in sub_state.items()
                for i, value in enumerate(slot_as_feature)
            }
        else:
            raise ValueError(
                f"Given attribute '{attribute}' is not supported. "
                f"It must be one of '{self._default_feature_states.keys()}'."
            )

    # pytype: enable=bad-return-type

    def _generate_features(
        self, sub_state: Sub_State, attribute: Text, sparse: bool = False
    ) -> List["Features"]:
        get_state_features = self.get_state_features_for_attribute(sub_state, attribute)

        get_features = np.zeros(len(self._default_feature_states[attribute]), np.float32)
        for state_feature, value in get_state_features.items():
            # check that the value is in default_feature_states to be able to assigh
            # its value
            if state_feature in self._default_feature_states[attribute]:
                get_features[self._default_feature_states[attribute][state_feature]] = value
        get_features = np.expand_dims(get_features, 0)

        if sparse:
            get_features = scipy.sparse.coo_matrix(get_features)

        get_features = Features(
            get_features,FEATURED_TYPE_SENTENCE, attribute, self.__class__.__name__
        )
        return [get_features]

    @staticmethod
    def _to_sparse_eachline_features(
        sparse_sequence_features: List["Features"],
    ) -> List["Features"]:
        return [
            Features(
                scipy.sparse.coo_matrix(feature.features.sum(0)),
                FEATURED_TYPE_SENTENCE,
                feature.attribute,
                feature.origin,
            )
            for feature in sparse_sequence_features
        ]

    def _fetch_features_from_parsed_msg(
        self, parsed_message: Optional[Msg], attributes: Set[Text]
    ) -> Dict[Text, List["Features"]]:
        if parsed_message is None:
            return {}

        result = defaultdict(list)
        for attribute in attributes:
            every_features = parsed_message.fetch_sparse_features(
                attribute
            ) + parsed_message.fetch_dense_features(attribute)

            for features in every_features:
                if features is not None:
                    result[attribute].append(features)

        # if features for INTENTION or ACT_NAME exist,
        # they are always sparse sequence features;
        # transform them to sentence sparse features
        if result.get(INTENTION):
            result[INTENTION] = self._to_sparse_eachline_features(result[INTENTION])
        if result.get(ACT_NAME):
            result[ACT_NAME] = self._to_sparse_eachline_features(result[ACT_NAME])

        return result

    @staticmethod
    def _fetch_name_attribute(attributes: Set[Text]) -> Optional[Text]:
        # there is always either INTENTION or ACT_NAME
        return next(
            (
                attribute
                for attribute in attributes
                if attribute in {INTENTION, ACT_NAME}
            ),
            None,
        )

    def _get_state_features(
        self,
        sub_state: Sub_State,
        interpreter: NaturalLangInterpreter,
        sparse: bool = False,
    ) -> Dict[Text, List["Features"]]:

        msg = Msg(data=sub_state)
        # remove entities from possible attributes
        attr = set(
            attribute for attribute in sub_state.keys() if attribute != ENTITIES_NAME
        )

        parsed_message = interpreter.featurize_msg(msg)
        result = self._fetch_features_from_parsed_msg(parsed_message, attr)

        # check that name attributes have features
        get_name_attribute = self._fetch_name_attribute(attr)
        if get_name_attribute and get_name_attribute not in result:
            # nlu pipeline didn't create features for user or action
            # this might happen, for example, when we have action_name in the state
            # but it did not get featurized because only character level
            # SumUpVectorsFeaturizer was included in the config.
            result[get_name_attribute] = self._generate_features(
                sub_state, get_name_attribute, sparse
            )

        return result

    def encode_state(
        self, state: fetch_state, interpreter: NaturalLangInterpreter
    ) -> Dict[Text, List["Features"]]:
        """Encode the given state with the help of the given interpreter.

        Args:
            state: The state to encode
            interpreter: The interpreter used to encode the state

        Returns:
            A dictionary of state_type to list of features.
        """
        get_state_features = {}
        for state_type, sub_state in state.items():
            if state_type == PRECEDING_ACTION   :
                get_state_features.update(
                    self._get_state_features(sub_state, interpreter, sparse=True)
                )
            # featurize user only if it is "real" user input,
            # i.e. input from a turn after action_listen
            if state_type == CONVO_USER and isPrevActionListenInState(state):
                get_state_features.update(
                    self._get_state_features(sub_state, interpreter, sparse=True)
                )
                if sub_state.get(ENTITIES_NAME):
                    get_state_features[ENTITIES_NAME] = self._generate_features(
                        sub_state, ENTITIES_NAME, sparse=True
                    )

            if state_type in {CONVO_SLOTS, CURRENT_LOOP   }:
                get_state_features[state_type] = self._generate_features(
                    sub_state, state_type, sparse=True
                )

        return get_state_features

    def _encode_act(
        self, action: Text, interpreter: NaturalLangInterpreter
    ) -> Dict[Text, List["Features"]]:
        if action in self.action_texts:
            act_as_sub_state = {ACT_TEXT: action}
        else:
            act_as_sub_state = {ACT_NAME: action}

        return self._get_state_features(act_as_sub_state, interpreter)

    def encode_all_acts(
        self, domain: Domain, interpreter: NaturalLangInterpreter
    ) -> List[Dict[Text, List["Features"]]]:
        """Encode all action from the domain using the given interpreter.

        Args:
            domain: The domain that contains the actions.
            interpreter: The interpreter used to encode the actions.

        Returns:
            A list of encoded actions.
        """

        return [
            self._encode_act(action, interpreter) for action in domain.action_names
        ]


class DuplexSingleStateFeaturizer(SingleStateFeaturizer):
    def __init__(self) -> None:
        super().__init__()
        convo.shared.utils.io.raising_warning(
            f"'{self.__class__.__name__}' is deprecated and "
            f"will be removed in the future. "
            f"It is recommended to use the '{SingleStateFeaturizer.__name__}' instead.",
            category=DeprecationWarning,
            docs=MIGRATION_GUIDE_DOCUMENTS_URL,
        )

    def _get_state_features(
        self,
        sub_state: Sub_State,
        interpreter: NaturalLangInterpreter,
        sparse: bool = False,
    ) -> Dict[Text, List["Features"]]:
        # create a special method that doesn't use passed interpreter
        get_name_attribute = self._fetch_name_attribute(set(sub_state.keys()))
        if get_name_attribute:
            return {
                get_name_attribute: self._generate_features(sub_state, get_name_attribute, sparse)
            }

        return {}


class TagTagenizerSingleStateFeaturizer(SingleStateFeaturizer):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__()
        # it is hard to fully mimic old behavior, but SingleStateFeaturizer
        # does the same thing if nlu pipeline is configured correctly
        convo.shared.utils.io.raising_warning(
            f"'{self.__class__.__name__}' is deprecated and "
            f"will be removed in the future. "
            f"It is recommended to use the '{SingleStateFeaturizer.__name__}' instead.",
            category=DeprecationWarning,
            docs=MIGRATION_GUIDE_DOCUMENTS_URL,
        )
