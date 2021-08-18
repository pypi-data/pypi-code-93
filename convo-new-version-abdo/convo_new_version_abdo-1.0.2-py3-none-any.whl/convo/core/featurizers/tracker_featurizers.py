from pathlib import Path

import jsonpickle
import logging

from convo.shared.exceptions import ConvoExceptions 
from convo.shared.nlu.constants import TXT
from tqdm import tqdm
from typing import Tuple, List, Optional, Dict, Text, Union
import numpy as np

from convo.core.featurizers.single_state_featurizer import SingleStateFeaturizer
from convo.shared.core.domain import fetch_state, Domain
from convo.shared.core.events import ActionExecuted
from convo.shared.core.trackers import DialogueStateTracer
from convo.shared.nlu.interpreter import NaturalLangInterpreter
from convo.shared.core.constants import CONVO_USER
import convo.shared.utils.io
from convo.shared.nlu.training_data.features import Features

FEATURIZER_FILENAME = "featurizer.json"

log = logging.getLogger(__name__)


class NotvalidStory(ConvoExceptions ):
    """Exception that can be raised if story cannot be featurized."""

    def __init__(self, message) -> None:
        self.message = message
        super(NotvalidStory, self).__init__()

    def __str__(self) -> Text:
        return self.message


class FeaturizerTracker:
    """Base class for actual tracker featurizers."""

    def __init__(
        self, state_featurizer: Optional[SingleStateFeaturizer] = None
    ) -> None:
        """Initialize the tracker featurizer.

        Args:
            state_featurizer: The state featurizer used to encode the states.
        """
        self.state_featurizer = state_featurizer

    @staticmethod
    def _create_states(tracker: DialogueStateTracer, domain: Domain) -> List[fetch_state]:
        """Create states for the given tracker.

        Args:
            tracker: a :class:`convo.core.trackers.DialogueStateTracer`
            domain: a :class:`convo.shared.core.domain.Domain`

        Returns:
            a list of states
        """
        return tracker.freeze_state(domain)

    def _featurize_states(
        self,
        trackers_as_states: List[List[fetch_state]],
        interpreter: NaturalLangInterpreter,
    ) -> List[List[Dict[Text, List["Features"]]]]:
        return [
            [
                self.state_featurizer.encode_state(state, interpreter)
                for state in tracker_states
            ]
            for tracker_states in trackers_as_states
        ]

    @staticmethod
    def _convert_labels_to_ids(
        trackers_as_actions: List[List[Text]], domain: Domain
    ) -> np.ndarray:
        # store labels in numpy arrays so that it corresponds to np arrays of input features
        return np.array(
            [
                np.array(
                    [domain.actions_index(action) for action in tracker_actions]
                )
                for tracker_actions in trackers_as_actions
            ]
        )

    def training_states_and_actions(
        self, trackers: List[DialogueStateTracer], domain: Domain
    ) -> Tuple[List[List[fetch_state]], List[List[Text]]]:
        """Transforms list of trackers to lists of states and actions.

        Args:
            trackers: The trackers to transform
            domain: The domain

        Returns:
            A tuple of list of states and list of actions.
        """
        raise NotImplementedError(
            "Featurizer must have the capacity to encode trackers to feature vectors"
        )

    def featurize_trackers(
        self,
        trackers: List[DialogueStateTracer],
        domain: Domain,
        interpreter: NaturalLangInterpreter,
    ) -> Tuple[List[List[Dict[Text, List["Features"]]]], np.ndarray]:
        """Featurize the training trackers.

        Args:
            trackers: list of training trackers
            domain: the domain
            interpreter: the interpreter

        Returns:
            - a dictionary of state types (INTENTION, TXT, ACT_NAME, ACT_TEXT,
              ENTITIES_NAME, CONVO_SLOTS, CURRENT_LOOP   ) to a list of features for all dialogue
              turns in all training trackers
            - the label ids (e.g. action ids) for every dialuge turn in all training
              trackers
        """
        if self.state_featurizer is None:
            raise ValueError(
                f"Instance variable 'state_featurizer' is not set. "
                f"During initialization set 'state_featurizer' to an instance of "
                f"'{SingleStateFeaturizer.__class__.__name__}' class "
                f"to get numerical features for trackers."
            )

        self.state_featurizer.prepare_from_domain(domain)

        tracers_as_states, trackers_as_act = self.training_states_and_actions(
            trackers, domain
        )

        tracer_state_features = self._featurize_states(tracers_as_states, interpreter)
        tag_ids = self._convert_labels_to_ids(trackers_as_act, domain)

        return tracer_state_features, tag_ids

    def prediction_states(
        self, trackers: List[DialogueStateTracer], domain: Domain
    ) -> List[List[fetch_state]]:
        """Transforms list of trackers to lists of states for prediction.

        Args:
            trackers: The trackers to transform
            domain: The domain

        Returns:
            A list of states.
        """
        raise NotImplementedError(
            "Featurizer must have the capacity to create feature vector"
        )

    def create_state_features(
        self,
        trackers: List[DialogueStateTracer],
        domain: Domain,
        interpreter: NaturalLangInterpreter,
    ) -> List[List[Dict[Text, List["Features"]]]]:
        """Create state features for prediction.

        Args:
            trackers: A list of state trackers
            domain: The domain
            interpreter: The interpreter

        Returns:
            A dictionary of state type (INTENTION, TXT, ACT_NAME, ACT_TEXT,
            ENTITIES_NAME, CONVO_SLOTS, CURRENT_LOOP   ) to a list of features for all dialogue
            turns in all trackers.
        """
        tracers_as_states = self.prediction_states(trackers, domain)
        return self._featurize_states(tracers_as_states, interpreter)

    def persist(self, path: Union[Text, Path]) -> None:
        """Persist the tracker featurizer to the given path.

        Args:
            path: The path to persist the tracker featurizer to.
        """
        featurizer_filename = Path(path) / FEATURIZER_FILENAME
        convo.shared.utils.io.create_dir_from_file(featurizer_filename)

        # noinspection PyTypeChecker
        convo.shared.utils.io.writing_text_file(
            str(jsonpickle.encode(self)), featurizer_filename
        )

    @staticmethod
    def load(path: Text) -> Optional["FeaturizerTracker"]:
        """Load the featurizer from file.

        Args:
            path: The path to load the tracker featurizer from.

        Returns:
            The loaded tracker featurizer.
        """
        featurizer_file = Path(path) / FEATURIZER_FILENAME
        if featurizer_file.is_file():
            return jsonpickle.decode(convo.shared.utils.io.read_file(featurizer_file))

        log.error(
            f"Couldn't load featurizer for policy. "
            f"File '{featurizer_file}' doesn't exist."
        )
        return None


