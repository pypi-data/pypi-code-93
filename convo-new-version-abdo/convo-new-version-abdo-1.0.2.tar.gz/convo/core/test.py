import logging
import os
import warnings
import typing
from collections import defaultdict, namedtuple
from typing import Any, Dict, List, Optional, Text, Tuple

from convo import telemetry
import convo.shared.utils.io
from convo.core.channels import UserMsg
from convo.shared.core.training_data.story_writer.yaml_story_writer import (
    YAMLStoryAuthor,
)
from convo.shared.core.domain import Domain
from convo.nlu.constants import ENTITY_ATTR_TXT_STR
from convo.shared.nlu.constants import (
    INTENTION,
    ENTITIES_NAME,
    ATTRIBUTE_VALUE_ENTITY,
    ATTRIBUTE_START_ENTITY,
    ATTRIBUTE_END_ENTITY,
    EXTRACTOR,
    ATTRIBUTE_TYPE_ENTITY,
)
from convo.constants import OUTCOME_FILES, PERCENTAGE_WISE_KEY
from convo.shared.core.events import ActionExecuted, UserUttered
from convo.shared.core.trackers import DialogueStateTracer
from convo.shared.nlu.training_data.formats.readerwriter import TrainingDataAuthor
from convo.shared.utils.io import ENCODING_DEFAULT

if typing.TYPE_CHECKING:
    from convo.core.agent import CoreAgent
    from convo.core.processor import MsgProcessor
    from convo.shared.core.generator import TrainingDataSetGenerator


CONFUSION_MATRIX_STORY_FILE_NAME = "story_confusion_matrix.png"
REPORT_STORIES_FILE_NAME = "story_report.json"
FAILED_STORIES_FILE_NAME = "failed_test_stories.yml"
SUCCESSFUL_STORIES_FILE_NAME = "successful_test_stories.yml"


log = logging.getLogger(__name__)

StoryAnalysis = namedtuple(
    "StoryEvaluation",
    [
        "evaluation_store",
        "failed_stories",
        "successful_stories",
        "action_list",
        "in_training_data_fraction",
    ],
)


