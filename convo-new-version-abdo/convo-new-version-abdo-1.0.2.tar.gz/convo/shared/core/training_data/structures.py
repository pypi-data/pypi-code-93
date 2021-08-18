import json
import logging
from collections import deque, defaultdict

import uuid
import typing
from typing import List, Text, Dict, Optional, Tuple, Any, Set, ValuesView, Union

import convo.shared.utils.io
from convo.shared.core.constants import LISTEN_ACTION_NAME  , SESSION_START_ACTION_NAME  
from convo.shared.core.conversation import Dialogue  # pytype: disable=pyi-error
from convo.shared.core.domain import Domain  # pytype: disable=pyi-error
from convo.shared.core.events import (  # pytype: disable=pyi-error
    UserUttered,
    ActionExecuted,
    Event,
    SessionBegan,
)
from convo.shared.core.trackers import DialogueStateTracer  # pytype: disable=pyi-error

if typing.TYPE_CHECKING:
    import networkx as nx

log = logging.getLogger(__name__)

# Inspection id used to identify story starting blocks
storyStart = "storyStart"

# Inspection id used to identify story end blocks
storyEnd = None

# need abbreviations otherwise they are not visualized well
generatedCheckpointPrefix = "GENR_"
checkpointCyclePrefix = "CYCL_"

generatedHashLength = 5

formPrefix = "form: "
# prefix for storystep ID to get reproducible sorting results
# will get increased with each new instance
stepCount = 1


class Inspection:
    def __init__(
        self, name: Optional[Text], conditions: Optional[Dict[Text, Any]] = None
    ) -> None:

        self.name = name
        self.conditions = conditions if conditions else {}

    def as_story_string(self) -> Text:
        dumped_conds = json.dumps(self.conditions) if self.conditions else ""
        return f"{self.name}{dumped_conds}"

    def filterTrackers(
        self, trackerList: List[DialogueStateTracer]
    ) -> List[DialogueStateTracer]:
        """Filters out all trackers that do not satisfy the conditions."""

        if not self.conditions:
            return trackerList

        for slot_name, slot_value in self.conditions.items():
            trackerList = [t for t in trackerList if t.get_slot(slot_name) == slot_value]
        return trackerList

    def __repr__(self) -> Text:
        return "Inspection(name={!r}, conditions={})".format(
            self.name, json.dumps(self.conditions)
        )


