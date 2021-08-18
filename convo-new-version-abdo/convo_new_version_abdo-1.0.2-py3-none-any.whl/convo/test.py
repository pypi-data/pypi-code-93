import logging
import os
import typing
from typing import Text, Dict, Optional, List, Any, Iterable, Tuple, Union
from pathlib import Path

import convo.shared.utils.cli
import convo.shared.utils.common
import convo.shared.utils.io
import convo.utils.common
from convo.constants import OUTCOME_FILES, NO_OF_TRAINING_STORY_FILE
from convo.shared.constants import DEFAULT_RESULT_PATH 
from convo.exceptions import ModelNotPresent
import convo.shared.nlu.training_data.loading

if typing.TYPE_CHECKING:
    from convo.core.agent import CoreAgent

logger = logging.getLogger(__name__)


def test_core_models_in_dir(
    model_dir: Text, stories: Text, output: Text
) -> None:
    from convo.core.test import compare_models_in_dir

    model_dir = _fetch_sanitized_model_dir(model_dir)

    convo.utils.common.running_in_loop(
        compare_models_in_dir(model_dir, stories, output)
    )

    story_n_path = os.path.join(model_dir, NO_OF_TRAINING_STORY_FILE)
    number_of_stories = convo.shared.utils.io.reading_json_file(story_n_path)
    plot_core_outcome(output, number_of_stories)


def plot_core_outcome(output_directory: Text, number_of_examples: List[int]) -> None:
    """Plot core model comparison graph.

    Args:
        output_directory: path to the output dir
        number_of_examples: number of examples per run
    """
    import convo.utils.plotting as plotting_utils

    graph_path = os.path.join(output_directory, "core_model_comparison_graph.pdf")

    plotting_utils.plotting_curve(
        output_directory,
        number_of_examples,
        x_label_text="Number of stories present during training",
        y_label_text="Number of correct test stories",
        graph_path=graph_path,
    )


def _fetch_sanitized_model_dir(model_directory: Text) -> Text:
    """Adjusts the `--model` argument of `convo test core` when called with
    `--evaluate-model-directory`.

    By default convo uses the latest model for the `--model` parameter. However, for
    `--evaluate-model-directory` we need a dir. This function checks if the
    passed parameter is a model or an individual model file.

    Args:
        model_directory: The model_directory argument that was given to
        `test_core_models_in_dir`.

    Returns: The adjusted model_directory that should be used in
        `test_core_models_in_dir`.
    """
    import convo.model

    p = Path(model_directory)
    if p.is_file():
        if model_directory != convo.model.fetch_latest_model():
            convo.shared.utils.cli.printing_warning(
                "You passed a file as '--model'. Will use the dir containing "
                "this file instead."
            )
        model_directory = str(p.parent)

    return model_directory


def testiing_core_model(models: List[Text], stories: Text, output: Text):
    from convo.core.test import compare_models

    convo.utils.common.running_in_loop(compare_models(models, stories, output))


def test(
    model: Text,
    stories: Text,
    nlu_data: Text,
    output: Text = DEFAULT_RESULT_PATH,
    add_on_arguments: Optional[Dict] = None,
):
    if add_on_arguments is None:
        add_on_arguments = {}

    test_core(model, stories, output, add_on_arguments)
    test_nlu(model, nlu_data, output, add_on_arguments)


def test_core(
    model: Optional[Text] = None,
    stories: Optional[Text] = None,
    output: Text = DEFAULT_RESULT_PATH,
    add_on_arguments: Optional[Dict] = None,
) -> None:
    import convo.model
    from convo.shared.nlu.interpreter import RegexInterpreter
    from convo.core.agent import CoreAgent

    if add_on_arguments is None:
        add_on_arguments = {}

    if output:
        convo.shared.utils.io.create_dir(output)

    try:
        unpacked_model = convo.model.fetch_model(model)
    except ModelNotPresent:
        convo.shared.utils.cli.printing_error(
            "Unable to test: could not find a model. Use 'convo train' to train a "
            "Convo model and provide it via the '--model' argument."
        )
        return

    _agent = CoreAgent.load(unpacked_model)

    if _agent.policy_ensemble is None:
        convo.shared.utils.cli.printing_error(
            "Unable to test: could not find a Core model. Use 'convo train' to train a "
            "Convo model and provide it via the '--model' argument."
        )

    if isinstance(_agent.interpreter, RegexInterpreter):
        convo.shared.utils.cli.printing_warning(
            "No NLU model found. Using default 'RegexInterpreter' for end-to-end "
            "evaluation. If you added actual user messages to your test stories "
            "this will likely lead to the tests failing. In that case, you need "
            "to train a NLU model first, e.g. using `convo train`."
        )

    from convo.core.test import test

    kwargs = convo.shared.utils.common.min_kwargs(
        add_on_arguments, test, ["stories", "agent"]
    )

    convo.utils.common.running_in_loop(test(stories, _agent, out_directory=output, **kwargs))


def test_nlu(
    model: Optional[Text],
    nlu_data: Optional[Text],
    output_directory: Text = DEFAULT_RESULT_PATH,
    add_on_arguments: Optional[Dict] = None,
):
    from convo.nlu.test import run_eval
    from convo.model import fetch_model

    try:
        unpacked_model = fetch_model(model)
    except ModelNotPresent:
        convo.shared.utils.cli.printing_error(
            "Could not find any model. Use 'convo train nlu' to train a "
            "Convo model and provide it via the '--model' argument."
        )
        return

    convo.shared.utils.io.create_dir(output_directory)

    nlu_model = os.path.join(unpacked_model, "nlu")

    if os.path.exists(nlu_model):
        kwargs = convo.shared.utils.common.min_kwargs(
            add_on_arguments,run_eval, ["data_path", "model"]
        )
        run_eval(nlu_data, nlu_model, output_directory=output_directory, **kwargs)
    else:
        convo.shared.utils.cli.printing_error(
            "Could not find any model. Use 'convo train nlu' to train a "
            "Convo model and provide it via the '--model' argument."
        )