class EvaluationStorage:
    """Class storing action, intent and entity predictions and targets."""

    def __init__(
        self,
        action_predictions: Optional[List[Text]] = None,
        action_targets: Optional[List[Text]] = None,
        intent_predictions: Optional[List[Text]] = None,
        intent_targets: Optional[List[Text]] = None,
        entity_predictions: Optional[List[Dict[Text, Any]]] = None,
        entity_targets: Optional[List[Dict[Text, Any]]] = None,
    ) -> None:
        self.action_predictions = action_predictions or []
        self.action_targets = action_targets or []
        self.intent_predictions = intent_predictions or []
        self.intent_targets = intent_targets or []
        self.entity_predictions = entity_predictions or []
        self.entity_targets = entity_targets or []

    def append_to_store(
        self,
        action_predictions: Optional[List[Text]] = None,
        action_targets: Optional[List[Text]] = None,
        intent_predictions: Optional[List[Text]] = None,
        intent_targets: Optional[List[Text]] = None,
        entity_predictions: Optional[List[Dict[Text, Any]]] = None,
        entity_targets: Optional[List[Dict[Text, Any]]] = None,
    ) -> None:
        """Add items or lists of items to the store"""

        self.action_predictions.extend(action_predictions or [])
        self.action_targets.extend(action_targets or [])
        self.intent_targets.extend(intent_targets or [])
        self.intent_predictions.extend(intent_predictions or [])
        self.entity_predictions.extend(entity_predictions or [])
        self.entity_targets.extend(entity_targets or [])

    def join_store(self, others: "EvaluationStorage") -> None:
        """Add the contents of others to self"""
        self.append_to_store(
            action_predictions=others.action_predictions,
            action_targets=others.action_targets,
            intent_predictions=others.intent_predictions,
            intent_targets=others.intent_targets,
            entity_predictions=others.entity_predictions,
            entity_targets=others.entity_targets,
        )

    def had_forecast_target_mismatch(self) -> bool:
        return (
            self.intent_predictions != self.intent_targets
            or self.entity_predictions != self.entity_targets
            or self.action_predictions != self.action_targets
        )

    @staticmethod
    def _compare_entities_feature(
        entity_predictions: List[Dict[Text, Any]],
        entity_targets: List[Dict[Text, Any]],
        i_pred: int,
        i_target: int,
    ) -> int:
        """
        Compare the current predicted and target entities and decide which one
        comes first. If the predicted entity comes first it returns -1,
        while it returns 1 if the target entity comes first.
        If target and predicted are aligned it returns 0
        """
        prediction = None
        goal = None
        if i_pred < len(entity_predictions):
            prediction = entity_predictions[i_pred]
        if i_target < len(entity_targets):
            goal = entity_targets[i_target]
        if goal and prediction:
            # Check which entity has the lower "start" value
            if prediction.get("start") < goal.get("start"):
                return -1
            elif goal.get("start") < prediction.get("start"):
                return 1
            else:
                # Since both have the same "start" values,
                # check which one has the lower "end" value
                if prediction.get("end") < goal.get("end"):
                    return -1
                elif goal.get("end") < prediction.get("end"):
                    return 1
                else:
                    # The entities have the same "start" and "end" values
                    return 0
        return 1 if goal else -1

    @staticmethod
    def _create_entity_training_data_set(entity: Dict[Text, Any]) -> Text:
        return TrainingDataAuthor.generating_entity(entity.get("text"), entity)

    def serialise_data(self) -> Tuple[List[Text], List[Text]]:
        """Turn targets and predictions to lists of equal size for sklearn."""
        txt = sorted(
            list(
                set(
                    [e.get("text") for e in self.entity_targets]
                    + [e.get("text") for e in self.entity_predictions]
                )
            )
        )

        range_entity_goals = []
        range_entity_predictions = []

        for text in txt:
            # sort the entities of this sentence to compare them directly
            entity_goals = sorted(
                filter(lambda x: x.get("text") == text, self.entity_targets),
                key=lambda x: x.get("start"),
            )
            entity_forecasts = sorted(
                filter(lambda x: x.get("text") == text, self.entity_predictions),
                key=lambda x: x.get("start"),
            )

            i_prediction, i_goal = 0, 0

            while i_prediction < len(entity_forecasts) or i_goal < len(entity_goals):
                cmp = self._compare_entities_feature(
                    entity_forecasts, entity_goals, i_prediction, i_goal
                )
                if cmp == -1:  # predicted comes first
                    range_entity_predictions.append(
                        self._create_entity_training_data_set(entity_forecasts[i_prediction])
                    )
                    range_entity_goals.append("None")
                    i_prediction += 1
                elif cmp == 1:  # target entity comes first
                    range_entity_goals.append(
                        self._create_entity_training_data_set(entity_goals[i_goal])
                    )
                    range_entity_predictions.append("None")
                    i_goal += 1
                else:  # target and predicted entity are aligned
                    range_entity_predictions.append(
                        self._create_entity_training_data_set(entity_forecasts[i_prediction])
                    )
                    range_entity_goals.append(
                        self._create_entity_training_data_set(entity_goals[i_goal])
                    )
                    i_prediction += 1
                    i_goal += 1

        goals = self.action_targets + self.intent_targets + range_entity_goals

        forecasts = (
            self.action_predictions
            + self.intent_predictions
            + range_entity_predictions
        )
        return goals, forecasts


class WronglyPredictedAct(ActionExecuted):
    """The model predicted the wrong action.

    Mostly used to mark wrong predictions and be able to
    dump them as stories."""

    type_name = "wrong_action"

    def __init__(
        self,
        action_name_target: Text,
        action_name_prediction: Text,
        policy: Optional[Text] = None,
        confidence: Optional[float] = None,
        timestamp: Optional[float] = None,
        metadata: Optional[Dict] = None,
    ) -> None:
        self.action_name_prediction = action_name_prediction
        super().__init__(action_name_target, policy, confidence, timestamp, metadata)

    def in_line_comment(self) -> Text:
        """A comment attached to this event. Used during dumping."""
        return f"predicted: {self.action_name_prediction}"

    def as_story_string(self) -> Text:
        return f"{self.action_name}   <!-- {self.in_line_comment()} -->"


