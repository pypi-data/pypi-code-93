from collections import defaultdict, deque

import random
from typing import Any, Text, List, Dict, Optional, TYPE_CHECKING, Set

import convo.shared.utils.io
from convo.shared.core.constants import LISTEN_ACTION_NAME  
from convo.shared.core.domain import Domain
from convo.shared.core.events import UserUttered, ActionExecuted, Event
from convo.shared.nlu.interpreter import NaturalLangInterpreter, RegexInterpreter
from convo.shared.core.generator import TrainingDataSetGenerator
from convo.shared.core.training_data.structures import StoryPlot, StoryStage
from convo.shared.nlu.constants import (
    ATTRIBUTE_VALUE_ENTITY,
    INTENTION,
    TXT,
    ATTRIBUTE_TYPE_ENTITY,
    ENTITIES_NAME,
    KEY_INTENT_NAME,
)

if TYPE_CHECKING:
    from convo.shared.nlu.training_data.training_data import TrainingDataSet
    from convo.shared.nlu.training_data.message import Msg
    import networkx

edgeNoneLabel = "NONE"

startNodeId = 0
endNodeId = -1
tmpNodeId = -2

visualizationTemplatePath = "/visualization.html"


class UserMessageCreator:
    def __init__(self, nlu_training_data) -> None:
        self.nlu_training_data = nlu_training_data
        self.mapping = self.createReverseMapping(self.nlu_training_data)

    @staticmethod
    def createReverseMapping(
        data: "TrainingDataSet",
    ) -> Dict[Dict[Text, Any], List["Msg"]]:
        """Create a mapping from intent to messages

        This allows a faster intent lookup."""

        e = defaultdict(list)
        for example in data.training_examples:
            if example.get(INTENTION, {}) is not None:
                e[example.get(INTENTION, {})].append(example)
        return e

    @staticmethod
    def containsSameEntity(entities, e) -> bool:
        return entities.get(e.get(ATTRIBUTE_TYPE_ENTITY)) is None or entities.get(
            e.get(ATTRIBUTE_TYPE_ENTITY)
        ) != e.get(ATTRIBUTE_VALUE_ENTITY)

    def messageForData(self, structured_info: Dict[Text, Any]) -> Any:
        """Find a data sample with the same intent and entityList.

        Given the parsed data from a message (intent and entityList) finds a
        message in the data that has the same intent and entityList."""

        if structured_info.get(INTENTION) is not None:
            intentName = structured_info.get(INTENTION, {}).get(KEY_INTENT_NAME)
            usableExamples = self.mapping.get(intentName, [])[:]
            random.shuffle(usableExamples)
            for example in usableExamples:
                entityList = {
                    e.get(ATTRIBUTE_TYPE_ENTITY): e.get(ATTRIBUTE_VALUE_ENTITY)
                    for e in example.get(ENTITIES_NAME, [])
                }
                for e in structured_info.get(ENTITIES_NAME, []):
                    if self.containsSameEntity(entityList, e):
                        break
                else:
                    return example.get(TXT)
        return structured_info.get(TXT)


def fingerprintNode(graph, node, max_history) -> Set[Text]:
    """Fingerprint a node in a graph.

    Can be used to identify nodes that are similar and can be merged within the
    graph.
    Generates all convo_paths starting at `node` following the directed graph up to
    the length of `max_history`, and returns a set of strings describing the
    found convo_paths. If the fingerprint creation for two nodes results in the same
    sets these nodes are indistinguishable if we walk along the path and only
    recall max history number of nodes we have visited. Hence, if we randomly
    walk on our directed graph, always only remembering the end `max_history`
    nodes we have visited, we can never recall if we have visited node A or
    node B if both have the same fingerprint."""

    # the candidate list contains all node convo_paths that haven't been
    # extended till `max_history` length yet.
    candidateList = deque()
    candidateList.append([node])
    carrying_on = []
    while len(candidateList) > 0:
        member = candidateList.pop()
        end = member[-1]
        blank = True
        for _, succ_node in graph.out_edges(end):
            nextCandidate = member[:]
            nextCandidate.append(succ_node)
            # if the path is already long enough, we add it to the results,
            # otherwise we add it to the candidateList
            # that we still need to visit
            if len(nextCandidate) == max_history:
                carrying_on.append(nextCandidate)
            else:
                candidateList.append(nextCandidate)
            blank = False
        if blank:
            carrying_on.append(member)
    return {
        " - ".join([graph.nodes[node]["label"] for node in continuation])
        for continuation in carrying_on
    }


def incomingEdges(graph, node) -> set:
    return {(prev_node, k) for prev_node, _, k in graph.in_edges(node, keys=True)}


