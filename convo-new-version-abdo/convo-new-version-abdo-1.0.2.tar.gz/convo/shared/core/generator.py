from collections import defaultdict, namedtuple, deque

import copy
import logging
import random

from tqdm import tqdm
from typing import Optional, List, Text, Set, Dict, Tuple, Deque, Any

from convo.shared.constants import STORIES_DOCUMENTS_URL
from convo.shared.core.constants import NOT_SET
from convo.shared.core.domain import Domain, fetch_state
from convo.shared.core.events import (
    ActionExecuted,
    UserUttered,
    ActReverted,
    UserChangeReverted,
    Restarted,
    Event,
  SetofSlot,
    OperationalLoop,
)
from convo.shared.core.trackers import DialogueStateTracer, Frozen_State
from convo.shared.core.slots import Slot
from convo.shared.core.training_data.structures import (
    StoryPlot,
    storyStart,
    StoryStage,
    RuleStage,
    generatedCheckpointPrefix,
)
from convo.shared.utils.io import logging_disabled_check
import convo.shared.utils.io

log = logging.getLogger(__name__)

ExtractorConfig = namedtuple(
    "ExtractorConfig",
    "remove_identical "
    "unique_last_num_of_states "
    "augmentation_factor "
    "max_number_of_augmented_trackers "
    "tracker_limit "
    "use_story_concatenation "
    "rand",
)


class TrackerInCachedStates(DialogueStateTracer):
    """A tracker wrapper that caches the state creation of the tracker."""

    def __init__(
        self,
        sender_id: Text,
        slots: Optional[List[Slot]],
        max_event_history: Optional[int] = None,
        domain: Optional[Domain] = None,
        is_augmented: bool = False,
        is_rule_tracker: bool = False,
    ) -> None:
        super().__init__(
            sender_id, slots, max_event_history, is_rule_tracker=is_rule_tracker
        )
        self._states_for_hashing = None
        self.domain = domain
        # T/F property to filter augmented stories
        self.is_augmented = is_augmented

    @classmethod
    def from_event(
        cls,
        sender_id: Text,
        evts: List[Event],
        slots: Optional[List[Slot]] = None,
        max_event_history: Optional[int] = None,
        sender_source: Optional[Text] = None,
        domain: Optional[Domain] = None,
        is_rule_tracker: bool = False,
    ) -> "TrackerInCachedStates":
        tracer = cls(
            sender_id, slots, max_event_history, domain, is_rule_tracker=is_rule_tracker
        )
        for e in evts:
            tracer.update(e)
        return tracer

    def hashing_of_past_states(self, domain: Domain) -> Deque[Frozen_State]:
        # we need to make sure this is the same domain, otherwise things will
        # go south. but really, the same tracker shouldn't be used across
        # domains
        assert domain == self.domain

        # if don't have it cached, we use the domain to calculate the states
        # from the events
        if self._states_for_hashing is None:
            states_name = super().freeze_state(domain)
            self._states_for_hashing = deque(
                self.current_state_freeze(s) for s in states_name
            )

        return self._states_for_hashing

    @staticmethod
    def un_freeze_states(frozen_states: Deque[Frozen_State]) -> List[fetch_state]:
        return [
            {key: dict(value) for key, value in dict(frozen_state).items()}
            for frozen_state in frozen_states
        ]

    def previous_states(self, domain: Domain) -> List[fetch_state]:
        states_for_hashing = self.hashing_of_past_states(domain)
        return self.un_freeze_states(states_for_hashing)

    def clearing_states(self) -> None:
        """Reset the states."""
        self._states_for_hashing = None

    def initialize_copy(self) -> "TrackerInCachedStates":
        """Create a new state tracker with the same initial values."""
        return type(self)(
            "",
            self.slots.values(),
            self._max_event_history,
            self.domain,
            self.is_augmented,
            self.is_rule_tracker,
        )

    def duplicate_copy(
        self, sender_id: Text = "", sender_source: Text = ""
    ) -> "TrackerInCachedStates":
        """Creates a duplicate of this tracker.

        A new tracker will be created and all events
        will be replayed."""

        # This is an optimization, we could use the original copy, but
        # the states would be lost and we would need to recalculate them

        tracer = self.initialize_copy()
        tracer.sender_id = sender_id
        tracer.sender_source = sender_source

        for event in self.events:
            tracer.update(event, skip_states=True)

        tracer._states_for_hashing = copy.copy(self._states_for_hashing)

        return tracer

    def append_current_active_state(self) -> None:
        if self._states_for_hashing is None:
            self._states_for_hashing = self.hashing_of_past_states(self.domain)
        else:
            state = self.domain.get_current_active_states(self)
            frozen_state = self.current_state_freeze(state)
            self._states_for_hashing.append(frozen_state)

    def update(self, event: Event, skip_states: bool = False) -> None:
        """Modify the state of the tracker according to an ``Event``. """

        # if `skip_states` is `True`, this function behaves exactly like the
        # normal update of the `DialogueStateTracer`

        if self._states_for_hashing is None and not skip_states:
            # rest of this function assumes we have the previous state
            # cached. let's make sure it is there.
            self._states_for_hashing = self.hashing_of_past_states(self.domain)

        super().update(event)

        if not skip_states:
            if isinstance(event, ActionExecuted):
                pass
            elif isinstance(event, ActReverted):
                self._states_for_hashing.pop()  # removes the state after the action
                self._states_for_hashing.pop()  # removes the state used for the action
            elif isinstance(event, UserChangeReverted):
                self.clearing_states()
            elif isinstance(event, Restarted):
                self.clearing_states()
            else:
                self._states_for_hashing.pop()

            self.append_current_active_state()