class StoryStage:
    """A StoryStage is a section of a story block between two checkpoints.

    NOTE: Checkpoints are not only limited to those manually written
    in the story file, but are also implicitly created at points where
    multiple convo_intents are separated in one line by chaining them with "OR"s.
    """

    def __init__(
        self,
        block_name: Optional[Text] = None,
        start_checkpoints: Optional[List[Inspection]] = None,
        end_checkpoints: Optional[List[Inspection]] = None,
        events: Optional[List[Union[Event, List[Event]]]] = None,
        source_name: Optional[Text] = None,
    ) -> None:

        self.end_checkpoints = end_checkpoints if end_checkpoints else []
        self.start_checkpoints = start_checkpoints if start_checkpoints else []
        self.events = events if events else []
        self.block_name = block_name
        self.source_name = source_name
        # put a counter prefix to uuid to get reproducible sorting results
        global stepCount
        self.id = "{}_{}".format(stepCount, uuid.uuid4().hex)
        stepCount += 1

    def createCopy(self, use_new_id: bool) -> "StoryStage":
        copied = StoryStage(
            self.block_name,
            self.start_checkpoints,
            self.end_checkpoints,
            self.events[:],
            self.source_name,
        )
        if not use_new_id:
            copied.id = self.id
        return copied

    def addUserMessage(self, user_message: UserUttered) -> None:
        self.addEvent(user_message)

    def addEvent(self, event: Event) -> None:
        self.events.append(event)

    def addEvents(self, events: List[Event]) -> None:
        self.events.append(events)

    @staticmethod
    def checkpointString(story_step_element: Inspection) -> Text:
        return f"> {story_step_element.as_story_string()}\n"

    @staticmethod
    def userString(story_step_element: UserUttered, e2e: bool) -> Text:
        return f"* {story_step_element.as_story_string(e2e)}\n"

    @staticmethod
    def botString(story_step_element: Event) -> Text:
        return f"    - {story_step_element.as_story_string()}\n"

    def as_story_string(self, flat: bool = False, e2e: bool = False) -> Text:
        # if the output should be flattened, we
        # will exclude the caption and any checkpoints.
        if flat:
            output = ""
        else:
            output = f"\n## {self.block_name}\n"
            for s in self.start_checkpoints:
                if s.name != storyStart:
                    output += self.checkpointString(s)

        for s in self.events:
            if (
                self.isActionListen(s)
                or self.isActionSessionStart(s)
                or isinstance(s, SessionBegan)
            ):
                continue

            if isinstance(s, UserUttered):
                output += self.userString(s, e2e)
            elif isinstance(s, Event):
                converted = s.as_story_string()  # pytype: disable=attribute-error
                if converted:
                    output += self.botString(s)
            else:
                raise Exception(f"Unexpected element in story step: {s}")

        if not flat:
            for s in self.end_checkpoints:
                output += self.checkpointString(s)
        return output

    @staticmethod
    def isActionListen(event: Event) -> bool:
        # this is not an `isinstance` because
        # we don't want to allow subclasses here
        # pytype: disable=attribute-error
        return type(event) == ActionExecuted and event.action_name == LISTEN_ACTION_NAME
        # pytype: enable=attribute-error

    @staticmethod
    def isActionSessionStart(event: Event) -> bool:
        # this is not an `isinstance` because
        # we don't want to allow subclasses here
        # pytype: disable=attribute-error
        return (
                type(event) == ActionExecuted
                and event.action_name == SESSION_START_ACTION_NAME
        )
        # pytype: enable=attribute-error

    def addActionListen(self, events: List[Event]) -> None:
        if not events or not self.isActionListen(events[-1]):
            # do not add second action_listen
            events.append(ActionExecuted(LISTEN_ACTION_NAME  ))

    def explicitEvents(
        self, domain: Domain, should_append_final_listen: bool = True
    ) -> List[Union[Event, List[Event]]]:
        """Returns eventList contained in the story step including implicit eventList.

        Not all eventList are always listed in the story dsl. This
        includes listen actions as well as implicitly
        set slots. This functions makes these eventList explicit and
        returns them with the rest of the steps eventList.
        """

        eventList = []

        for e in self.events:
            if isinstance(e, UserUttered):
                self.addActionListen(eventList)
                eventList.append(e)
                eventList.extend(
                    domain.entities_slots(
                        e.entities  # pytype: disable=attribute-error
                    )
                )
            else:
                eventList.append(e)

        if not self.end_checkpoints and should_append_final_listen:
            self.addActionListen(eventList)

        return eventList

    def __repr__(self) -> Text:
        return (
            "StoryStage("
            "block_name={!r}, "
            "start_checkpoints={!r}, "
            "end_checkpoints={!r}, "
            "events={!r})".format(
                self.block_name,
                self.start_checkpoints,
                self.end_checkpoints,
                self.events,
            )
        )