class EndToEndUserRemark(UserUttered):
    """End-to-end user utterance.

    Mostly used to print the full end-to-end user message in the
    `failed_test_stories.yml` output file."""

    def as_story_string(self, e2e: bool = True) -> Text:
        return super().as_story_string(e2e=True)


class IncorrectClassifiedUserUtterance(UserUttered):
    """The NLU model predicted the wrong user utterance.

    Mostly used to mark wrong predictions and be able to
    dump them as stories."""

    type_name = "wrong_utterance"

    def __init__(self, event: UserUttered, eval_store: EvaluationStorage) -> None:

        if not eval_store.intent_predictions:
            self.predicted_intent = None
        else:
            self.predicted_intent = eval_store.intent_predictions[0]
        self.predicted_entities = eval_store.entity_predictions

        intention = {"name": eval_store.intent_targets[0]}

        super().__init__(
            event.text,
            intention,
            eval_store.entity_targets,
            event.parse_data,
            event.timestamp,
            event.input_channel,
        )

    def in_line_comment(self) -> Text:
        """A comment attached to this event. Used during dumping."""
        from convo.shared.core.events import md_format_message

        forecasted_msg = md_format_message(
            self.text, self.predicted_intent, self.predicted_entities
        )
        return f"predicted: {self.predicted_intent}: {forecasted_msg}"

    def as_story_string(self, e2e: bool = True) -> Text:
        from convo.shared.core.events import md_format_message

        correct_msg = md_format_message(
            self.text, self.intent.get("name"), self.entities
        )
        return (
            f"{self.intent.get('name')}: {correct_msg}   "
            f"<!-- {self.in_line_comment()} -->"
        )


async def _create_data_set_generator(
    resource_name: Text,
    agent: "CoreAgent",
    max_stories: Optional[int] = None,
    use_e2e: bool = False,
) -> "TrainingDataSetGenerator":
    from convo.shared.core.generator import TrainingDataSetGenerator

    from convo.core import training

    graph_of_story = await training.extract_story_graph(
        resource_name, agent.domain, use_e2e
    )
    return TrainingDataSetGenerator(
        graph_of_story,
        agent.domain,
        use_story_concatenation=False,
        augmentation_factor=0,
        tracker_limit=max_stories,
    )


def _clean_entity_output(
    text: Text, entity_results: List[Dict[Text, Any]]
) -> List[Dict[Text, Any]]:
    """Extract only the token variables from an entity dict."""
    cleaned_up_entities = []

    for r in tuple(entity_results):
        cleaned_up_entity = {ENTITY_ATTR_TXT_STR: text}
        for k in (
            ATTRIBUTE_START_ENTITY,
            ATTRIBUTE_END_ENTITY,
            ATTRIBUTE_TYPE_ENTITY,
            ATTRIBUTE_VALUE_ENTITY,
        ):
            if k in set(r):
                if k == ATTRIBUTE_VALUE_ENTITY and EXTRACTOR in set(r):
                    # convert values to strings for evaluation as
                    # target values are all of type string
                    r[k] = str(r[k])
                cleaned_up_entity[k] = r[k]
        cleaned_up_entities.append(cleaned_up_entity)

    return cleaned_up_entities


def _assemble_user_uttered_predictions(
    event: UserUttered,
    predicted: Dict[Text, Any],
    partial_tracker: DialogueStateTracer,
    fail_on_prediction_errors: bool,
) -> EvaluationStorage:
    user_uttered_evaluation_store = EvaluationStorage()

    gold_intent = event.intent.get("name")
    forecast_intent = predicted.get(INTENTION, {}).get("name")

    user_uttered_evaluation_store.append_to_store(
        intent_predictions=[forecast_intent], intent_targets=[gold_intent]
    )

    gold_intent = event.entities
    forecasted_entities = predicted.get(ENTITIES_NAME)

    if gold_intent or forecasted_entities:
        user_uttered_evaluation_store.append_to_store(
            entity_targets=_clean_entity_output(event.text, gold_intent),
            entity_predictions=_clean_entity_output(event.text, forecasted_entities),
        )

    if user_uttered_evaluation_store.had_forecast_target_mismatch():
        partial_tracker.update(
            IncorrectClassifiedUserUtterance(event, user_uttered_evaluation_store)
        )
        if fail_on_prediction_errors:
            raise ValueError(
                "NLU model predicted a wrong intent. Failed Story:"
                " \n\n{}".format(
                    YAMLStoryAuthor().data_dumps(partial_tracker.as_story().story_steps)
                )
            )
    else:
        end_to_end_user_remark = EndToEndUserRemark(
            event.text, event.intent, event.entities
        )
        partial_tracker.update(end_to_end_user_remark)

    return user_uttered_evaluation_store