# define types
TrackerLookupDictionary = Dict[Optional[Text], List[TrackerInCachedStates]]

TrackerTuple = Tuple[List[TrackerInCachedStates], List[TrackerInCachedStates]]


class TrainingDataSetGenerator:
    def __init__(
        self,
        story_graph: StoryPlot,
        domain: Domain,
        remove_identical: bool = True,
        unique_last_num_of_states: Optional[int] = None,
        augmentation_factor: int = 50,
        tracker_limit: Optional[int] = None,
        use_story_concatenation: bool = True,
        debug_plots: bool = False,
    ):
        """Given a set of story parts, generates all stories that are possible.

        The different story parts can end and start with checkpoints
        and this generator will match start and end checkpoints to
        connect complete stories. Afterwards, duplicate stories will be
        removed and the data is augmented (if augmentation is enabled)."""

        self.story_graph = story_graph.withCyclesRemoved()
        if debug_plots:
            self.story_graph.anticipate("story_blocks_connections.html")

        self.domain = domain

        # 10x factor is a heuristic for augmentation rounds
        maximum_no_of_augmented_trackers = augmentation_factor * 10

        self.config = ExtractorConfig(
            remove_identical=remove_identical,
            unique_last_num_of_states=unique_last_num_of_states,
            augmentation_factor=augmentation_factor,
            max_number_of_augmented_trackers=maximum_no_of_augmented_trackers,
            tracker_limit=tracker_limit,
            use_story_concatenation=use_story_concatenation,
            rand=random.Random(42),
        )
        # hashed featurization of all finished trackers
        self.hashed_featurizations = set()

    @staticmethod
    def phase_name(everything_reachable_is_reached, phase):
        if everything_reachable_is_reached:
            return f"augmentation round {phase}"
        else:
            return f"data generation round {phase}"

    def create(self) -> List[TrackerInCachedStates]:
        """Generate trackers from stories and rules.

        Returns:
            The generated trackers.
        """
        return self.story_trackers_generation() + self.rule_trackers_generation()

    def story_trackers_generation(self) -> List[TrackerInCachedStates]:
        """Generate trackers from stories (exclude rule trackers).

        Returns:
            The generated story trackers.
        """
        generator_steps = [
            step
            for step in self.story_graph.orderedSteps()
            if not isinstance(step, RuleStage)
        ]

        return self._create(generator_steps, is_rule_data=False)

    def rule_trackers_generation(self) -> List[TrackerInCachedStates]:
        generator_steps = [
            step
            for step in self.story_graph.orderedSteps()
            if isinstance(step, RuleStage)
        ]

        return self._create(generator_steps, is_rule_data=True)

    def _create(
        self, story_steps: List[StoryStage], is_rule_data: bool = False
    ) -> List[TrackerInCachedStates]:
        if not story_steps:
            log.debug(f"No {'rules' if is_rule_data else 'story blocks'} found.")
            return []

        if self.config.remove_identical and self.config.unique_last_num_of_states:
            log.debug(
                "Generated trackers will be deduplicated "
                "based on their unique last {} states."
                "".format(self.config.unique_last_num_of_states)
            )
        self.mark_first_act_in_story_step_as_unpredictable()

        current_active_trackers = defaultdict(list)

        initialize_tracker = TrackerInCachedStates(
            "",
            self.domain.slots,
            max_event_history=self.config.tracker_limit,
            domain=self.domain,
            is_rule_tracker=is_rule_data,
        )
        current_active_trackers[storyStart].append(initialize_tracker)

        # trackers that are sent to a featurizer
        trackers_finished = []
        # keep story end trackers separately for augmentation
        trackers_for_story_end = []

        stage = 0  # one stage is one traversal of all story steps.

        # do not augment rule data
        if not is_rule_data:
            minimum_number_augmented_phases = 3 if self.config.augmentation_factor > 0 else 0
            log.debug(f"Number of augmentation rounds is {minimum_number_augmented_phases}")
        else:
            minimum_number_augmented_phases = 0

        # placeholder to track gluing process of checkpoints
        checkpoints_used = set()
        prev_unused = set()
        reached_everything_reachable = False

        # we will continue generating data until we have reached all
        # checkpoints that seem to be reachable. This is a heuristic,
        # if we did not reach any new checkpoints in an iteration, we
        # assume we have reached all and stop.

        while not reached_everything_reachable or stage < minimum_number_augmented_phases:
            stage_name = self.phase_name(reached_everything_reachable, stage)

            number_active_trackers = self.trackers_count(current_active_trackers)

            if number_active_trackers:
                log.debug(
                    "Starting {} ... (with {} trackers)"
                    "".format(stage_name, number_active_trackers)
                )
            else:
                log.debug(f"There are no trackers for {stage_name}")
                break

            # track unused checkpoints for this stage
            checkpoints_unused: Set[Text] = set()

            description = f"Processed {'rules' if is_rule_data else 'story blocks'}"
            pslab = tqdm(story_steps, desc=description, disable=logging_disabled_check())
            for step in pslab:
                trackers_incoming: List[TrackerInCachedStates] = []
                for start in step.start_checkpoints:
                    if current_active_trackers[start.name]:
                        st = start.filterTrackers(current_active_trackers[start.name])
                        trackers_incoming.extend(st)
                        checkpoints_used.add(start.name)
                    elif start.name not in checkpoints_used:
                        # need to skip - there was no previous step that
                        # had this start checkpoint as an end checkpoint
                        # it will be processed in next phases
                        checkpoints_unused.add(start.name)
                if not trackers_incoming:
                    # if there are no trackers,
                    # we can skip the rest of the loop
                    continue

                # these are the trackers that reached this story
                # step and that need to handle all events of the step

                if self.config.remove_identical:
                    trackers_incoming, end_trackers = self.duplicate_trackers_remove(
                        trackers_incoming
                    )

                    # append end trackers to finished trackers
                    trackers_finished.extend(end_trackers)

                if reached_everything_reachable:
                    # augmentation round
                    trackers_incoming = self.sub_sample_trackers(
                        trackers_incoming, self.config.max_number_of_augmented_trackers
                    )

                # update progress bar
                pslab.set_postfix({"# trackers": "{:d}".format(len(trackers_incoming))})

                trackers, end_trackers = self.process_step(step, trackers_incoming)

                # add end trackers to finished trackers
                trackers_finished.extend(end_trackers)

                # update our tracker dictionary with the trackers
                # that handled the events of the step and
                # that can now be used for further story steps
                # that start with the checkpoint this step ended with

                for end in step.end_checkpoints:
                    generator_start_name = self.find_name_of_start_checkpoint(end.name)

                    current_active_trackers[generator_start_name].extend(trackers)

                    if generator_start_name in checkpoints_used:
                        # add end checkpoint as unused
                        # if this checkpoint was processed as
                        # start one before
                        checkpoints_unused.add(generator_start_name)

                if not step.end_checkpoints:
                    unique_last = self.remove_duplicate_story_end_trackers(trackers)
                    trackers_for_story_end.extend(unique_last)

            number_finished = len(trackers_finished) + len(trackers_for_story_end)
            log.debug(f"Finished stage ({number_finished} training samples found).")

            # prepare next round
            stage += 1

            if not reached_everything_reachable:
                # check if we reached all nodes that can be reached
                # if we reached at least one more node this round
                # than last one, we assume there is still
                # something left to reach and we continue

                checkpoints_unused = self.add_unused_end_checkpoints(
                    set(current_active_trackers.keys()), checkpoints_unused, checkpoints_used
                )
                current_active_trackers = self.active_trackers_filter(
                    current_active_trackers, checkpoints_unused
                )
                number_active_trackers = self.trackers_count(current_active_trackers)

                reached_everything_reachable = (
                    checkpoints_unused == prev_unused or number_active_trackers == 0
                )
                prev_unused = checkpoints_unused

                if reached_everything_reachable:
                    # should happen only once

                    prev_unused -= checkpoints_used
                    # add trackers with unused checkpoints
                    # to finished trackers
                    for generator_start_name in prev_unused:
                        trackers_finished.extend(current_active_trackers[generator_start_name])

                    log.debug("Data generation rounds finished.")
                    log.debug(
                        "Found {} unused checkpoints".format(len(prev_unused))
                    )
                    stage = 0
                else:
                    log.debug(
                        "Found {} unused checkpoints "
                        "in current stage."
                        "".format(len(checkpoints_unused))
                    )
                    log.debug(
                        "Found {} active trackers "
                        "for these checkpoints."
                        "".format(number_active_trackers)
                    )

            if reached_everything_reachable:
                # augmentation round, so we process only
                # story end checkpoints
                # reset used checkpoints
                checkpoints_used: Set[Text] = set()

                # generate active trackers for augmentation
                current_active_trackers = self.create_starting_tracker_for_augmentation(
                    trackers_for_story_end
                )

        trackers_finished.extend(trackers_for_story_end)
        self.issue_unused_check_point_notification(prev_unused)
        log.debug("Found {} training trackers.".format(len(trackers_finished)))

        if self.config.augmentation_factor > 0:
            trackers_augmented, original_trackers = [], []
            for t in trackers_finished:
                if t.is_augmented:
                    trackers_augmented.append(t)
                else:
                    original_trackers.append(t)
            trackers_augmented = self.sub_sample_trackers(
                trackers_augmented, self.config.max_number_of_augmented_trackers
            )
            log.debug(
                "Subsampled to {} augmented training trackers."
                "".format(len(trackers_augmented))
            )
            log.debug(
                "There are {} original trackers.".format(len(original_trackers))
            )
            trackers_finished = original_trackers + trackers_augmented

        return trackers_finished

    @staticmethod
    def trackers_count(active_trackers: TrackerLookupDictionary) -> int:
        """Count the number of trackers in the tracker dictionary."""
        return sum(len(ts) for ts in active_trackers.values())

    def sub_sample_trackers(
        self,
        incoming_trackers: List[TrackerInCachedStates],
        max_number_of_trackers: int,
    ) -> List[TrackerInCachedStates]:
        """Subsample the list of trackers to retrieve a random subset."""

        # if flows get very long and have a lot of forks we
        # get into trouble by collecting too many trackers
        # hence the sub sampling
        if max_number_of_trackers is not None:
            return sub_sample_array(
                incoming_trackers, max_number_of_trackers, rand=self.config.rand
            )
        else:
            return incoming_trackers

    def find_name_of_start_checkpoint(self, end_name: Text) -> Text:
        """Find start checkpoint name given end checkpoint name of a cycle"""
        return self.story_graph.story_end_checkpoints.get(end_name, end_name)

    @staticmethod
    def add_unused_end_checkpoints(
        start_checkpoints: Set[Text],
        unused_checkpoints: Set[Text],
        used_checkpoints: Set[Text],
    ) -> Set[Text]:
        """Add unused end checkpoints
        if they were never encountered as start checkpoints
        """

        return unused_checkpoints.union(
            {
                start_name
                for start_name in start_checkpoints
                if start_name not in used_checkpoints
            }
        )

    @staticmethod
    def active_trackers_filter(
        active_trackers: TrackerLookupDictionary, unused_checkpoints: Set[Text]
    ) -> TrackerLookupDictionary:
        """Filter active trackers that ended with unused checkpoint
        or are parts of loops."""
        next_active_tracker = defaultdict(list)

        for start_name in unused_checkpoints:
            # process trackers ended with unused checkpoints further
            if start_name != storyStart:
                # there is no point to process storyStart checkpoint again
                next_active_tracker[start_name] = active_trackers.get(start_name, [])

        return next_active_tracker

    def create_starting_tracker_for_augmentation(
        self, story_end_trackers: List[TrackerInCachedStates]
    ) -> TrackerLookupDictionary:
        """This is where the augmentation magic happens.

        We will reuse all the trackers that reached the
        end checkpoint `None` (which is the end of a
        story) and start processing all steps again. So instead
        of starting with a fresh tracker, the second and
        all following phases will reuse a couple of the trackers
        that made their way to a story end.

        We need to do some cleanup before processing them again.
        """
        next_active_tracker = defaultdict(list)

        if self.config.use_story_concatenation:
            end_trackers = sub_sample_array(
                story_end_trackers,
                self.config.augmentation_factor,
                rand=self.config.rand,
            )
            for t in end_trackers:
                # this is a nasty thing - all stories end and
                # start with action listen - so after logging the first
                # actions in the next phase the trackers would
                # contain action listen followed by action listen.
                # to fix this we are going to "undo" the last action listen

                # tracker should be copied,
                # otherwise original tracker is updated
                augumented_type = t.duplicate_copy()
                augumented_type.is_augmented = True
                augumented_type.update(ActReverted())
                next_active_tracker[storyStart].append(augumented_type)

        return next_active_tracker

    def process_step(
        self, step: StoryStage, incoming_trackers: List[TrackerInCachedStates]
    ) -> TrackerTuple:
        """Processes a steps generator_events with all generator_trackers.

        The generator_trackers that reached the steps starting checkpoint will
        be used to process the generator_events. Collects and returns training
        data while processing the story step."""

        generator_events = step.explicitEvents(self.domain)

        generator_trackers = []
        if generator_events:  # small optimization

            # need to copy the tracker as multiple story steps
            # might start with the same checkpoint and all of them
            # will use the same set of incoming generator_trackers

            for tracker in incoming_trackers:
                # sender id is used to be able for a human to see where the
                # messages and generator_events for this tracker came from - to do this
                # we concatenate the story block names of the blocks that
                # contribute to the generator_trackers generator_events
                if tracker.sender_id:
                    if step.block_name not in tracker.sender_id.split(" > "):
                        latest_sender = tracker.sender_id + " > " + step.block_name
                    else:
                        latest_sender = tracker.sender_id
                else:
                    latest_sender = step.block_name
                generator_trackers.append(tracker.duplicate_copy(latest_sender, step.source_name))

        trackers_end = []
        for event in generator_events:
            for tracker in generator_trackers:
                if isinstance(
                    event, (ActReverted, UserChangeReverted, Restarted)
                ):
                    trackers_end.append(tracker.duplicate_copy(tracker.sender_id))
                if isinstance(step, RuleStage):
                    # The rules can specify that a form or a slot shouldn't be set,
                    # therefore we need to distinguish between not set
                    # and explicitly set to None
                    if isinstance(event, OperationalLoop) and event.name is None:
                        event.name = NOT_SET

                    if isinstance(event, SetofSlot) and event.value is None:
                        event.value = NOT_SET   

                tracker.update(event)

        # end generator_trackers should be returned separately
        # to avoid using them for augmentation
        return generator_trackers, trackers_end

    def duplicate_trackers_remove(
        self, trackers: List[TrackerInCachedStates]
    ) -> TrackerTuple:
        """Removes trackers that create equal featurizations
            for current story step.

        From multiple trackers that create equal featurizations
        we only need to keep one. Because as we continue processing
        events and story steps, all trackers that created the
        same featurization once will do so in the future (as we
        feed the same events to all trackers)."""

        step_hashed_features = set()

        # collected trackers that created different featurizations
        distinct_trackers = []  # for current step
        end_trackers = []  # for all steps

        for tracker in trackers:
            state_for_hashing = tuple(tracker.hashing_of_past_states(self.domain))
            hashed_value = hash(state_for_hashing)

            # only continue with trackers that created a
            # hashed_featurization we haven't observed
            if hashed_value  not in step_hashed_features:
                if self.config.unique_last_num_of_states:
                    closing_states = state_for_hashing[
                        -self.config.unique_last_num_of_states :
                    ]
                    rearmost_hashed = hash(closing_states )

                    if rearmost_hashed not in step_hashed_features:
                        step_hashed_features.add(rearmost_hashed)
                        distinct_trackers.append(tracker)
                    elif (
                            len(state_for_hashing) > len(closing_states )
                            and hashed_value not in self.hashed_featurizations
                    ):
                        self.hashed_featurizations.add(hashed_value)
                        end_trackers.append(tracker)
                else:
                    distinct_trackers.append(tracker)

                step_hashed_features.add(hashed_value)

        return distinct_trackers, end_trackers

    def remove_duplicate_story_end_trackers(
        self, trackers: List[TrackerInCachedStates]
    ) -> List[TrackerInCachedStates]:
        """Removes trackers that reached story end and
        created equal featurizations."""

        # collected trackers that created different featurizations
        distinct_trackers = []  # for all steps

        # deduplication of finished trackers is needed,
        # otherwise featurization does a lot of unnecessary work

        for tracker in trackers:
            state_for_hashing = tuple(tracker.hashing_of_past_states(self.domain))
            hashed_value = hash(state_for_hashing + (tracker.is_rule_tracker,))

            # only continue with trackers that created a
            # hashed_featurization we haven't observed

            if hashed_value not in self.hashed_featurizations:
                self.hashed_featurizations.add(hashed_value)
                distinct_trackers.append(tracker)

        return distinct_trackers

    def mark_first_act_in_story_step_as_unpredictable(self) -> None:
        """Mark actions which shouldn't be used during ML training.

        If a story starts with an action, we can not use
        that first action as a training example, as there is no
        history. There is one exception though, we do want to
        predict action listen. But because stories never
        contain action listen events (they are added when a
        story gets converted to a dialogue) we need to apply a
        small trick to avoid marking actions occurring after
        an action listen as unpredictable."""

        for step in self.story_graph.story_steps:
            # TODO: this does not work if a step is the conversational start
            #       as well as an intermediary part of a conversation.
            #       This means a checkpoint can either have multiple
            #       checkpoints OR be the start of a conversation
            #       but not both.
            if storyStart in {s.name for s in step.start_checkpoints}:
                for i, e in enumerate(step.events):
                    if isinstance(e, UserUttered):
                        # if there is a user utterance, that means before the
                        # user uttered something there has to be
                        # an action listen. therefore, any action that comes
                        # after this user utterance isn't the first
                        # action anymore and the tracker used for prediction
                        # is not empty anymore. Hence, it is fine
                        # to predict anything that occurs after an utterance.
                        break
                    if isinstance(e, ActionExecuted):
                        e.unpredictable = True
                        break

    def issue_unused_check_point_notification(
        self, unused_checkpoints: Set[Text]
    ) -> None:
        """Warns about unused story blocks.

        Unused steps are ones having a start or end checkpoint
        that no one provided."""

        if storyStart in unused_checkpoints:
            convo.shared.utils.io.raising_warning(
                "There is no starting story block "
                "in the training data. "
                "All your story blocks start with some checkpoint. "
                "There should be at least one story block "
                "that starts without any checkpoint.",
                docs=STORIES_DOCUMENTS_URL + "#stories",
            )

        # running through the steps first will result in only one warning
        # per block (as one block might have multiple steps)
        start_collected = set()
        end_collected = set()
        for step in self.story_graph.story_steps:
            for start in step.start_checkpoints:
                if start.name in unused_checkpoints:
                    # After processing, there shouldn't be a story part left.
                    # This indicates a start checkpoint that doesn't exist
                    start_collected.add((start.name, step.block_name))

            for end in step.end_checkpoints:
                if end.name in unused_checkpoints:
                    # After processing, there shouldn't be a story part left.
                    # This indicates an end checkpoint that doesn't exist
                    end_collected.add((end.name, step.block_name))

        for cp, block_name in start_collected:
            if not cp.startswith(generatedCheckpointPrefix):
                convo.shared.utils.io.raising_warning(
                    f"Unsatisfied start checkpoint '{cp}' "
                    f"in block '{block_name}'. "
                    f"Remove this checkpoint or add "
                    f"story blocks that end "
                    f"with this checkpoint.",
                    docs=STORIES_DOCUMENTS_URL + "#checkpoints",
                )

        for cp, block_name in end_collected:
            if not cp.startswith(generatedCheckpointPrefix):
                convo.shared.utils.io.raising_warning(
                    f"Unsatisfied end checkpoint '{cp}' "
                    f"in block '{block_name}'. "
                    f"Remove this checkpoint or add "
                    f"story blocks that start "
                    f"with this checkpoint.",
                    docs=STORIES_DOCUMENTS_URL + "#checkpoints",
                )


def sub_sample_array(
    array: List[Any],
    max_values: int,
    can_modify_incoming_array: bool = True,
    rand: Optional[random.Random] = None,
) -> List[Any]:
    """Shuffles the array and returns `max_values` number of elements."""
    if not can_modify_incoming_array:
        array = array[:]
    if rand is not None:
        rand.shuffle(array)
    else:
        random.shuffle(array)
    return array[:max_values]