class FullDialogueTracerFeaturizer(FeaturizerTracker):
    """Creates full dialogue training data for time distributed architectures.

    Creates training data that uses each time output for prediction.
    Training data is padded up to the length of the longest dialogue with -1.
    """

    def training_states_and_actions(
        self, trackers: List[DialogueStateTracer], domain: Domain
    ) -> Tuple[List[List[fetch_state]], List[List[Text]]]:
        """Transforms list of trackers to lists of states and acts.

        Training data is padded up to the length of the longest dialogue with -1.

        Args:
            trackers: The trackers to transform
            domain: The domain

        Returns:
            A tuple of list of states and list of acts.
        """

        tracers_as_states = []
        trackers_as_act = []

        log.debug(
            "Creating states and action examples from "
            "collected trackers (by {}({}))..."
            "".format(type(self).__name__, type(self.state_featurizer).__name__)
        )
        p_bar = tqdm(
            trackers,
            desc="Processed trackers",
            disable=convo.shared.utils.io.logging_disabled_check(),
        )
        for tracker in p_bar:
            states_name = self._create_states(tracker, domain)

            remove_first_state = False
            acts = []
            for event in tracker.request_events():
                if not isinstance(event, ActionExecuted):
                    continue

                if not event.unpredictable:
                    # only acts which can be
                    # predicted at a stories start
                    acts.append(event.action_name or event.action_text)
                else:
                    # unpredictable acts can be
                    # only the first in the story
                    if remove_first_state:
                        raise NotvalidStory(
                            f"Found two unpredictable acts in one story "
                            f"'{tracker.sender_id}'. Check your story files."
                        )
                    remove_first_state = True

            if remove_first_state:
                states_name = states_name[1:]

            tracers_as_states.append(states_name[:-1])
            trackers_as_act.append(acts)

        return tracers_as_states, trackers_as_act

    def prediction_states(
        self, trackers: List[DialogueStateTracer], domain: Domain
    ) -> List[List[fetch_state]]:
        """Transforms list of trackers to lists of states for prediction.

        Args:
            trackers: The trackers to transform
            domain: The domain

        Returns:
            A list of states.
        """

        tracers_as_states = [
            self._create_states(tracker, domain) for tracker in trackers
        ]
        # TODO there is no prediction support for e2e input right now, therefore
        #  temporary remove TEXT features from CONVO_USER state during prediction
        for states in tracers_as_states:
            for state in states:
                if state.get(CONVO_USER, {}).get(TXT):
                    del state[CONVO_USER][TXT]

        return tracers_as_states