def outgoingEdges(graph, node) -> set:
    return {(succ_node, k) for _, succ_node, k in graph.out_edges(node, keys=True)}


def outgoingEdgesAreSimilar(graph, node_a, node_b) -> bool:
    """If the outgoing edges from the two nodes are similar enough,
    it doesn't matter if you are in a or b.

    As your path will be the same because the outgoing edges will lead you to
    the same nodes anyways."""

    neglected = {node_b, node_a}
    aEdges = {
        (target, k)
        for target, k in outgoingEdges(graph, node_a)
        if target not in neglected
    }
    bEdges = {
        (target, k)
        for target, k in outgoingEdges(graph, node_b)
        if target not in neglected
    }
    return aEdges == bEdges or not aEdges or not bEdges


def nodesAreEquivalent(graph, node_a, node_b, max_history) -> bool:
    """Decides if two nodes are equivalent based on their fingerprints."""
    return graph.nodes[node_a]["label"] == graph.nodes[node_b]["label"] and (
            outgoingEdgesAreSimilar(graph, node_a, node_b)
            or incomingEdges(graph, node_a) == incomingEdges(graph, node_b)
            or fingerprintNode(graph, node_a, max_history)
            == fingerprintNode(graph, node_b, max_history)
    )


def addEdge(graph, u, v, key_name, stage=None, **kwargs) -> None:
    """Adds an edge to the graph if the edge is not already present. Uses the
    label as the key."""

    if key_name is None:
        key_name = edgeNoneLabel

    if key_name == edgeNoneLabel:
        stage = ""

    if not graph.has_edge(u, v, key=edgeNoneLabel):
        graph.add_edge(u, v, key=key_name, label=stage, **kwargs)
    else:
        e = graph.get_edge_data(u, v, key=edgeNoneLabel)
        transferStyle(kwargs, e)


def transferStyle(source, target: Dict[Text, Any]) -> Dict[Text, Any]:
    """Copy over class names from source to target for all special classes.

    Used if a node is highlighted and merged with another node."""

    classes = source.get("class", "")

    specialClasses = {"dashed", "active"}

    if "class" not in target:
        target["class"] = ""

    for c in specialClasses:
        if c in classes and c not in target["class"]:
            target["class"] += " " + c

    target["class"] = target["class"].strip()
    return target


def mergeEquivalentNodes(graph, max_history) -> None:
    """Searches for equivalent nodes in the graph and merges them."""

    updated = True
    # every node merge changes the graph and can trigger previously
    # impossible node merges - we need to repeat until
    # the graph doesn't change anymore
    while updated:
        updated = False
        remainingNodeIds = [n for n in graph.nodes() if n > 0]
        for idx, i in enumerate(remainingNodeIds):
            if graph.has_node(i):
                # assumes node equivalence is cumulative
                for j in remainingNodeIds[idx + 1 :]:
                    if graph.has_node(j) and nodesAreEquivalent(
                        graph, i, j, max_history
                    ):
                        # make sure we keep special styles
                        transferStyle(
                            graph.nodes(data=True)[j], graph.nodes(data=True)[i]
                        )

                        updated = True
                        # moves all outgoing edges to the others node
                        jOutgoingEdges = list(
                            graph.out_edges(j, keys=True, data=True)
                        )
                        for _, succ_node, k, d in jOutgoingEdges:
                            addEdge(
                                graph,
                                i,
                                succ_node,
                                k,
                                d.get("label"),
                                **{"class": d.get("class", "")},
                            )
                            graph.remove_edge(j, succ_node)
                        # moves all incoming edges to the others node
                        jIncomingEdges = list(graph.in_edges(j, keys=True, data=True))
                        for prev_node, _, k, d in jIncomingEdges:
                            addEdge(
                                graph,
                                prev_node,
                                i,
                                k,
                                d.get("label"),
                                **{"class": d.get("class", "")},
                            )
                            graph.remove_edge(prev_node, j)
                        graph.remove_node(j)