def copy_loop_rejection(partial_tracker: DialogueStateTracer) -> None:
    """Add `ActExecutionRejected` event to the tracker.

    During evaluation, we don't run action server, therefore in order to correctly
    test unhappy convo_paths of the loops, we need to emulate loop rejection.

    Args:
        partial_tracker: a :class:`convo.core.trackers.DialogueStateTracer`
    """
    from convo.shared.core.events import ActExecutionRejected

    rejected_action_name: Text = partial_tracker.activeLoopName
    partial_tracker.update(ActExecutionRejected(rejected_action_name))


def _assemble_act_executed_forecast(
    processor: "MsgProcessor",
    partial_tracker: DialogueStateTracer,
    event: ActionExecuted,
    fail_on_prediction_errors: bool,
    circuit_breaker_tripped: bool,
) -> Tuple[EvaluationStorage, Optional[Text], Optional[float]]:
    from convo.core.policies.form_policy import FormPolicy

    act_executed_evaluation_store = EvaluationStorage()

    gold = event.action_name or event.action_text

    if circuit_breaker_tripped:
        forecasted = "circuit breaker tripped"
        guideline = None
        confidence = None
    else:
        act, guideline, confidence = processor.forecast_next_act(partial_tracker)
        forecasted = act.name()

        if (
            guideline
            and forecasted != gold
            and _form_might_had_rejected(
                processor.domain, partial_tracker, forecasted
            )
        ):
            # Wrong action was predicted,
            # but it might be Ok if form action is rejected.
            copy_loop_rejection(partial_tracker)
            # try again
            act, guideline, confidence = processor.forecast_next_act(partial_tracker)

            # Even if the prediction is also wrong, we don't have to undo the emulation
            # of the action rejection as we know that the user explicitly specified
            # that something else than the form was supposed to run.
            forecasted = act.name()

    act_executed_evaluation_store.append_to_store(
        action_predictions=[forecasted], action_targets=[gold]
    )

    if act_executed_evaluation_store.had_forecast_target_mismatch():
        partial_tracker.update(
            WronglyPredictedAct(
                gold, forecasted, event.policy, event.confidence, event.timestamp
            )
        )
        if fail_on_prediction_errors:
            error_message = (
                "Model predicted a wrong action. Failed Story: "
                "\n\n{}".format(
                    YAMLStoryAuthor().data_dumps(partial_tracker.as_story().story_steps)
                )
            )
            if FormPolicy.__name__ in guideline:
                error_message += (
                    "FormAction is not run during "
                    "evaluation therefore it is impossible to know "
                    "if validation failed or this story is wrong. "
                    "If the story is correct, add it to the "
                    "training stories and retrain."
                )
            raise ValueError(error_message)
    else:
        partial_tracker.update(event)

    return act_executed_evaluation_store, guideline, confidence


def _form_might_had_rejected(
    domain: Domain, tracker: DialogueStateTracer, predicted_action_name: Text
) -> bool:
    return (
            tracker.activeLoopName == predicted_action_name
            and predicted_action_name in domain.form_names
    )