class MaxHistoryTrackerFeaturizer(FeaturizerTracker):
    """Slices the tracker history into max_history batches.

    Creates training data that uses last output for prediction.
    Training data is padded up to the max_history with -1.
    """

    def __init__(
        self,
        state_featurizer: Optional[SingleStateFeaturizer] = None,
        max_history: Optional[int] = None,
        remove_identical: bool = True,
    ) -> None:

        super().__init__(state_featurizer)
        self.max_history = max_history
        self.remove_identical = remove_identical

    @staticmethod
    def slice_state_history(
        states: List[fetch_state], slice_length: Optional[int]
    ) -> List[fetch_state]:
        """Slice states from the trackers history.

        If the slice is at the array borders, padding will be added to ensure
        the slice length.

        Args:
            states: The states
            slice_length: The slice length

        Returns:
            The sliced states.
        """
        if not slice_length:
            return states

        return states[-slice_length:]

    @staticmethod
    def _hash_example(
        states: List[fetch_state], action: Text, tracker: DialogueStateTracer
    ) -> int:
        """Hash states for efficient deduplication."""
        stable_states = tuple(
            s if s is None else tracker.current_state_freeze(s) for s in states
        )
        stable_acts = (action,)
        return hash((stable_states, stable_acts))

    def training_states_and_actions(
        self, trackers: List[DialogueStateTracer], domain: Domain
    ) -> Tuple[List[List[fetch_state]], List[List[Text]]]:
        """Transforms list of trackers to lists of states and actions.

        Training data is padded up to the length of the longest dialogue with -1.

        Args:
            trackers: The trackers to transform
            domain: The domain

        Returns:
            A tuple of list of states and list of actions.
        """

        tracers_as_states = []
        trackers_as_act = []

        # from multiple states that create equal featurizations
        # we only need to keep one.
        hashed_eg = set()

        log.debug(
            "Creating states and action examples from "
            "collected trackers (by {}({}))..."
            "".format(type(self).__name__, type(self.state_featurizer).__name__)
        )
        p_bar = tqdm(
            trackers,
            desc="Processed trackers",
            disable=convo.shared.utils.io.logging_disabled_check(),
        )
        for tracker in p_bar:
            states = self._create_states(tracker, domain)

            states_len_for_act = 0
            for event in tracker.request_events():
                if not isinstance(event, ActionExecuted):
                    continue

                states_len_for_act += 1

                # use only actions which can be predicted at a stories start
                if event.unpredictable:
                    continue

                sliced_states = self.slice_state_history(
                    states[:states_len_for_act], self.max_history
                )
                if self.remove_identical:
                    hashed = self._hash_example(
                        sliced_states, event.action_name or event.action_text, tracker
                    )

                    # only continue with tracker_states that created a
                    # hashed_featurization we haven't observed
                    if hashed not in hashed_eg:
                        hashed_eg.add(hashed)
                        tracers_as_states.append(sliced_states)
                        trackers_as_act.append(
                            [event.action_name or event.action_text]
                        )
                else:
                    tracers_as_states.append(sliced_states)
                    trackers_as_act.append([event.action_name or event.action_text])

                p_bar.set_postfix({"# actions": "{:d}".format(len(trackers_as_act))})

        log.debug("Created {} action examples.".format(len(trackers_as_act)))

        return tracers_as_states, trackers_as_act

    def prediction_states(
        self, trackers: List[DialogueStateTracer], domain: Domain
    ) -> List[List[fetch_state]]:
        """Transforms list of trackers to lists of states for prediction.

        Args:
            trackers: The trackers to transform
            domain: The domain

        Returns:
            A list of states.
        """

        tracers_as_states = [
            self._create_states(tracker, domain) for tracker in trackers
        ]
        tracers_as_states = [
            self.slice_state_history(states, self.max_history)
            for states in tracers_as_states
        ]
        # TODO there is no prediction support for e2e input right now, therefore
        #  temporary remove TEXT features from CONVO_USER state during prediction
        for states in tracers_as_states:
            for state in states:
                if state.get(CONVO_USER, {}).get(TXT):
                    del state[CONVO_USER][TXT]

        return tracers_as_states