async def replaceEdgeLabelsWithNodes(
    graph, succeeding_id, interpreter, nlu_training_data
) -> None:
    """User messages are created as edge labels. This removes the labels and
    creates nodes instead.

    The algorithms (e.g. merge) are simpler if the user messages are labels
    on the edgeList. But it sometimes
    looks better if in the final graphs the user messages are nodes instead
    of edge labels."""

    if nlu_training_data:
        messageGenerator = UserMessageCreator(nlu_training_data)
    else:
        messageGenerator = None

    edgeList = list(graph.edges(keys=True, data=True))
    for s, e, k, d in edgeList:
        if k != edgeNoneLabel:
            if messageGenerator and d.get("label", k) is not None:
                parsedInfo = await interpreter.parse_func(d.get("label", k))
                stage = messageGenerator.messageForData(parsedInfo)
            else:
                stage = d.get("label", k)
            succeeding_id += 1
            graph.remove_edge(s, e, k)
            graph.add_node(
                succeeding_id,
                label=stage,
                shape="rect",
                style="filled",
                fillcolor="lightblue",
                **transferStyle(d, {"class": "intent"}),
            )
            graph.add_edge(s, succeeding_id, **{"class": d.get("class", "")})
            graph.add_edge(succeeding_id, e, **{"class": d.get("class", "")})


def visualizationHtmlPath() -> Text:
    import pkg_resources

    return pkg_resources.resource_filename(__name__, visualizationTemplatePath)


def persist_graph(graph: "networkx.Graph", output_file: Text) -> None:
    """Plots the graph and persists it into a html file."""
    import networkx as nx

    expg = nx.nx_pydot.to_pydot(graph)

    template_file = convo.shared.utils.io.read_file(visualizationHtmlPath())

    # Insert graph into template
    template_file = template_file.replace("// { is-client }", "isClient = true", 1)
    graphAsText = expg.to_string()
    # escape backslashes
    graphAsText = graphAsText.replace("\\", "\\\\")
    template_file = template_file.replace("// { graph-content }", f"graph = `{graphAsText}`", 1)

    convo.shared.utils.io.writing_text_file(template_file, output_file)


def lengthOfCommonActionPrefix(this: List[Event], others: List[Event]) -> int:
    """Calculate number of actions that two conversations have in common."""

    numCommonActions = 0
    tCleaned = [e for e in this if e.type_name in {"user", "action"}]
    oCleaned = [e for e in others if e.type_name in {"user", "action"}]

    for i, e in enumerate(tCleaned):
        if i == len(oCleaned):
            break
        elif isinstance(e, UserUttered) and isinstance(oCleaned[i], UserUttered):
            continue
        elif (
                isinstance(e, ActionExecuted)
                and isinstance(oCleaned[i], ActionExecuted)
                and oCleaned[i].action_name == e.action_name
        ):
            numCommonActions += 1
        else:
            break
    return numCommonActions


def addDefaultNodes(graph: "networkx.MultiDiGraph", fontsize: int = 12) -> None:
    """Add the standard nodes we need."""

    graph.add_node(
        startNodeId,
        label="START",
        fillcolor="green",
        style="filled",
        fontsize=fontsize,
        **{"class": "start active"},
    )
    graph.add_node(
        endNodeId,
        label="END",
        fillcolor="red",
        style="filled",
        fontsize=fontsize,
        **{"class": "end"},
    )
    graph.add_node(tmpNodeId, label="TMP", style="invis", **{"class": "invisible"})


def createGraph(fontsize: int = 12) -> "networkx.MultiDiGraph":
    """Create a graph and adds the default nodes."""

    import networkx as nx

    graph = nx.MultiDiGraph()
    addDefaultNodes(graph, fontsize)
    return graph


def addMessageEdge(
    graph: "networkx.MultiDiGraph",
    message: Optional[Dict[Text, Any]],
    current_node: int,
    next_node_idx: int,
    is_current: bool,
):
    """Create an edge based on the user message."""

    if message:
        messageKey = message.get("intent", {}).get("name", None)
        messageLabel = message.get("text", None)
    else:
        messageKey = None
        messageLabel = None

    addEdge(
        graph,
        current_node,
        next_node_idx,
        messageKey,
        messageLabel,
        **{"class": "active" if is_current else ""},
    )