class RuleStage(StoryStage):
    """A Special type of StoryStage representing a Rule. """

    def __init__(
        self,
        block_name: Optional[Text] = None,
        start_checkpoints: Optional[List[Inspection]] = None,
        end_checkpoints: Optional[List[Inspection]] = None,
        events: Optional[List[Union[Event, List[Event]]]] = None,
        source_name: Optional[Text] = None,
        condition_events_indices: Optional[Set[int]] = None,
    ) -> None:
        super().__init__(
            block_name, start_checkpoints, end_checkpoints, events, source_name
        )
        self.condition_events_indices = (
            condition_events_indices if condition_events_indices else set()
        )

    def createCopy(self, use_new_id: bool) -> "StoryStage":
        cloned = RuleStage(
            self.block_name,
            self.start_checkpoints,
            self.end_checkpoints,
            self.events[:],
            self.source_name,
            self.condition_events_indices,
        )
        if not use_new_id:
            cloned.id = self.id
        return cloned

    def __repr__(self) -> Text:
        return (
            "RuleStage("
            "block_name={!r}, "
            "start_checkpoints={!r}, "
            "end_checkpoints={!r}, "
            "events={!r})".format(
                self.block_name,
                self.start_checkpoints,
                self.end_checkpoints,
                self.events,
            )
        )

    def getRulesCondition(self) -> List[Event]:
        """Returns a list of events forming a condition of the Rule. """

        return [
            event
            for event_id, event in enumerate(self.events)
            if event_id in self.condition_events_indices
        ]

    def getRulesEvents(self) -> List[Event]:
        """Returns a list of events forming the Rule, that are not conditions. """

        return [
            event
            for event_id, event in enumerate(self.events)
            if event_id not in self.condition_events_indices
        ]

    def addEventAsCondition(self, event: Event) -> None:
        """Adds event to the Rule as part of its condition.

        Args:
            event: The event to be added.
        """
        self.condition_events_indices.add(len(self.events))
        self.events.append(event)


class Story:
    def __init__(
        self, story_steps: List[StoryStage] = None, story_name: Optional[Text] = None
    ) -> None:
        self.story_steps = story_steps if story_steps else []
        self.story_name = story_name

    @staticmethod
    def from_events_tracker(events: List[Event], story_name: Optional[Text] = None) -> "Story":
        """Create a story from a list of events."""

        storyStep = StoryStage(story_name)
        for event in events:
            storyStep.addEvent(event)
        return Story([storyStep], story_name)

    def asDialogue(self, sender_id: Text, domain: Domain) -> Dialogue:
        eventList = []
        for step in self.story_steps:
            eventList.extend(
                step.explicitEvents(domain, should_append_final_listen=False)
            )

        eventList.append(ActionExecuted(LISTEN_ACTION_NAME  ))
        return Dialogue(sender_id, eventList)

    def as_story_string(self, flat: bool = False, e2e: bool = False) -> Text:
        storyContent = ""
        for step in self.story_steps:
            storyContent += step.as_story_string(flat, e2e)

        if flat:
            if self.story_name:
                title = self.story_name
            else:
                title = "Generated Story {}".format(hash(storyContent))
            return f"## {title}\n{storyContent}"
        else:
            return storyContent

    def dumpToFile(
        self, filename: Text, flat: bool = False, e2e: bool = False
    ) -> None:

        convo.shared.utils.io.writing_text_file(
            self.as_story_string(flat, e2e), filename, append=True
        )