async def _forecast_tracker_act(
    tracker: DialogueStateTracer,
    agent: "CoreAgent",
    fail_on_prediction_errors: bool = False,
    use_e2e: bool = False,
) -> Tuple[EvaluationStorage, DialogueStateTracer, List[Dict[Text, Any]]]:

    test_processor = agent.create_processor()
    tracker_evaluation_store = EvaluationStorage()

    events = list(tracker.events)

    limited_tracker = DialogueStateTracer.from_events_tracker(
        tracker.sender_id,
        events[:1],
        agent.domain.slots,
        sender_source=tracker.sender_source,
    )

    tracker_acts = []
    shall_forecast_another_act = True
    num_forecasted_acts = 0

    for event in events[1:]:
        if isinstance(event, ActionExecuted):
            circuit_breaker_tripped = test_processor.is_act_limit_reached(
                num_forecasted_acts, shall_forecast_another_act
            )
            (
                action_executed_result,
                policy,
                confidence,
            ) = _assemble_act_executed_forecast(
                test_processor,
                limited_tracker,
                event,
                fail_on_prediction_errors,
                circuit_breaker_tripped,
            )
            tracker_evaluation_store.join_store(action_executed_result)
            tracker_acts.append(
                {
                    "action": action_executed_result.action_targets[0],
                    "predicted": action_executed_result.action_predictions[0],
                    "policy": policy,
                    "confidence": confidence,
                }
            )
            shall_forecast_another_act = test_processor.should_forecast_another_act(
                action_executed_result.action_predictions[0]
            )
            num_forecasted_acts += 1

        elif use_e2e and isinstance(event, UserUttered):
            # This means that user utterance didn't have a user message, only intent,
            # so we can skip the NLU part and take the parse data directly.
            # Indirectly that means that the test story was in YAML format.
            if not event.text:
                forecasted = event.parse_data
            # Indirectly that means that the test story was in Markdown format.
            # Leaving that as it is because Markdown is in legacy mode.
            else:
                forecasted = await test_processor.parse_msg(UserMsg(event.text))
            user_uttered_output = _assemble_user_uttered_predictions(
                event, forecasted, limited_tracker, fail_on_prediction_errors
            )

            tracker_evaluation_store.join_store(user_uttered_output)
        else:
            limited_tracker.update(event)
        if isinstance(event, UserUttered):
            num_forecasted_acts = 0

    return tracker_evaluation_store, limited_tracker, tracker_acts


def _in_training_data_set_fraction(action_list: List[Dict[Text, Any]]) -> float:
    """Given a list of action items, returns the fraction of actions

    that were predicted using one of the Memoization policies."""
    from convo.core.policies.ensemble import SimplePolicyEnsemble

    in_training_data_set = [
        a["action"]
        for a in action_list
        if a["policy"] and not SimplePolicyEnsemble.is_not_memo_policy(a["policy"])
    ]

    return len(in_training_data_set) / len(action_list) if action_list else 0


async def _assemble_story_forecasts(
    completed_trackers: List["DialogueStateTracer"],
    agent: "CoreAgent",
    fail_on_prediction_errors: bool = False,
    use_e2e: bool = False,
) -> Tuple[StoryAnalysis, int]:
    """Test the stories from a file, running them through the stored model."""
    from convo.test import fetch_evaluation_metrics
    from tqdm import tqdm

    story_evaluation_store = EvaluationStorage()
    unsuccessful = []
    completed = []
    right_dialogues = []
    no_of_story = len(completed_trackers)

    log.info(f"Evaluating {no_of_story} stories\nProgress:")

    act_list = []

    for tracker in tqdm(completed_trackers):
        (
            tracker_results,
            predicted_tracker,
            tracker_actions,
        ) = await _forecast_tracker_act(
            tracker, agent, fail_on_prediction_errors, use_e2e
        )

        story_evaluation_store.join_store(tracker_results)

        act_list.extend(tracker_actions)

        if tracker_results.had_forecast_target_mismatch():
            # there is at least one wrong prediction
            unsuccessful.append(predicted_tracker)
            right_dialogues.append(0)
        else:
            right_dialogues.append(1)
            completed.append(predicted_tracker)

    log.info("Finished collecting predictions.")
    with warnings.catch_warnings():
        from sklearn.exceptions import UndefinedMetricWarning

        warnings.simplefilter("ignore", UndefinedMetricWarning)
        report, precision, f1, accuracy = fetch_evaluation_metrics(
            [1] * len(completed_trackers), right_dialogues
        )

    in_training_data_set_fraction = _in_training_data_set_fraction(act_list)

    _log_analysis_table(
        [1] * len(completed_trackers),
        "END-TO-END" if use_e2e else "CONVERSATION",
        report,
        precision,
        f1,
        accuracy,
        in_training_data_set_fraction,
        include_report=False,
    )

    return (
        StoryAnalysis(
            evaluation_store=story_evaluation_store,
            failed_stories=unsuccessful,
            successful_stories=completed,
            action_list=act_list,
            in_training_data_fraction=in_training_data_set_fraction,
        ),
        no_of_story,
    )