async def visualizeNeighborhood(
    current: Optional[List[Event]],
    event_sequences: List[List[Event]],
    output_file: Optional[Text] = None,
    max_history: int = 2,
    interpreter: NaturalLangInterpreter = RegexInterpreter(),
    nlu_training_data: Optional["TrainingDataSet"] = None,
    should_merge_nodes: bool = True,
    max_distance: int = 1,
    fontsize: int = 12,
):
    """Given a set of event lists, visualizing the flows."""

    chart = createGraph(fontsize)
    addDefaultNodes(chart)

    nextNodeIndex = startNodeId
    specialNodeIndex = -3
    pathEllipsisEnds = set()

    for events in event_sequences:
        if current and max_distance:
            affix = lengthOfCommonActionPrefix(current, events)
        else:
            affix = len(events)

        msg = None
        currentNode = startNodeId
        index = 0
        isCurrent = events == current

        for index, el in enumerate(events):
            if not affix:
                index -= 1
                break
            if isinstance(el, UserUttered):
                if not el.intent:
                    msg = await interpreter.parse_func(el.text)
                else:
                    msg = el.parse_data
            elif (
                    isinstance(el, ActionExecuted) and el.action_name != LISTEN_ACTION_NAME
            ):
                nextNodeIndex += 1
                chart.add_node(
                    nextNodeIndex,
                    label=el.action_name,
                    fontsize=fontsize,
                    **{"class": "active" if isCurrent else ""},
                )

                addMessageEdge(
                    chart, msg, currentNode, nextNodeIndex, isCurrent
                )
                currentNode = nextNodeIndex

                msg = None
                affix -= 1

        # determine what the end node of the conversation is going to be
        # this can either be an ellipsis "...", the conversation end node
        # "END" or a "TMP" node if this is the active conversation
        if isCurrent:
            if (
                isinstance(events[index], ActionExecuted)
                and events[index].action_name == LISTEN_ACTION_NAME
            ):
                nextNodeIndex += 1
                chart.add_node(
                    nextNodeIndex,
                    label="  ?  "
                    if not msg
                    else msg.get("intent", {}).get("name", "  ?  "),
                    shape="rect",
                    **{"class": "intent dashed active"},
                )
                objective = nextNodeIndex
            elif currentNode:
                d = chart.nodes(data=True)[currentNode]
                d["class"] = "dashed active"
                objective = tmpNodeId
            else:
                objective = tmpNodeId
        elif index == len(events) - 1:
            objective = endNodeId
        elif currentNode and currentNode not in pathEllipsisEnds:
            chart.add_node(specialNodeIndex, label="...", **{"class": "ellipsis"})
            objective = specialNodeIndex
            pathEllipsisEnds.add(currentNode)
            specialNodeIndex -= 1
        else:
            objective = endNodeId

        addMessageEdge(chart, msg, currentNode, objective, isCurrent)

    if should_merge_nodes:
        mergeEquivalentNodes(chart, max_history)
    await replaceEdgeLabelsWithNodes(
        chart, nextNodeIndex, interpreter, nlu_training_data
    )

    removeAuxiliaryNodes(chart, specialNodeIndex)

    if output_file:
        persist_graph(chart, output_file)
    return chart


def removeAuxiliaryNodes(
    graph: "networkx.MultiDiGraph", special_node_idx: int
) -> None:
    """Remove any temporary or unused nodes."""

    graph.remove_node(tmpNodeId)

    if not len(list(graph.predecessors(endNodeId))):
        graph.remove_node(endNodeId)

    # remove duplicated "..." nodes after merge
    ps = set()
    for i in range(special_node_idx + 1, tmpNodeId):
        for pred in list(graph.predecessors(i)):
            if pred in ps:
                graph.remove_node(i)
            else:
                ps.add(pred)


async def imaginary_stories(
    story_steps: List[StoryStage],
    domain: Domain,
    output_file: Optional[Text],
    max_history: int,
    interpreter: NaturalLangInterpreter = RegexInterpreter(),
    nlu_training_data: Optional["TrainingDataSet"] = None,
    should_merge_nodes: bool = True,
    fontsize: int = 12,
):
    """Given a set of stories, generates a graph visualizing the flows in the
    stories.

    Visualization is always a trade off between making the graph as small as
    possible while
    at the same time making sure the meaning doesn't change to "much". The
    algorithm will
    compress the graph generated from the stories to merge nodes that are
    similar. Hence,
    the algorithm might create convo_paths through the graph that aren't actually
    specified in the
    stories, but we try to minimize that.

    Output file defines if and where a file containing the plotted graph
    should be stored.

    The history defines how much 'memory' the graph has. This influences in
    which situations the
    algorithm will merge nodes. Nodes will only be merged if they are equal
    within the history, this
    means the larger the history is we take into account the less likely it
    is we merge any nodes.

    The training data parameter can be used to pass in a Convo NLU training
    data instance. It will
    be used to replace the user messages from the story file with actual
    messages from the training data."""

    storyGraph = StoryPlot(story_steps)

    f = TrainingDataSetGenerator(
        storyGraph,
        domain,
        use_story_concatenation=False,
        tracker_limit=100,
        augmentation_factor=0,
    )
    completedTrackers = f.create()
    eventSequences = [t.events for t in completedTrackers]

    graph = await visualizeNeighborhood(
        None,
        eventSequences,
        output_file,
        max_history,
        interpreter,
        nlu_training_data,
        should_merge_nodes,
        max_distance=1,
        fontsize=fontsize,
    )
    return graph