class StoryPlot:
    """Graph of the story-steps pooled from all stories in the training data."""

    def __init__(
        self,
        story_steps: List[StoryStage],
        story_end_checkpoints: Optional[Dict[Text, Text]] = None,
    ) -> None:
        self.story_steps = story_steps
        self.step_lookup = {s.id: s for s in self.story_steps}
        ordered_ids, cyclic_edges = StoryPlot.orderSteps(story_steps)
        self.ordered_ids = ordered_ids
        self.cyclic_edge_ids = cyclic_edges
        if story_end_checkpoints:
            self.story_end_checkpoints = story_end_checkpoints
        else:
            self.story_end_checkpoints = {}

    def __hash__(self) -> int:
        selfAsString= self.as_story_string()
        textHash= convo.shared.utils.io.fetch_text_hashcode(selfAsString)

        return int(textHash, 16)

    def orderedSteps(self) -> List[StoryStage]:
        """Returns the story steps ordered by topological order of the DAG."""

        return [self.get(step_id) for step_id in self.ordered_ids]

    def cyclicEdges(self) -> List[Tuple[Optional[StoryStage], Optional[StoryStage]]]:
        """Returns the story steps ordered by topological order of the DAG."""

        return [
            (self.get(source), self.get(target))
            for source, target in self.cyclic_edge_ids
        ]

    def merge(self, others: Optional["StoryPlot"]) -> "StoryPlot":
        if not others:
            return self

        procedures = self.story_steps.copy() + others.story_steps
        storyEndCheckpoints = self.story_end_checkpoints.copy().update(
            others.story_end_checkpoints
        )
        return StoryPlot(procedures, storyEndCheckpoints)

    @staticmethod
    def overlappingCheckpointNames(
        cps: List[Inspection], other_cps: List[Inspection]
    ) -> Set[Text]:
        """Find overlapping checkpoints names"""

        return {cp.name for cp in cps} & {cp.name for cp in other_cps}

    def withCyclesRemoved(self) -> "StoryPlot":
        """Create a graph with the cyclic edges removed from this graph."""

        storyEndCheckpoints = self.story_end_checkpoints.copy()
        cyclicEdgeIds = self.cyclic_edge_ids
        # we need to remove the begin steps and replace them with steps ending
        # in a special end checkpoint

        storySteps = {s.id: s for s in self.story_steps}

        # collect all overlapping checkpoints
        # we will remove unused begin ones
        allOverlappingCps = set()

        if self.cyclic_edge_ids:
            # we are going to do this in a recursive way. we are going to
            # remove one cycle and then we are going to
            # let the cycle detection run again
            # this is not inherently necessary so if this becomes a performance
            # issue, we can change it. It is actually enough to run the cycle
            # detection only once and then remove one cycle after another, but
            # since removing the cycle is done by adding / removing edges and
            #  nodes
            # the logic is a lot easier if we only need to make sure the
            # change is consistent if we only change one compared to
            # changing all of them.

            for s, e in cyclicEdgeIds:
                cid = generateId(max_chars=generatedHashLength)
                affix = generatedCheckpointPrefix + checkpointCyclePrefix
                # need abbreviations otherwise they are not visualized well
                sinkCpName = affix + "SINK_" + cid
                connectorCpName = affix + "CONN_" + cid
                sourceCpName = affix + "SRC_" + cid
                storyEndCheckpoints[sinkCpName] = sourceCpName

                overlappingCps = self.overlappingCheckpointNames(
                    storySteps[s].end_checkpoints, storySteps[e].start_checkpoints
                )

                allOverlappingCps.update(overlappingCps)

                # change end checkpoints of starts
                begin = storySteps[s].createCopy(use_new_id=False)
                begin.end_checkpoints = [
                    cp for cp in begin.end_checkpoints if cp.name not in overlappingCps
                ]
                begin.end_checkpoints.append(Inspection(sinkCpName))
                storySteps[s] = begin

                needsConnector = False

                for k, step in list(storySteps.items()):
                    additionalEnds = []
                    for original_cp in overlappingCps:
                        for cp in step.start_checkpoints:
                            if cp.name == original_cp:
                                if k == e:
                                    cpName = sourceCpName
                                else:
                                    cpName = connectorCpName
                                    needsConnector = True

                                if not self.isCheckpointInList(
                                    cpName, cp.conditions, step.start_checkpoints
                                ):
                                    # add checkpoint only if it was not added
                                    additionalEnds.append(
                                        Inspection(cpName, cp.conditions)
                                    )

                    if additionalEnds:
                        changed = step.createCopy(use_new_id=False)
                        changed.start_checkpoints.extend(additionalEnds)
                        storySteps[k] = changed

                if needsConnector:
                    begin.end_checkpoints.append(Inspection(connectorCpName ))

        # the process above may generate unused checkpoints
        # we need to find them and remove them
        self.removeUnusedGeneratedCps(
            storySteps, allOverlappingCps, storyEndCheckpoints
        )

        return StoryPlot(list(storySteps.values()), storyEndCheckpoints)

    @staticmethod
    def checkpointDifference(
        cps: List[Inspection], cp_name_to_ignore: Set[Text]
    ) -> List[Inspection]:
        """Finds checkpoints which names are
        different form names of checkpoints to ignore"""

        return [cp for cp in cps if cp.name not in cp_name_to_ignore]

    def removeUnusedGeneratedCps(
        self,
        story_steps: Dict[Text, StoryStage],
        overlapping_cps: Set[Text],
        story_end_checkpoints: Dict[Text, Text],
    ) -> None:
        """Finds unused generated checkpoints
        and remove them from story steps."""

        unusedCps = self.findUnusedCheckpoints(
            story_steps.values(), story_end_checkpoints
        )

        unusedOverlappingCps = unusedCps.intersection(overlapping_cps)

        unusedGenrCps = {
            cp_name
            for cp_name in unusedCps
            if cp_name.startswith(generatedCheckpointPrefix)
        }

        kToRemove = set()
        for k, step in story_steps.items():
            # changed all ends
            changed = step.createCopy(use_new_id=False)
            changed.start_checkpoints = self.checkpointDifference(
                changed.start_checkpoints, unusedOverlappingCps
            )

            # remove generated unused end checkpoints
            changed.end_checkpoints = self.checkpointDifference(
                changed.end_checkpoints, unusedGenrCps
            )

            if (
                step.start_checkpoints
                and not changed.start_checkpoints
                or step.end_checkpoints
                and not changed.end_checkpoints
            ):
                # remove story step if the generated checkpoints
                # were the only ones
                kToRemove.add(k)

            story_steps[k] = changed

        # remove unwanted story steps
        for k in kToRemove:
            del story_steps[k]

    @staticmethod
    def isCheckpointInList(
        checkpoint_name: Text, conditions: Dict[Text, Any], cps: List[Inspection]
    ) -> bool:
        """Checks if checkpoint with name and conditions is
        already in the list of checkpoints."""

        for cp in cps:
            if checkpoint_name == cp.name and conditions == cp.conditions:
                return True
        return False

    @staticmethod
    def findUnusedCheckpoints(
        story_steps: ValuesView[StoryStage], story_end_checkpoints: Dict[Text, Text]
    ) -> Set[Text]:
        """Finds all unused checkpoints."""

        collectedStart = {storyEnd, storyStart}
        collectedEnd = {storyEnd, storyStart}

        for step in story_steps:
            for start in step.start_checkpoints:
                collectedStart.add(start.name)
            for end in step.end_checkpoints:
                startName= story_end_checkpoints.get(end.name, end.name)
                collectedEnd.add(startName)

        return collectedEnd.symmetric_difference(collectedStart)

    def get(self, step_id: Text) -> Optional[StoryStage]:
        """Looks a story step up by its id."""

        return self.step_lookup.get(step_id)

    def as_story_string(self) -> Text:
        """Convert the graph into the story file format."""

        storyContent = ""
        for step in self.story_steps:
            storyContent += step.as_story_string(flat=False)
        return storyContent

    @staticmethod
    def orderSteps(
        story_steps: List[StoryStage],
    ) -> Tuple[deque, List[Tuple[Text, Text]]]:
        """Topological sort of the steps returning the ids of the steps."""

        checkpointList = StoryPlot.groupByStartCheckpoint(story_steps)
        chart = {
            s.id: {
                others.id for end in s.end_checkpoints for others in checkpointList[end.name]
            }
            for s in story_steps
        }
        return StoryPlot.topologicalSort(chart)

    @staticmethod
    def groupByStartCheckpoint(
        story_steps: List[StoryStage],
    ) -> Dict[Text, List[StoryStage]]:
        """Returns all the start checkpoint of the steps"""

        checkpointList = defaultdict(list)
        for step in story_steps:
            for start in step.start_checkpoints:
                checkpointList[start.name].append(step)
        return checkpointList

    @staticmethod
    def topologicalSort(
        graph: Dict[Text, Set[Text]]
    ) -> Tuple[deque, List[Tuple[Text, Text]]]:
        """Creates a top sort of a directed graph. This is an unstable sorting!

        The function returns the sorted nodes as well as the edges that need
        to be removed from the graph to make it acyclic (and hence, sortable).

        The graph should be represented as a dictionary, e.g.:

        >>> example_graph = {
        ...         "a": set("b", "c", "d"),
        ...         "b": set(),
        ...         "c": set("d"),
        ...         "d": set(),
        ...         "e": set("f"),
        ...         "f": set()}
        >>> StoryPlot.topologicalSort(example_graph)
        (deque([u'e', u'f', u'a', u'c', u'd', u'b']), [])
        """

        # noinspection PyPep8Naming
        GRAY, BLACK = 0, 1

        order = deque()
        unProcessed = sorted(set(graph))
        visitedNodes = {}

        removedEdges = set()

        def DepthFirstSearch(node):
            visitedNodes[node] = GRAY
            for k in sorted(graph.get(node, set())):
                SearchKey = visitedNodes.get(k, None)
                if SearchKey == GRAY:
                    removedEdges.add((node, k))
                    continue
                if SearchKey == BLACK:
                    continue
                unProcessed.remove(k)
                DepthFirstSearch(k)
            order.appendleft(node)
            visitedNodes[node] = BLACK

        while unProcessed:
            DepthFirstSearch(unProcessed.pop())

        return order, sorted(removedEdges)

    def anticipate(self, output_file: Optional[Text] = None) -> "nx.MultiDiGraph":
        import networkx as nx
        from convo.shared.core.training_data import visualization
        from colorhash import ColorHash

        chart = nx.MultiDiGraph()
        nextNodeIndex = [0]
        nodeList = {"storyStart": 0, "STORY_END": -1}

        def ensureCheckpointIsDrawn(cp: Inspection) -> None:
            if cp.name not in nodeList:
                nextNodeIndex[0] += 1
                nodeList[cp.name] = nextNodeIndex[0]

                if cp.name.startswith(generatedCheckpointPrefix):
                    # colors generated checkpoints based on their hash
                    shade = ColorHash(cp.name[-generatedHashLength:]).hex
                    chart.add_node(
                        nextNodeIndex[0],
                        label=capLength(cp.name),
                        style="filled",
                        fillcolor=shade,
                    )
                else:
                    chart.add_node(nextNodeIndex[0], label=capLength(cp.name))

        chart.add_node(
            nodeList["storyStart"], label="START", fillcolor="green", style="filled"
        )
        chart.add_node(nodeList["STORY_END"], label="END", fillcolor="red", style="filled")

        for step in self.story_steps:
            nextNodeIndex[0] += 1
            stepIndex = nextNodeIndex[0]

            chart.add_node(
                nextNodeIndex[0],
                label=capLength(step.block_name),
                style="filled",
                fillcolor="lightblue",
                shape="rect",
            )

            for c in step.start_checkpoints:
                ensureCheckpointIsDrawn(c)
                chart.add_edge(nodeList[c.name], stepIndex)
            for c in step.end_checkpoints:
                ensureCheckpointIsDrawn(c)
                chart.add_edge(stepIndex, nodeList[c.name])

            if not step.end_checkpoints:
                chart.add_edge(stepIndex, nodeList["STORY_END"])

        if output_file:
            visualization.persist_graph(chart, output_file)

        return chart

    def is_empty(self) -> bool:
        """Checks if `StoryPlot` is empty."""

        return not self.story_steps


def generateId(prefix: Text = "", max_chars: Optional[int] = None) -> Text:
    """Generate a random UUID.

    Args:
        prefix: String to prefix the ID with.
        max_chars: Maximum number of characters.

    Returns:
        Generated random UUID.
    """
    import uuid

    fid = uuid.uuid4().hex
    if max_chars:
        fid = fid[:max_chars]

    return f"{prefix}{fid}"


def capLength(s: Text, char_limit: int = 20, append_ellipsis: bool = True) -> Text:
    """Makes sure the string doesn't exceed the passed char limit.

    Appends an ellipsis if the string is too long."""

    if len(s) > char_limit:
        if append_ellipsis:
            return s[: char_limit - 3] + "..."
        else:
            return s[:char_limit]
    else:
        return s