def _story_log(trackers: List[DialogueStateTracer], file_path: Text) -> None:
    """Write given stories to the given file."""

    with open(file_path, "w", encoding=ENCODING_DEFAULT) as f:
        if not trackers:
            f.write("# None of the test stories failed - all good!")
        else:
            stories = [tracker.as_story(include_source=True) for tracker in trackers]
            steps = [step for story in stories for step in story.story_steps]
            f.write(YAMLStoryAuthor().data_dumps(steps))


async def test(
    stories: Text,
    agent: "CoreAgent",
    max_stories: Optional[int] = None,
    out_directory: Optional[Text] = None,
    fail_on_prediction_errors: bool = False,
    e2e: bool = False,
    disable_plotting: bool = False,
    successes: bool = False,
    errors: bool = True,
) -> Dict[Text, Any]:
    """Run the evaluation of the stories, optionally plot the results.

    Args:
        stories: the stories to evaluate on
        agent: the agent
        max_stories: maximum number of stories to consider
        out_directory: path to dir to results to
        fail_on_prediction_errors: boolean indicating whether to fail on prediction
            errors or not
        e2e: boolean indicating whether to use end to end evaluation or not
        disable_plotting: boolean indicating whether to disable plotting or not
        successes: boolean indicating whether to write down successful predictions or
            not
        errors: boolean indicating whether to write down incorrect predictions or not

    Returns:
        Evaluation summary.
    """
    from convo.test import fetch_evaluation_metrics

    test_generator = await _create_data_set_generator(stories, agent, max_stories, e2e)
    trackers_done = test_generator.story_trackers_generation()

    store_analysis, _ = await _assemble_story_forecasts(
        trackers_done, agent, fail_on_prediction_errors, e2e
    )

    evaluation_store = store_analysis.evaluation_store

    with warnings.catch_warnings():
        from sklearn.exceptions import UndefinedMetricWarning

        warnings.simplefilter("ignore", UndefinedMetricWarning)

        goals, forecasts = evaluation_store.serialise_data()

        if out_directory:
            result, exactness, f1_key, correctness = fetch_evaluation_metrics(
                goals, forecasts, output_dict=True
            )

            result_file_name = os.path.join(out_directory, REPORT_STORIES_FILE_NAME)
            convo.shared.utils.io.dump_object_as_json_to_file(result_file_name, result)
            log.info(f"Stories report saved to {result_file_name}.")
        else:
            result, exactness, f1_key, correctness = fetch_evaluation_metrics(
                goals, forecasts, output_dict=True
            )

    telemetry.traverse_core_model_test(len(test_generator.story_graph.story_steps), e2e, agent)

    _log_analysis_table(
        evaluation_store.action_targets,
        "ACTION",
        result,
        exactness,
        f1_key,
        correctness,
        store_analysis.in_training_data_fraction,
        include_report=False,
    )

    if not disable_plotting and out_directory:
        _plot_story_analysis(
            evaluation_store.action_targets,
            evaluation_store.action_predictions,
            out_directory,
        )

    if errors and out_directory:
        _story_log(
            store_analysis.failed_stories,
            os.path.join(out_directory, FAILED_STORIES_FILE_NAME),
        )
    if successes and out_directory:
        _story_log(
            store_analysis.successful_stories,
            os.path.join(out_directory, SUCCESSFUL_STORIES_FILE_NAME),
        )

    return {
        "report": result,
        "precision": exactness,
        "f1": f1_key,
        "accuracy": correctness,
        "actions": store_analysis.action_list,
        "in_training_data_fraction": store_analysis.in_training_data_fraction,
        "is_end_to_end_evaluation": e2e,
    }