def comparison_nlu_models(
    configs: List[Text],
    nlu: Text,
    output: Text,
    runs: int,
    exclusion_percentages: List[int],
):
    """Trains multiple models, compares them and saves the results."""

    from convo.nlu.test import drop_convo_intents_below_freq
    from convo.nlu.utils import write_json_to_file
    from convo.utils.io import create_path
    from convo.nlu.test import nlu_comparison

    data_set = convo.shared.nlu.training_data.loading.load_data_set(nlu)
    data_set = drop_intents_below_freq(data_set, cutoff=5)

    create_path(output)

    base = [os.path.basename(nlu_config) for nlu_config in configs]
    models_name = [os.path.splitext(base)[0] for base in base]

    f1_score_results = {
        model_name: [[] for _ in range(runs)] for model_name in models_name
    }

    training_examples_per_run = nlu_comparison(
        configs,
        data_set,
        exclusion_percentages,
        f1_score_results,
        models_name,
        output,
        runs,
    )

    f1_path_flow = os.path.join(output, OUTCOME_FILES)
    write_json_to_file(f1_path_flow, f1_score_results)

    plot_nlu_outcome(output, training_examples_per_run)


def plot_nlu_outcome(output_directory: Text, number_of_examples: List[int]) -> None:
    """Plot NLU model comparison graph.

    Args:
        output_directory: path to the output dir
        number_of_examples: number of examples per run
    """
    import convo.utils.plotting as plotting_utils

    graph_path = os.path.join(output_directory, "nlu_model_comparison_graph.pdf")

    plotting_utils.plotting_curve(
        output_directory,
        number_of_examples,
        x_label_text="Number of intent examples present during training",
        y_label_text="Label-weighted average F1 score on test set",
        graph_path=graph_path,
    )


def execute_nlu_cross_validate(
    config: Text,
    nlu: Text,
    output: Text,
    add_on_arguments: Optional[Dict[Text, Any]],
):
    import convo.nlu.config
    from convo.nlu.test import (
        drop_convo_intents_below_freq,
        cross_validation,
        logging_ress,
        log_ent_ress,
    )

    add_on_arguments = add_on_arguments or {}
    get_folds = int(add_on_arguments.get("folds", 3))
    nlu_configuration = convo.nlu.config.load(config)
    data = convo.shared.nlu.training_data.loading.load_data_set(nlu)
    data = drop_convo_intents_below_freq(data, cutoff=get_folds)
    keyword_arguments = convo.shared.utils.common.min_kwargs(
        add_on_arguments, cross_validation
    )
    outcomes, entities_results, response_selection_outcome = cross_validation(
        data, get_folds, nlu_configuration, output, **keyword_arguments
    )
    logger.info(f"CV evaluation (n={get_folds})")

    if any(outcomes):
        logger.info("Intent evaluation results")
        logging_ress(outcomes.train, "train")
        logging_ress(outcomes.test, "test")
    if any(entities_results):
        logger.info("Entity evaluation results")
        log_ent_ress(entities_results.train, "train")
        log_ent_ress(entities_results.test, "test")
    if any(response_selection_outcome):
        logger.info("Response Selection evaluation results")
        logging_ress(response_selection_outcome.train, "train")
        logging_ress(response_selection_outcome.test, "test")


def fetch_evaluation_metrics(
    goals: Iterable[Any],
    forecasts: Iterable[Any],
    output_dict: bool = False,
    exclude_label: Optional[Text] = None,
) -> Tuple[Union[Text, Dict[Text, Dict[Text, float]]], float, float, float]:
    """Compute the f1, precision, accuracy and summary report from sklearn.

    Args:
        goals: target labels
        forecasts: predicted labels
        output_dict: if True sklearn returns a summary report as dict, if False the
          report is in string format
        exclude_label: labels to exclude from evaluation

    Returns:
        Report from sklearn, precision, f1, and accuracy values.
    """
    from sklearn import metrics

    goals = clean_tags(goals)
    forecasts = clean_tags(forecasts)

    tags = get_unique_labels(goals, exclude_label)
    if not tags:
        logger.warning("No labels to evaluate. Skip evaluation.")
        return {}, 0.0, 0.0, 0.0

    detail_report = metrics.classification_report(
        goals, forecasts, labels=tags, output_dict=output_dict
    )
    accuracy = metrics.precision_score(
        goals, forecasts, labels=tags, average="weighted"
    )
    f_1 = metrics.f1_score(goals, forecasts, labels=tags, average="weighted")
    accuracy = metrics.accuracy_score(goals, forecasts)

    return detail_report, accuracy, f_1, accuracy


def clean_tags(labels: Iterable[Text]) -> List[Text]:
    """Remove `None` labels. sklearn metrics do not support them.

    Args:
        labels: list of labels

    Returns:
        Cleaned labels.
    """
    return [label if label is not None else "" for label in labels]


def get_unique_labels(
    targets: Iterable[Text], exclude_label: Optional[Text]
) -> List[Text]:
    """Get unique labels. Exclude 'exclude_label' if specified.

    Args:
        targets: labels
        exclude_label: label to exclude

    Returns:
         Unique labels.
    """
    labels = set(targets)
    if exclude_label and exclude_label in labels:
        labels.remove(exclude_label)
    return list(labels)