def _log_analysis_table(
    golds: List[Any],
    name: Text,
    report: Dict[Text, Any],
    precision: float,
    f1: float,
    accuracy: float,
    in_training_data_fraction: float,
    include_report: bool = True,
) -> None:  # pragma: no cover
    """Log the sklearn evaluation metrics."""
    log.info(f"Evaluation Results on {name} level:")
    log.info(f"\tCorrect:          {int(len(golds) * accuracy)} / {len(golds)}")
    log.info(f"\tF1-Score:         {f1:.3f}")
    log.info(f"\tPrecision:        {precision:.3f}")
    log.info(f"\tAccuracy:         {accuracy:.3f}")
    log.info(f"\tIn-data fraction: {in_training_data_fraction:.3g}")

    if include_report:
        log.info(f"\tClassification report: \n{report}")


def _plot_story_analysis(
    targets: List[Text], predictions: List[Text], output_directory: Optional[Text]
) -> None:
    """Plot a confusion matrix of story evaluation."""
    from sklearn.metrics import confusion_matrix
    from sklearn.utils.multiclass import unique_labels
    from convo.utils.plotting import matrix_plot_confusion

    confused_matrix_file_name = CONFUSION_MATRIX_STORY_FILE_NAME
    if output_directory:
        confused_matrix_file_name = os.path.join(
            output_directory, confused_matrix_file_name
        )

    cnf_matrix_file = confusion_matrix(targets, predictions)

    matrix_plot_confusion(
        cnf_matrix_file,
        classes=unique_labels(targets, predictions),
        title="Action Confusion matrix",
        output_file=confused_matrix_file_name,
    )


async def compare_models_in_dir(
    model_dir: Text, stories_file: Text, output: Text
) -> None:
    """Evaluate multiple trained models in a dir on a test set.

    Args:
        model_dir: path to dir that contains the models to evaluate
        stories_file: path to the story file
        output: output dir to store results to
    """
    no_right = defaultdict(list)

    for run in convo.shared.utils.io.list_sub_dirs(model_dir):
        number_correct_in_execution = defaultdict(list)

        for model in sorted(convo.shared.utils.io.listing_files(run)):
            if not model.endswith("tar.gz"):
                continue

            # The model files are named like <config-name>PERCENTAGE_WISE_KEY<number>.tar.gz
            # Remove the percentage key and number from the name to get the config name
            configuration_name = os.path.basename(model).split(PERCENTAGE_WISE_KEY)[0]
            no_of_right_story = await _analysis_core_model(model, stories_file)
            number_correct_in_execution[configuration_name].append(no_of_right_story)

        for k, v in number_correct_in_execution.items():
            no_right[k].append(v)

    convo.shared.utils.io.dump_object_as_json_to_file(
        os.path.join(output, OUTCOME_FILES), no_right
    )


async def differentiate_models(models: List[Text], stories_file: Text, output: Text) -> None:
    """Evaluate provided trained models on a test set.

    Args:
        models: list of trained model convo_paths
        stories_file: path to the story file
        output: output dir to store results to
    """
    no_right = defaultdict(list)

    for model in models:
        number_of_correct_stories = await _analysis_core_model(model, stories_file)
        no_right[os.path.basename(model)].append(number_of_correct_stories)

    convo.shared.utils.io.dump_object_as_json_to_file(
        os.path.join(output, OUTCOME_FILES), no_right
    )


async def _analysis_core_model(model: Text, stories_file: Text) -> int:
    from convo.core.agent import CoreAgent

    log.info(f"Evaluating model '{model}'")

    get_agent = CoreAgent.load(model)
    test_generator = await _create_data_set_generator(stories_file, get_agent)
    finished_trackers = test_generator.story_trackers_generation()
    story_evaluation_store, no_of_story = await _assemble_story_forecasts(
        finished_trackers, get_agent
    )
    unsuccessful_stories = story_evaluation_store.failed_stories
    return no_of_story - len(unsuccessful_stories)
