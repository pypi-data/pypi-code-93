import itertools
import os
import logging
import numpy as np
from collections import defaultdict, namedtuple
from tqdm import tqdm
from typing import (
    Iterable,
    Iterator,
    Tuple,
    List,
    Set,
    Optional,
    Text,
    Union,
    Dict,
    Any,
)

from convo import telemetry
import convo.shared.utils.io
import convo.utils.plotting as plot_utils
import convo.utils.io as io_utils
import convo.utils.common

from convo.constants import DATA_FILE_TESTING, DATA_FILE_TRANING, NLG_DATA_SET_FILE
from convo.nlu.constants import (
    DFAULT_INTENT_RESPONSE_PICKER,
    PROP_NAME_RESPONSE_PICKER,
    PREDICTION_KEY_RESPONSE_PICKER,
    NAMES_OF_TOKENS,
    ENTITY_ATTR_CONFIDENCE_TYPE_VAL,
    ENTITY_ATTR_CONFIDENCE_ROLE,
    ENTITY_ATTR_CONFIDENCE_GRP,
)
from convo.shared.nlu.constants import (
    TXT,
    INTENTION,
    KEY_INTENT_RESPONSE,
    ENTITIES_NAME,
    EXTRACTOR,
    PRE_TRAINED_EXTRACTORS,
    ATTRIBUTE_TYPE_ENTITY,
    ATTRIBUTE_GROUP_ENTITY,
    ATTRIBUTE_ROLE_ENTITY,
    ENTITY_TAG_ABSENT,
    KEY_INTENT_NAME,
    KEY_PREDICTED_CONFIDENCE,
)
from convo.model import fetch_model
from convo.nlu.components import ElementBuilder
from convo.nlu.config import ConvoNLUModelConfiguration
from convo.nlu.model import Interpreter, Instructor, TrainingDataSet
from convo.nlu.components import Element
from convo.nlu.tokenizers.tokenizer import Tkn
from convo.utils.tensorflow.constants import ENTITY_IDENTIFICATION

log = logging.getLogger(__name__)

# Exclude 'EntitySynonymMapper' and 'ResponseSelector' as their super class
# performs entity extraction but those two classifiers don't
PROCESSORS_ENTITY = {"EntitySynonymMapper", "ResponseSelector"}

CONFIDENT_EXTRACTORS = {"CRFEntityExtractor", "DIETClassifier"}

cv_evaluation_result = namedtuple("Results", "train test")

NOT_ENTITY = "no_entity"

intent_evaluation_res = namedtuple(
    "IntentEvaluationResult", "intent_target intent_prediction message confidence"
)

response_selection_evaluation_res = namedtuple(
    "ResponseSelectionEvaluationResult",
    "intent_response_key_target intent_response_key_prediction message confidence",
)

entity_evaluation_res = namedtuple(
    "EntityEvaluationResult", "entity_targets entity_predictions tokens message"
)

intent_metrics = Dict[Text, List[float]]
entity_metrics = Dict[Text, Dict[Text, List[float]]]
res_select_metrics = Dict[Text, List[float]]


def log_eval_table(
    report: Text, precision: float, f1: float, accuracy: float
) -> None:  # pragma: no cover
    """Log the sklearn evaluation metrics."""
    log.info(f"F1-Score:  {f1}")
    log.info(f"Precision: {precision}")
    log.info(f"Accuracy:  {accuracy}")
    log.info(f"Classification report: \n{report}")


def del_empty_intent_exps(
    intent_results: List[intent_evaluation_res],
) -> List[intent_evaluation_res]:
    """Remove those examples without an intent.

    Args:
        intent_results: intent evaluation results

    Returns: intent evaluation results
    """
    filter = []
    for s in intent_results:
        # substitute None values with empty string
        # to enable sklearn evaluation
        if s.intent_prediction is None:
            s = s._replace(intent_prediction="")

        if s.intent_target != "" and s.intent_target is not None:
            filter.append(s)

    return filter


def del_empty_res_examples(
    response_results: List[response_selection_evaluation_res],
) -> List[response_selection_evaluation_res]:
    """Remove those examples without a response.

    Args:
        response_results: response selection evaluation results

    Returns: response selection evaluation results
    """

    filter = []
    for s in response_results:
        # substitute None values with empty string
        # to enable sklearn evaluation
        if s.intent_response_key_prediction is None:
            s = s._replace(intent_response_key_prediction="")

        if s.intent_response_key_target:
            filter.append(s)

    return filter


def drop_convo_intents_below_freq(
    training_data: TrainingDataSet, cutoff: int = 5
) -> TrainingDataSet:
    """Remove intent groups with less than cutoff instances.

    Args:
        training_data: training data
        cutoff: threshold

    Returns: updated training data
    """
    log.debug(
        "Raw data intent examples: {}".format(len(training_data.intent_exp))
    )
    keep_exps = [
        ex
        for ex in training_data.intent_exp
        if training_data.no_of_examples_per_intent[ex.get(INTENTION)] >= cutoff
    ]

    return TrainingDataSet(
        keep_exps,
        training_data.entity_synonyms,
        training_data.regex_features,
        responses=training_data.responses,
    )


def writig_intent_success(
    intent_results: List[intent_evaluation_res], successes_filename: Text
) -> None:
    """Write successful intent predictions to a file.

    Args:
        intent_results: intent evaluation result
        successes_filename: filename of file to save successful predictions to
    """
    success = [
        {
            "text": r.message,
            "intent": r.intent_target,
            "intent_prediction": {
                KEY_INTENT_NAME: r.intent_prediction,
                "confidence": r.confidence,
            },
        }
        for r in intent_results
        if r.intent_target == r.intent_prediction
    ]

    if success:
        convo.shared.utils.io.dump_object_as_json_to_file(successes_filename, success)
        log.info(f"Successful intent predictions saved to {successes_filename}.")
        log.debug(f"\n\nSuccessfully predicted the following convo_intents: \n{success}")
    else:
        log.info("No successful intent predictions found.")


def writing_intent_errs(
    intent_results: List[intent_evaluation_res], errors_filename: Text
) -> None:
    """Write incorrect intent predictions to a file.

    Args:
        intent_results: intent evaluation result
        errors_filename: filename of file to save incorrect predictions to
    """
    errs = [
        {
            "text": r.message,
            "intent": r.intent_target,
            "intent_prediction": {
                KEY_INTENT_NAME: r.intent_prediction,
                "confidence": r.confidence,
            },
        }
        for r in intent_results
        if r.intent_target != r.intent_prediction
    ]

    if errs:
        convo.shared.utils.io.dump_object_as_json_to_file(errors_filename, errs)
        log.info(f"Incorrect intent predictions saved to {errors_filename}.")
        log.debug(
            "\n\nThese intent examples could not be classified "
            "correctly: \n{}".format(errs)
        )
    else:
        log.info("Your model predicted all convo_intents successfully.")


def writing_res_success(
    response_results: List[response_selection_evaluation_res], successes_filename: Text
) -> None:
    """Write successful response selection predictions to a file.

    Args:
        response_results: response selection evaluation result
        successes_filename: filename of file to save successful predictions to
    """

    success = [
        {
            "text": r.message,
            "intent_response_key_target": r.intent_response_key_target,
            "intent_response_key_prediction": {
                "name": r.intent_response_key_prediction,
                "confidence": r.confidence,
            },
        }
        for r in response_results
        if r.intent_response_key_prediction == r.intent_response_key_target
    ]

    if success:
        convo.shared.utils.io.dump_object_as_json_to_file(successes_filename, success)
        log.info(f"Successful response predictions saved to {successes_filename}.")
        log.debug(
            f"\n\nSuccessfully predicted the following responses: \n{success}"
        )
    else:
        log.info("No successful response predictions found.")


def writing_res_errs(
    response_results: List[response_selection_evaluation_res], errors_filename: Text
) -> None:
    """Write incorrect response selection predictions to a file.

    Args:
        response_results: response selection evaluation result
        errors_filename: filename of file to save incorrect predictions to
    """
    errs = [
        {
            "text": r.message,
            "intent_response_key_target": r.intent_response_key_target,
            "intent_response_key_prediction": {
                "name": r.intent_response_key_prediction,
                "confidence": r.confidence,
            },
        }
        for r in response_results
        if r.intent_response_key_prediction != r.intent_response_key_target
    ]

    if errs:
        convo.shared.utils.io.dump_object_as_json_to_file(errors_filename, errs)
        log.info(f"Incorrect response predictions saved to {errors_filename}.")
        log.debug(
            "\n\nThese response examples could not be classified "
            "correctly: \n{}".format(errs)
        )
    else:
        log.info("Your model predicted all responses successfully.")


def plotting_attr_confidences(
    results: Union[
        List[intent_evaluation_res], List[response_selection_evaluation_res]
    ],
    hist_filename: Optional[Text],
    target_key: Text,
    prediction_key: Text,
    title: Text,
) -> None:
    """Create histogram of confidence distribution.

    Args:
        results: evaluation results
        hist_filename: filename to save plot to
        target_key: key of target in results
        prediction_key: key of predictions in results
        title: title of plot
    """
    positive_histogram = [
        r.confidence
        for r in results
        if getattr(r, target_key) == getattr(r, prediction_key)
    ]

    negative_histogram = [
        r.confidence
        for r in results
        if getattr(r, target_key) != getattr(r, prediction_key)
    ]

    plot_utils.plotting_histogram([positive_histogram, negative_histogram], title, hist_filename)


def plotting_entity_confidences(
    merged_targets: List[Text],
    merged_predictions: List[Text],
    merged_confidences: List[float],
    hist_filename: Text,
    title: Text,
) -> None:
    """Create histogram of confidence distribution.

    Args:
        results: evaluation results
        hist_filename: filename to save plot to
        target_key: key of target in results
        prediction_key: key of predictions in results
        title: title of plot
    """
    positive_histogram = [
        confidence
        for target, prediction, confidence in zip(
            merged_targets, merged_predictions, merged_confidences
        )
        if target != NOT_ENTITY and target == prediction
    ]

    negative_histogram = [
        confidence
        for target, prediction, confidence in zip(
            merged_targets, merged_predictions, merged_confidences
        )
        if prediction not in (NOT_ENTITY, target)
    ]

    plot_utils.plotting_histogram([positive_histogram, negative_histogram], title, hist_filename)


def evaluating_res_selections(
    res_select_res: List[response_selection_evaluation_res],
    output_directory: Optional[Text],
    successes: bool,
    errors: bool,
    disable_plotting: bool,
) -> Dict:  # pragma: no cover
    """Creates summary statistics for response selection.

    Only considers those examples with a set response.
    Others are filtered out. Returns a dictionary of containing the
    evaluation result.

    Args:
        res_select_res: response selection evaluation results
        output_directory: dir to store files to
        successes: if True success are written down to disk
        errors: if True errors are written down to disk
        disable_plotting: if True no plots are created

    Returns: dictionary with evaluation results
    """
    import sklearn.metrics
    import sklearn.utils.multiclass
    from convo.test import fetch_evaluation_metrics

    # remove empty response targets
    number_exps = len(res_select_res)
    res_select_res = del_empty_res_examples(
        res_select_res
    )

    log.info(
        f"Response Selection Evaluation: Only considering those "
        f"{len(res_select_res)} examples that have a defined response out "
        f"of {number_exps} examples."
    )

    (
        tar_intent_res_keys,
        intent_ser_keys_predicted,
    ) = tar_pred_from(
        res_select_res,
        "intent_response_key_target",
        "intent_response_key_prediction",
    )

    matrix_with_confusion = sklearn.metrics.confusion_matrix(
        tar_intent_res_keys, intent_ser_keys_predicted
    )
    tags = sklearn.utils.multiclass.unique_labels(
        tar_intent_res_keys, intent_ser_keys_predicted
    )

    if output_directory:
        result, precision, f1, accuracy = fetch_evaluation_metrics(
            tar_intent_res_keys,
            intent_ser_keys_predicted,
            output_dict=True,
        )
        result = _adding_confused_tags_to_report(result, matrix_with_confusion, tags)

        file_name_report = os.path.join(
            output_directory, "response_selection_report.json"
        )
        convo.shared.utils.io.dump_object_as_json_to_file(file_name_report, result)
        log.info(f"Classification report saved to {file_name_report}.")

    else:
        result, precision, f1, accuracy = fetch_evaluation_metrics(
            tar_intent_res_keys, intent_ser_keys_predicted
        )
        if isinstance(result, str):
            log_eval_table(result, precision, f1, accuracy)

    if successes:
        file_name_success = "response_selection_successes.json"
        if output_directory:
            file_name_success = os.path.join(output_directory, file_name_success)
        # save classified samples to file for debugging
        writing_res_success(res_select_res, file_name_success)

    if errors:
        file_name_errs = "response_selection_errors.json"
        if output_directory:
            file_name_errs = os.path.join(output_directory, file_name_errs)
        # log and save misclassified samples to file for debugging
        writing_res_errs(res_select_res, file_name_errs)

    if not disable_plotting:
        file_name_confusion_matrix = "response_selection_confusion_matrix.png"
        if output_directory:
            file_name_confusion_matrix = os.path.join(
                output_directory, file_name_confusion_matrix
            )

        plot_utils.matrix_plot_confusion(
            matrix_with_confusion,
            classes=tags,
            title="Response Selection Confusion Matrix",
            output_file=file_name_confusion_matrix,
        )

        file_name_hist = "response_selection_histogram.png"
        if output_directory:
            file_name_hist = os.path.join(output_directory, file_name_hist)
        plotting_attr_confidences(
            res_select_res,
            file_name_hist,
            "intent_response_key_target",
            "intent_response_key_prediction",
            title="Response Selection Prediction Confidence Distribution",
        )

    forecast = [
        {
            "text": res.message,
            "intent_response_key_target": res.intent_response_key_target,
            "intent_response_key_prediction": res.intent_response_key_prediction,
            "confidence": res.confidence,
        }
        for res in res_select_res
    ]

    return {
        "predictions": forecast,
        "report": result,
        "precision": precision,
        "f1_score": f1,
        "accuracy": accuracy,
    }


def _adding_confused_tags_to_report(
    report: Dict[Text, Dict[Text, Any]],
    confusion_matrix: np.ndarray,
    labels: List[Text],
    labels_excluded: Optional[List[Text]] = None,
) -> Dict[Text, Dict[Text, Union[Dict, Any]]]:
    """Adds a field "confused_with" to the evaluation report.

    The value is a dict of {"false_positive_label": false_positive_count} pairs.
    If there are no false positives in the confusion matrix,
    the dict will be empty. Typically we include the two most
    commonly false positive labels, three in the rare case that
    the diagonal element in the confusion matrix is not one of the
    three highest values in the row.

    Args:
        report: the evaluation report
        confusion_matrix: confusion matrix
        labels: list of labels

    Returns: updated evaluation report
    """
    if labels_excluded is None:
        labels_excluded = []

    # sort confusion matrix by false positives
    indexes = np.argsort(confusion_matrix, axis=1)
    x_cands = min(3, len(labels))

    for label in labels:
        if label in labels_excluded:
            continue
        # it is possible to predict intent 'None'
        if report.get(label):
            report[label]["confused_with"] = {}

    for i, label in enumerate(labels):
        if label in labels_excluded:
            continue
        for j in range(x_cands):
            label_index = indexes[i, -(1 + j)]
            wrong_pos_label = labels[label_index]
            label_false_positive = int(confusion_matrix[i, label_index])
            if (
                wrong_pos_label != label
                and wrong_pos_label not in labels_excluded
                and label_false_positive > 0
            ):
                report[label]["confused_with"][wrong_pos_label] = label_false_positive

    return report


def calculate_intents(
    intents_res: List[intent_evaluation_res],
    output_directory: Optional[Text],
    successes: bool,
    errors: bool,
    disable_plotting: bool,
) -> Dict:  # pragma: no cover
    """Creates summary statistics for convo_intents.

    Only considers those examples with a set intent. Others are filtered out.
    Returns a dictionary of containing the evaluation result.

    Args:
        intents_res: intent evaluation results
        output_directory: dir to store files to
        successes: if True correct predictions are written to disk
        errors: if True incorrect predictions are written to disk
        disable_plotting: if True no plots are created

    Returns: dictionary with evaluation results
    """
    import sklearn.metrics
    import sklearn.utils.multiclass
    from convo.test import fetch_evaluation_metrics

    # remove empty intent targets
    number_exps = len(intents_res)
    intents_res = del_empty_intent_exps(intents_res)

    log.info(
        f"Intent Evaluation: Only considering those {len(intents_res)} examples "
        f"that have a defined intent out of {number_exps} examples."
    )

    tar_intents, intents_predicted = tar_pred_from(
        intents_res, "intent_target", "intent_prediction"
    )

    uncertainty_matrix = sklearn.metrics.confusion_matrix(
        tar_intents, intents_predicted
    )
    tags = sklearn.utils.multiclass.unique_labels(tar_intents, intents_predicted)

    if output_directory:
        result, exactness, x1, efficiency = fetch_evaluation_metrics(
            tar_intents, intents_predicted, output_dict=True
        )
        result = _adding_confused_tags_to_report(result, uncertainty_matrix, tags)

        file_name_report = os.path.join(output_directory, "intent_report.json")
        convo.shared.utils.io.dump_object_as_json_to_file(file_name_report, result)
        log.info(f"Classification report saved to {file_name_report}.")

    else:
        result, exactness, x1, efficiency = fetch_evaluation_metrics(
            tar_intents, intents_predicted
        )
        if isinstance(result, str):
            log_eval_table(result, exactness, x1, efficiency)

    if successes and output_directory:
        file_name_success = os.path.join(output_directory, "intent_successes.json")
        # save classified samples to file for debugging
        writig_intent_success(intents_res, file_name_success)

    if errors and output_directory:
        file_name_errs = os.path.join(output_directory, "intent_errors.json")
        # log and save misclassified samples to file for debugging
        writing_intent_errs(intents_res, file_name_errs)

    if not disable_plotting:
        file_name_confusion_matrix = "intent_confusion_matrix.png"
        if output_directory:
            file_name_confusion_matrix = os.path.join(
                output_directory, file_name_confusion_matrix
            )
        plot_utils.matrix_plot_confusion(
            uncertainty_matrix,
            classes=tags,
            title="Intent Confusion matrix",
            output_file=file_name_confusion_matrix,
        )

        file_name_hist = "intent_histogram.png"
        if output_directory:
            file_name_hist = os.path.join(output_directory, file_name_hist)
        plotting_attr_confidences(
            intents_res,
            file_name_hist,
            "intent_target",
            "intent_prediction",
            title="Intent Prediction Confidence Distribution",
        )

    forecast = [
        {
            "text": res.message,
            "intent": res.intent_target,
            "predicted": res.intent_prediction,
            "confidence": res.confidence,
        }
        for res in intents_res
    ]

    return {
        "predictions": forecast,
        "report": result,
        "precision": exactness,
        "f1_score": x1,
        "accuracy": efficiency,
    }


def merging_tags(
    aligned_predictions: List[Dict], extractor: Optional[Text] = None
) -> List[Text]:
    """Concatenates all labels of the aligned predictions.

    Takes the aligned prediction labels which are grouped for each message
    and concatenates them.

    Args:
        aligned_predictions: aligned predictions
        extractor: entity extractor name

    Returns: concatenated predictions
    """

    if extractor:
        lists_of_labels = [ap["extractor_labels"][extractor] for ap in aligned_predictions]
    else:
        lists_of_labels = [ap["target_labels"] for ap in aligned_predictions]

    return list(itertools.chain(*lists_of_labels))


def merging_confidences(
    aligned_predictions: List[Dict], extractor: Optional[Text] = None
) -> List[float]:
    """Concatenates all confidences of the aligned predictions.

    Takes the aligned prediction confidences which are grouped for each message
    and concatenates them.

    Args:
        aligned_predictions: aligned predictions
        extractor: entity extractor name

    Returns: concatenated confidences
    """

    lists_of_labels = [ap["confidences"][extractor] for ap in aligned_predictions]
    return list(itertools.chain(*lists_of_labels))


def sub_labels(labels: List[Text], old: Text, new: Text) -> List[Text]:
    """Replaces label names in a list of labels.

    Args:
        labels: list of labels
        old: old label name that should be replaced
        new: new label name

    Returns: updated labels
    """
    return [new if label == old else label for label in labels]


def writing_wrong_entity_preds(
    entity_results: List[entity_evaluation_res],
    merged_targets: List[Text],
    merged_predictions: List[Text],
    error_filename: Text,
) -> None:
    """Write incorrect entity predictions to a file.

    Args:
        entity_results: response selection evaluation result
        merged_predictions: list of predicted entity labels
        merged_targets: list of true entity labels
        error_filename: filename of file to save incorrect predictions to
    """
    errs = collecting_wrong_entity_preds(
        entity_results, merged_predictions, merged_targets
    )

    if errs:
        convo.shared.utils.io.dump_object_as_json_to_file(error_filename, errs)
        log.info(f"Incorrect entity predictions saved to {error_filename}.")
        log.debug(
            "\n\nThese intent examples could not be classified "
            "correctly: \n{}".format(errs)
        )
    else:
        log.info("Your model predicted all entities successfully.")


def collecting_wrong_entity_preds(
    entity_results: List[entity_evaluation_res],
    merged_predictions: List[Text],
    merged_targets: List[Text],
):
    """Get incorrect entity predictions.

    Args:
        entity_results: entity evaluation results
        merged_predictions: list of predicted entity labels
        merged_targets: list of true entity labels

    Returns: list of incorrect predictions
    """
    errs = []
    off_set = 0
    for entity_result in entity_results:
        for i in range(off_set, off_set + len(entity_result.tokens)):
            if merged_targets[i] != merged_predictions[i]:
                errs.append(
                    {
                        "text": entity_result.message,
                        "entities": entity_result.entity_targets,
                        "predicted_entities": entity_result.entity_predictions,
                    }
                )
                break
        off_set += len(entity_result.tokens)
    return errs


def writing_correct_entity_preds(
    entity_results: List[entity_evaluation_res],
    merged_targets: List[Text],
    merged_predictions: List[Text],
    successes_filename: Text,
) -> None:
    """Write correct entity predictions to a file.

    Args:
        entity_results: response selection evaluation result
        merged_predictions: list of predicted entity labels
        merged_targets: list of true entity labels
        successes_filename: filename of file to save correct predictions to
    """
    success = collecting_correct_entity_preds(
        entity_results, merged_predictions, merged_targets
    )

    if success:
        convo.shared.utils.io.dump_object_as_json_to_file(successes_filename, success)
        log.info(f"Successful entity predictions saved to {successes_filename}.")
        log.debug(
            f"\n\nSuccessfully predicted the following entities: \n{success}"
        )
    else:
        log.info("No successful entity prediction found.")


def collecting_correct_entity_preds(
    entity_results: List[entity_evaluation_res],
    merged_predictions: List[Text],
    merged_targets: List[Text],
):
    """Get correct entity predictions.

    Args:
        entity_results: entity evaluation results
        merged_predictions: list of predicted entity labels
        merged_targets: list of true entity labels

    Returns: list of correct predictions
    """
    success = []
    off_set = 0
    for entity_result in entity_results:
        for i in range(off_set, off_set + len(entity_result.tokens)):
            if (
                merged_targets[i] == merged_predictions[i]
                and merged_targets[i] != NOT_ENTITY
            ):
                success.append(
                    {
                        "text": entity_result.message,
                        "entities": entity_result.entity_targets,
                        "predicted_entities": entity_result.entity_predictions,
                    }
                )
                break
        off_set += len(entity_result.tokens)
    return success


def entities_evaluation(
    entity_results: List[entity_evaluation_res],
    extractors: Set[Text],
    output_directory: Optional[Text],
    successes: bool,
    errors: bool,
    disable_plotting: bool,
) -> Dict:  # pragma: no cover
    """Creates summary statistics for each entity extractor.

    Logs precision, recall, and F1 per entity type for each extractor.

    Args:
        entity_results: entity evaluation results
        extractors: entity extractors to consider
        output_directory: dir to store files to
        successes: if True correct predictions are written to disk
        errors: if True incorrect predictions are written to disk
        disable_plotting: if True no plots are created

    Returns: dictionary with evaluation results
    """
    import sklearn.metrics
    import sklearn.utils.multiclass
    from convo.test import fetch_evaluation_metrics

    preds_aligned = aligning_all_ent_preds(entity_results, extractors)
    targers_merged = merging_tags(preds_aligned)
    targers_merged = sub_labels(targers_merged, ENTITY_TAG_ABSENT, NOT_ENTITY)

    res = {}

    for extractor in extractors:
        preds_merged = merging_tags(preds_aligned, extractor)
        preds_merged = sub_labels(
            preds_merged, ENTITY_TAG_ABSENT, NOT_ENTITY
        )

        log.info(f"Evaluation for entity extractor: {extractor} ")

        confusion_matrix = sklearn.metrics.confusion_matrix(
            targers_merged, preds_merged
        )
        tags = sklearn.utils.multiclass.unique_labels(
            targers_merged, preds_merged
        )

        if output_directory:
            file_name_report = f"{extractor}_report.json"
            file_name_extractor_report = os.path.join(output_directory, file_name_report)

            report, precision, x1, accuracy = fetch_evaluation_metrics(
                targers_merged,
                preds_merged,
                output_dict=True,
                exclude_label=NOT_ENTITY,
            )
            report = _adding_confused_tags_to_report(
                report, confusion_matrix, tags, [NOT_ENTITY]
            )

            convo.shared.utils.io.dump_object_as_json_to_file(
                file_name_extractor_report, report
            )

            log.info(
                "Classification report for '{}' saved to '{}'."
                "".format(extractor, file_name_extractor_report)
            )

        else:
            report, precision, x1, accuracy = fetch_evaluation_metrics(
                targers_merged,
                preds_merged,
                output_dict=False,
                exclude_label=NOT_ENTITY,
            )
            if isinstance(report, str):
                log_eval_table(report, precision, x1, accuracy)

        if successes:
            file_name_success = f"{extractor}_successes.json"
            if output_directory:
                file_name_success = os.path.join(output_directory, file_name_success)
            # save classified samples to file for debugging
            writing_correct_entity_preds(
                entity_results, targers_merged, preds_merged, file_name_success
            )

        if errors:
            file_name_errs = f"{extractor}_errors.json"
            if output_directory:
                file_name_errs = os.path.join(output_directory, file_name_errs)
            # log and save misclassified samples to file for debugging
            writing_wrong_entity_preds(
                entity_results, targers_merged, preds_merged, file_name_errs
            )

        if not disable_plotting:
            file_name_confusion_matrix = f"{extractor}_confusion_matrix.png"
            if output_directory:
                file_name_confusion_matrix = os.path.join(
                    output_directory, file_name_confusion_matrix
                )
            plot_utils.matrix_plot_confusion(
                confusion_matrix,
                classes=tags,
                title="Entity Confusion matrix",
                output_file=file_name_confusion_matrix,
            )

            if extractor in CONFIDENT_EXTRACTORS:
                confidences_merged = merging_confidences(preds_aligned, extractor)
                file_name_hist = f"{extractor}_histogram.png"
                if output_directory:
                    file_name_hist = os.path.join(
                        output_directory, file_name_hist
                    )
                plotting_entity_confidences(
                    targers_merged,
                    preds_merged,
                    confidences_merged,
                    title="Entity Confusion matrix",
                    hist_filename=file_name_hist,
                )

        res[extractor] = {
            "report": report,
            "precision": precision,
            "f1_score": x1,
            "accuracy": accuracy,
        }

    return res


def token_within_entity_check(token: Tkn, entity: Dict) -> bool:
    """Checks if a token is within the boundaries of an entity."""
    return inter_section_determination(token, entity) == len(token.text)


def token_crossing_borders_check(token: Tkn, entity: Dict) -> bool:
    """Checks if a token crosses the boundaries of an entity."""

    inter_section_number = inter_section_determination(token, entity)
    return 0 < inter_section_number < len(token.text)


def inter_section_determination(token: Tkn, entity: Dict) -> int:
    """Calculates how many characters a given token and entity share."""

    positive_token = set(range(token.start, token.end))
    positive_entity = set(range(entity["start"], entity["end"]))
    return len(positive_token.intersection(positive_entity))


def entity_overlap_check(entities: List[Dict]) -> bool:
    """Checks if entities overlap.

    I.e. cross each others start and end boundaries.

    Args:
        entities: list of entities

    Returns: true if entities overlap, false otherwise.
    """
    entities_sorted = sorted(entities, key=lambda e: e["start"])
    for i in range(len(entities_sorted) - 1):
        current_entity = entities_sorted[i]
        next_coming_entity = entities_sorted[i + 1]
        if (
            next_coming_entity["start"] < current_entity["end"]
            and next_coming_entity["entity"] != current_entity["entity"]
        ):
            log.warning(f"Overlapping entity {current_entity} with {next_coming_entity}")
            return True

    return False


def search_intersecting_ents(token: Tkn, entities: List[Dict]) -> List[Dict]:
    """Finds the entities that intersect with a token.

    Args:
        token: a single token
        entities: entities found by a single extractor

    Returns: list of entities
    """
    cands = []
    for e in entities:
        if token_within_entity_check(token, e):
            cands.append(e)
        elif token_crossing_borders_check(token, e):
            cands.append(e)
            log.debug(
                "Token boundary error for token {}({}, {}) "
                "and entity {}"
                "".format(token.text, token.start, token.end, e)
            )
    return cands


def select_best_ent_fit(
    token: Tkn, candidates: List[Dict[Text, Any]]
) -> Optional[Dict[Text, Any]]:
    """
    Determines the best fitting entity given intersecting entities.

    Args:
        token: a single token
        candidates: entities found by a single extractor
        attribute_key: the attribute key of interest

    Returns:
        the value of the attribute key of the best fitting entity
    """
    if len(candidates) == 0:
        return None
    elif len(candidates) == 1:
        return candidates[0]
    else:
        perfect_fit = np.argmax([inter_section_determination(token, c) for c in candidates])
        return candidates[int(perfect_fit)]


def token_labels_determination(
    token:Tkn,
    entities: List[Dict],
    extractors: Optional[Set[Text]] = None,
    attribute_key: Text = ATTRIBUTE_TYPE_ENTITY,
) -> Text:
    """
    Determines the token label for the provided attribute key given entities that do
    not overlap.

    Args:
        token: a single token
        entities: entities found by a single extractor
        extractors: list of extractors
        attribute_key: the attribute key for which the entity type should be returned
    Returns:
        entity type
    """
    ent = ent_for_token_determination(token, entities, extractors)

    if ent is None:
        return ENTITY_TAG_ABSENT

    tag = ent.get(attribute_key)

    if not tag:
        return ENTITY_TAG_ABSENT

    return tag


def ent_for_token_determination(
    token: Tkn,
    entities: List[Dict[Text, Any]],
    extractors: Optional[Set[Text]] = None,
) -> Optional[Dict[Text, Any]]:
    """
    Determines the best fitting entity for the given token, given entities that do
    not overlap.

    Args:
        token: a single token
        entities: entities found by a single extractor
        extractors: list of extractors

    Returns:
        entity type
    """
    if entities is None or len(entities) == 0:
        return None
    if not overlapping_supported_by_extractors_check(extractors) and entity_overlap_check(entities):
        raise ValueError("The possible entities should not overlap.")

    cands = search_intersecting_ents(token, entities)
    return select_best_ent_fit(token, cands)


def overlapping_supported_by_extractors_check(extractors: Optional[Set[Text]]) -> bool:
    """Checks if extractors support overlapping entities"""
    if extractors is None:
        return False

    from convo.nlu.extractors.crf_entity_extractor import CRFEntityExtractor

    return CRFEntityExtractor.name not in extractors


def aligning_ent_preds(
    result: entity_evaluation_res, extractors: Set[Text]
) -> Dict:
    """Aligns entity predictions to the message tokens.

    Determines for every token the true label based on the
    prediction targets and the label assigned by each
    single extractor.

    Args:
        result: entity evaluation result
        extractors: the entity extractors that should be considered

    Returns: dictionary containing the true token labels and token labels
             from the extractors
    """
    correct_token_labels = []
    entities_by_extractors: Dict[Text, List] = {
        extractor: [] for extractor in extractors
    }
    for p in result.entity_predictions:
        entities_by_extractors[p[EXTRACTOR]].append(p)
    extractor_labels: Dict[Text, List] = {extractor: [] for extractor in extractors}
    extractor_confidences: Dict[Text, List] = {
        extractor: [] for extractor in extractors
    }
    for t in result.tokens:
        correct_token_labels.append(_ent_labels_concatenation(t, result.entity_targets))
        for extractor, entities in entities_by_extractors.items():
            labels_extracted = _ent_labels_concatenation(t, entities, {extractor})
            confidences_extracted = _fetch_ent_confidences(t, entities, {extractor})
            extractor_labels[extractor].append(labels_extracted)
            extractor_confidences[extractor].append(confidences_extracted)

    return {
        "target_labels": correct_token_labels,
        "extractor_labels": extractor_labels,
        "confidences": extractor_confidences,
    }


def _ent_labels_concatenation(
    token: Tkn, entities: List[Dict], extractors: Optional[Set[Text]] = None
) -> Text:
    """Concatenate labels for entity type, role, and group for evaluation.

    In order to calculate metrics also for entity type, role, and group we need to
    concatenate their labels. For example, 'location.destination'. This allows
    us to report metrics for every combination of entity type, role, and group.

    Args:
        token: the token we are looking at
        entities: the available entities
        extractors: the extractor of interest

    Returns:
        the entity label of the provided token
    """
    ent_label = token_labels_determination(
        token, entities, extractors, ATTRIBUTE_TYPE_ENTITY
    )
    label_group = token_labels_determination(
        token, entities, extractors, ATTRIBUTE_GROUP_ENTITY
    )
    label_role = token_labels_determination(
        token, entities, extractors, ATTRIBUTE_ROLE_ENTITY
    )

    if ent_label == label_role == label_group == ENTITY_TAG_ABSENT:
        return ENTITY_TAG_ABSENT

    tags = [ent_label, label_group, label_role]
    tags = [label for label in tags if label != ENTITY_TAG_ABSENT]

    return ".".join(tags)


def _fetch_ent_confidences(
    token: Tkn, entities: List[Dict], extractors: Optional[Set[Text]] = None
) -> float:
    """Get the confidence value of the best fitting entity.

    If multiple confidence values are present, e.g. for type, role, group, we
    pick the lowest confidence value.

    Args:
        token: the token we are looking at
        entities: the available entities
        extractors: the extractor of interest

    Returns:
        the confidence value
    """
    ent = ent_for_token_determination(token, entities, extractors)

    if ent is None:
        return 0.0

    if ent.get("extractor") not in CONFIDENT_EXTRACTORS:
        return 0.0

    confidence_type = ent.get(ENTITY_ATTR_CONFIDENCE_TYPE_VAL) or 1.0
    confidence_role = ent.get(ENTITY_ATTR_CONFIDENCE_ROLE) or 1.0
    confidence_group = ent.get(ENTITY_ATTR_CONFIDENCE_GRP) or 1.0

    return min(confidence_type, confidence_role, confidence_group)


def aligning_all_ent_preds(
    entity_results: List[entity_evaluation_res], extractors: Set[Text]
) -> List[Dict]:
    """Aligns entity predictions to the message tokens for the whole dataset
    using align_entity_predictions.

    Args:
        entity_results: list of entity prediction results
        extractors: the entity extractors that should be considered

    Returns: list of dictionaries containing the true token labels and token
    labels from the extractors
    """
    preds_aligned = []
    for result in entity_results:
        preds_aligned.append(aligning_ent_preds(result, extractors))

    return preds_aligned


def fetch_eval_data(
    interpreter: Interpreter, test_data: TrainingDataSet
) -> Tuple[
    List[intent_evaluation_res],
    List[response_selection_evaluation_res],
    List[entity_evaluation_res],
]:  # pragma: no cover
    """Runs the model for the test set and extracts targets and predictions.

    Returns intent results (intent targets and predictions, the original
    messages and the confidences of the predictions), response results (
    response targets and predictions) as well as entity results
    (entity_targets, entity_predictions, and tokens).

    Args:
        interpreter: the interpreter
        test_data: test data

    Returns: intent, response, and entity evaluation results
    """
    log.info("Running model for predictions:")

    int_res, ent_res, resp_selection_res = [], [], []

    resp_labels = [
        e.get(KEY_INTENT_RESPONSE)
        for e in test_data.intent_exp
        if e.get(KEY_INTENT_RESPONSE) is not None
    ]
    ibt_label = [e.get(INTENTION) for e in test_data.intent_exp]
    intents_eval_check = (
            int_classifier_present_check(interpreter) and len(set(ibt_label)) >= 2
    )
    resp_selection_eval_check = (
            resp_selector_present_check(interpreter) and len(set(resp_labels)) >= 2
    )
    resp_selector_types_available = fetch_resp_selector_types_available(
        interpreter
    )

    entities_evaluation_check = ent_extractor_present_check(interpreter)

    for example in tqdm(test_data.nlu_exp):
        res = interpreter.parse_func(example.get(TXT), only_output_properties=False)

        if intents_eval_check:
            pred_intent = res.get(INTENTION, {}) or {}
            int_res.append(
                intent_evaluation_res(
                    example.get(INTENTION, ""),
                    pred_intent.get(KEY_INTENT_NAME),
                    res.get(TXT, {}),
                    pred_intent.get("confidence"),
                )
            )

        if resp_selection_eval_check:

            # including all examples here. Empty response examples are filtered at the
            # time of metric calculation
            tar_intent = example.get(INTENTION, "")
            selector_props = res.get(PROP_NAME_RESPONSE_PICKER, {})

            if tar_intent in resp_selector_types_available:
                resp_pred_key = tar_intent
            else:
                resp_pred_key = DFAULT_INTENT_RESPONSE_PICKER

            resp_pred = selector_props.get(
                resp_pred_key, {}
            ).get(PREDICTION_KEY_RESPONSE_PICKER, {})

            intent_resp_key_tar = example.get(KEY_INTENT_RESPONSE, "")

            resp_selection_res.append(
                response_selection_evaluation_res(
                    intent_resp_key_tar,
                    resp_pred.get(KEY_INTENT_RESPONSE),
                    res.get(TXT, {}),
                    resp_pred.get(KEY_PREDICTED_CONFIDENCE),
                )
            )

        if entities_evaluation_check:
            ent_res.append(
                entity_evaluation_res(
                    example.get(ENTITIES_NAME, []),
                    res.get(ENTITIES_NAME, []),
                    res.get(NAMES_OF_TOKENS[TXT], []),
                    res.get(TXT, ""),
                )
            )

    return int_res, resp_selection_res, ent_res


def fetch_ent_extractors(interpreter: Interpreter) -> Set[Text]:
    """Finds the names of entity extractors used by the interpreter.

    Processors are removed since they do not detect the boundaries themselves.

    Args:
        interpreter: the interpreter

    Returns: entity extractor names
    """
    from convo.nlu.extractors.extractor import ExtractorEntity
    from convo.nlu.classifiers.diet_classifier import DIETClassifier

    fetch_extractors = set()
    for c in interpreter.pipeline:
        if isinstance(c, ExtractorEntity):
            if isinstance(c, DIETClassifier):
                if c.component_config[ENTITY_IDENTIFICATION]:
                    fetch_extractors.add(c.name)
            else:
                fetch_extractors.add(c.name)

    return fetch_extractors - PROCESSORS_ENTITY


def ent_extractor_present_check(interpreter: Interpreter) -> bool:
    """Checks whether entity extractor is present."""

    extractors = fetch_ent_extractors(interpreter)
    return extractors != []


def int_classifier_present_check(interpreter: Interpreter) -> bool:
    """Checks whether intent classifier is present."""

    from convo.nlu.classifiers.classifier import IntentionClassifier

    intention_classifiers = [
        c.name for c in interpreter.pipeline if isinstance(c, IntentionClassifier)
    ]
    return intention_classifiers != []


def resp_selector_present_check(interpreter: Interpreter) -> bool:
    """Checks whether response selector is present."""

    from convo.nlu.selectors.response_selector import ResponseSelector

    resp_selectors = [
        c.name for c in interpreter.pipeline if isinstance(c, ResponseSelector)
    ]
    return resp_selectors != []


def fetch_resp_selector_types_available(interpreter: Interpreter) -> List[Text]:
    """Gets all available response selector types."""

    from convo.nlu.selectors.response_selector import ResponseSelector

    types_of_resp_selector = [
        c.retrieval_intent
        for c in interpreter.pipeline
        if isinstance(c, ResponseSelector)
    ]

    return types_of_resp_selector


def delete_pre_trained_extractors(pipe_line: List[Element]) -> List[Element]:
    """Remove pre-trained extractors from the pipeline.

    Remove pre-trained extractors so that entities from pre-trained extractors
    are not predicted upon parsing.

    Args:
        pipe_line: the pipeline

    Returns:
        Updated pipeline
    """
    pipe_line = [c for c in pipe_line if c.name not in PRE_TRAINED_EXTRACTORS]
    return pipe_line


def run_eval(
    data_path: Text,
    model_path: Text,
    output_directory: Optional[Text] = None,
    successes: bool = False,
    errors: bool = False,
    component_builder: Optional[ElementBuilder] = None,
    disable_plotting: bool = False,
) -> Dict:  # pragma: no cover
    """Evaluate intent classification, response selection and entity extraction.

    Args:
        data_path: path to the test data
        model_path: path to the model
        output_directory: path to folder where all output will be stored
        successes: if true successful predictions are written to a file
        errors: if true incorrect predictions are written to a file
        component_builder: component builder
        disable_plotting: if true confusion matrix and histogram will not be rendered

    Returns: dictionary containing evaluation results
    """
    import convo.shared.nlu.training_data.loading

    # get the metadata config from the package data
    interpreter = Interpreter.load(model_path, component_builder)

    interpreter.pipeline = delete_pre_trained_extractors(interpreter.pipeline)
    testing_dataset = convo.shared.nlu.training_data.loading.load_data_set(
        data_path, interpreter.model_metadata.lang
    )

    result: Dict[Text, Optional[Dict]] = {
        "intent_evaluation": None,
        "entity_evaluation": None,
        "response_selection_evaluation": None,
    }

    if output_directory:
        convo.shared.utils.io.create_dir(output_directory)

    (intent_results, response_selection_results, entity_results,) = fetch_eval_data(
        interpreter, testing_dataset
    )

    if intent_results:
        log.info("Intent evaluation results:")
        result["intent_evaluation"] = calculate_intents(
            intent_results, output_directory, successes, errors, disable_plotting
        )

    if response_selection_results:
        log.info("Response selection evaluation results:")
        result["response_selection_evaluation"] = evaluating_res_selections(
            response_selection_results,
            output_directory,
            successes,
            errors,
            disable_plotting,
        )

    if any(entity_results):
        log.info("Entity evaluation results:")
        extractors_name = fetch_ent_extractors(interpreter)
        result["entity_evaluation"] = entities_evaluation(
            entity_results,
            extractors_name,
            output_directory,
            successes,
            errors,
            disable_plotting,
        )

    telemetry.traverse_nlu_model_test(testing_dataset)

    return result


def generating_folders(
    n: int, training_data: TrainingDataSet
) -> Iterator[Tuple[TrainingDataSet, TrainingDataSet]]:
    """Generates n cross validation folds for given training data."""

    from sklearn.model_selection import StratifiedKFold

    skf = StratifiedKFold(n_splits=n, shuffle=True)
    a = training_data.intent_exp

    # Get labels as they appear in the training data because we want a
    # stratified split on all convo_intents(including retrieval convo_intents if they exist)
    b = [example.get_complete_intent() for example in a]
    for i_fold, (train_index, test_index) in enumerate(skf.split(a, b)):
        log.debug(f"Fold: {i_fold}")
        train = [a[i] for i in train_index]
        testing = [a[i] for i in test_index]
        yield (
            TrainingDataSet(
                training_examples=train,
                entity_synonyms=training_data.entity_synonyms,
                regex_features=training_data.regex_features,
                responses=training_data.responses,
            ),
            TrainingDataSet(
                training_examples=testing,
                entity_synonyms=training_data.entity_synonyms,
                regex_features=training_data.regex_features,
                responses=training_data.responses,
            ),
        )


def merge_res(
    intent_metrics: intent_metrics,
    entity_metrics: entity_metrics,
    response_selection_metrics: res_select_metrics,
    interpreter: Interpreter,
    data: TrainingDataSet,
    int_ress: Optional[List[intent_evaluation_res]] = None,
    ent_ress: Optional[List[entity_evaluation_res]] = None,
    resp_selection_ress: Optional[
        List[response_selection_evaluation_res]
    ] = None,
) -> Tuple[intent_metrics, entity_metrics, res_select_metrics]:
    """Collects intent, response selection and entity metrics for cross validation
    folds.

    If `intent_results`, `response_selection_results` or `entity_results` is provided
    as a list, prediction results are also collected.

    Args:
        intent_metrics: intent metrics
        entity_metrics: entity metrics
        response_selection_metrics: response selection metrics
        interpreter: the interpreter
        data: training data
        int_ress: intent evaluation results
        ent_ress: entity evaluation results
        resp_selection_ress: reponse selection evaluation results

    Returns: intent, entity, and response selection metrics
    """
    (
        intention_current_metrics,
        entity_present_metrics,
        resp_selection_surrent_metrics,
        current_int_ress,
        current_ent_ress,
        current_respo_select_res,
    ) = metrics_computation(interpreter, data)

    if int_ress is not None:
        int_ress += current_int_ress

    if ent_ress is not None:
        ent_ress += current_ent_ress

    if resp_selection_ress is not None:
        resp_selection_ress += current_respo_select_res

    for k, v in intention_current_metrics.items():
        intent_metrics[k] = v + intent_metrics[k]

    for k, v in resp_selection_surrent_metrics.items():
        response_selection_metrics[k] = v + response_selection_metrics[k]

    for extractor, extractor_metric in entity_present_metrics.items():
        entity_metrics[extractor] = {
            k: v + entity_metrics[extractor][k] for k, v in extractor_metric.items()
        }

    return intent_metrics, entity_metrics, response_selection_metrics


def _consist_ent_tags(entity_results: List[entity_evaluation_res]) -> bool:

    for result in entity_results:
        if result.entity_targets or result.entity_predictions:
            return True
    return False


def cross_validation(
    data: TrainingDataSet,
    n_folds: int,
    nlu_configuration: Union[ConvoNLUModelConfiguration, Text],
    output: Optional[Text] = None,
    successes: bool = False,
    errors: bool = False,
    disable_plotting: bool = False,
) -> Tuple[cv_evaluation_result, cv_evaluation_result, cv_evaluation_result]:
    """Stratified cross validation on data.

    Args:
        data: Training Data
        n_folds: integer, number of cv folds
        nlu_configuration: nlu config file
        output: path to folder where reports are stored
        successes: if true successful predictions are written to a file
        errors: if true incorrect predictions are written to a file
        disable_plotting: if true no confusion matrix and historgram plates are created

    Returns:
        dictionary with key, list structure, where each entry in list
              corresponds to the relevant result for one fold
    """
    import convo.nlu.config

    if isinstance(nlu_configuration, str):
        nlu_configuration = convo.nlu.config.load(nlu_configuration)

    if output:
        convo.shared.utils.io.create_dir(output)

    instructor = Instructor(nlu_configuration)
    instructor.pipeline = delete_pre_trained_extractors(instructor.pipeline)

    intent_train_metrics: intent_metrics = defaultdict(list)
    intent_test_metrics: intent_metrics = defaultdict(list)
    ent_training_metrics: entity_metrics = defaultdict(lambda: defaultdict(list))
    ent_testing_metrics: entity_metrics = defaultdict(lambda: defaultdict(list))
    response_selection_train_metrics: res_select_metrics = defaultdict(list)
    response_selection_test_metrics: res_select_metrics = defaultdict(list)

    intent_test_results: List[intent_evaluation_res] = []
    entity_test_results: List[entity_evaluation_res] = []
    response_selection_test_results: List[response_selection_evaluation_res] = []
    int_classifier_available = False
    resp_selector_available = False
    ent_eval_possible = False
    fetch_extractors: Set[Text] = set()

    for train, test in generating_folders(n_folds, data):
        fetch_interpreter = instructor.train(train)

        # calculate train accuracy
        merge_res(
            intent_train_metrics,
            ent_training_metrics,
            response_selection_train_metrics,
            fetch_interpreter,
            train,
        )
        # calculate test accuracy
        merge_res(
            intent_test_metrics,
            ent_testing_metrics,
            response_selection_test_metrics,
            fetch_interpreter,
            test,
            intent_test_results,
            entity_test_results,
            response_selection_test_results,
        )

        if not fetch_extractors:
            fetch_extractors = fetch_ent_extractors(fetch_interpreter)
            ent_eval_possible = (
                    ent_eval_possible
                    or _consist_ent_tags(entity_test_results)
            )

        if int_classifier_present_check(fetch_interpreter):
            int_classifier_available = True

        if resp_selector_present_check(fetch_interpreter):
            resp_selector_available = True

    if int_classifier_available and intent_test_results:
        log.info("Accumulated test folds intent evaluation results:")
        calculate_intents(
            intent_test_results, output, successes, errors, disable_plotting
        )

    if fetch_extractors and ent_eval_possible:
        log.info("Accumulated test folds entity evaluation results:")
        entities_evaluation(
            entity_test_results, fetch_extractors, output, successes, errors, disable_plotting
        )

    if resp_selector_available and response_selection_test_results:
        log.info("Accumulated test folds response selection evaluation results:")
        evaluating_res_selections(
            response_selection_test_results, output, successes, errors, disable_plotting
        )

    if not ent_eval_possible:
        ent_testing_metrics = defaultdict(lambda: defaultdict(list))
        ent_training_metrics = defaultdict(lambda: defaultdict(list))

    return (
        cv_evaluation_result(dict(intent_train_metrics), dict(intent_test_metrics)),
        cv_evaluation_result(dict(ent_training_metrics), dict(ent_testing_metrics)),
        cv_evaluation_result(
            dict(response_selection_train_metrics),
            dict(response_selection_test_metrics),
        ),
    )


def tar_pred_from(
    results: Union[
        List[intent_evaluation_res], List[response_selection_evaluation_res]
    ],
    target_key: Text,
    prediction_key: Text,
) -> Iterator[Iterable[Optional[Text]]]:
    return zip(*[(getattr(r, target_key), getattr(r, prediction_key)) for r in results])


def metrics_computation(
    interpreter: Interpreter, training_data: TrainingDataSet
) -> Tuple[
    intent_metrics,
    entity_metrics,
    res_select_metrics,
    List[intent_evaluation_res],
    List[entity_evaluation_res],
    List[response_selection_evaluation_res],
]:
    """Computes metrics for intent classification, response selection and entity
    extraction.

    Args:
        interpreter: the interpreter
        training_data: training data

    Returns: intent, response selection and entity metrics, and prediction results.
    """
    int_ress, resp_selection_ress, ent_ress = fetch_eval_data(
        interpreter, training_data
    )

    int_ress = del_empty_intent_exps(int_ress)

    resp_selection_ress = del_empty_res_examples(
        resp_selection_ress
    )

    int_metrics = {}
    if int_ress:
        int_metrics = _metrics_computation(
            int_ress, "intent_target", "intent_prediction"
        )

    ent_metrics = {}
    if ent_ress:
        ent_metrics = _ent_metrics_computation(ent_ress, interpreter)

    resp_selection_metrics = {}
    if resp_selection_ress:
        resp_selection_metrics = _metrics_computation(
            resp_selection_ress,
            "intent_response_key_target",
            "intent_response_key_prediction",
        )

    return (
        int_metrics,
        ent_metrics,
        resp_selection_metrics,
        int_ress,
        ent_ress,
        resp_selection_ress,
    )


def nlu_comparison(
    configs: List[Text],
    data: TrainingDataSet,
    exclusion_percentages: List[int],
    f_score_results: Dict[Text, Any],
    model_names: List[Text],
    output: Text,
    runs: int,
) -> List[int]:
    """
    Trains and compares multiple NLU models.
    For each run and exclusion percentage a model per config file is trained.
    Thereby, the model is trained only on the current percentage of training data.
    Afterwards, the model is tested on the complete test data of that run.
    All results are stored in the provided output dir.

    Args:
        configs: config files needed for training
        data: training data
        exclusion_percentages: percentages of training data to exclude during comparison
        f_score_results: dictionary of model name to f-score results per run
        model_names: names of the models to train
        output: the output dir
        runs: number of comparison runs

    Returns: training examples per run
    """

    from convo.train import supervise_nlu

    training_eg_per_run = []

    for run in range(runs):

        log.info("Beginning comparison run {}/{}".format(run + 1, runs))

        run_path_flow = os.path.join(output, "run_{}".format(run + 1))
        io_utils.creating_path(run_path_flow)

        testing_path = os.path.join(run_path_flow, DATA_FILE_TESTING)
        io_utils.creating_path(testing_path)

        training,testing = data.training_test_split()
        convo.shared.utils.io.writing_text_file(testing.nlu_markdown(), testing_path)

        for percentage in exclusion_percentages:
            percentage_str = f"{percentage}%_exclusion"

            _, training_included = training.training_test_split(percentage / 100)
            # only count for the first run and ignore the others
            if run == 0:
                training_eg_per_run.append(len(training_included.nlu_exp))

            path_model_out = os.path.join(run_path_flow, percentage_str)
            train_split_path = os.path.join(path_model_out, "train")
            path_train_nlu_split = os.path.join(train_split_path, DATA_FILE_TRANING)
            path_train_nlg_split = os.path.join(train_split_path, NLG_DATA_FILE)
            io_utils.creating_path(path_train_nlu_split)
            convo.shared.utils.io.writing_text_file(
                training_included.nlu_markdown(), path_train_nlu_split
            )
            convo.shared.utils.io.writing_text_file(
                training_included.nlg_markdown(), path_train_nlg_split
            )

            for nlu_config, model_name in zip(configs, model_names):
                log.info(
                    "Evaluating configuration '{}' with {} training data.".format(
                        model_name, percentage_str
                    )
                )

                try:
                    model_path_flow = supervise_nlu(
                        nlu_config,
                        train_split_path,
                        path_model_out,
                        fixed_model_name=model_name,
                    )
                except Exception as e:  # skipcq: PYL-W0703
                    # general exception catching needed to continue evaluating others
                    # model configurations
                    log.warning(f"Training model '{model_name}' failed. Error: {e}")
                    f_score_results[model_name][run].append(0.0)
                    continue

                model_path_flow = os.path.join(fetch_model(model_path_flow), "nlu")

                out_path = os.path.join(path_model_out, f"{model_name}_report")
                res = run_eval(
                    testing_path, model_path_flow, output_directory=out_path, errors=True
                )

                f1 = res["intent_evaluation"]["f1_score"]
                f_score_results[model_name][run].append(f1)

    return training_eg_per_run


def _metrics_computation(
    results: Union[
        List[intent_evaluation_res], List[response_selection_evaluation_res]
    ],
    target_key: Text,
    prediction_key: Text,
) -> Union[intent_metrics, res_select_metrics]:
    """Computes evaluation metrics for a given corpus and returns the results.

    Args:
        results: evaluation results
        target_key: target key name
        prediction_key: prediction key name

    Returns: metrics
    """
    from convo.test import fetch_evaluation_metrics

    # compute fold metrics
    objective, preds = tar_pred_from(
        results, target_key, prediction_key
    )
    _, exactness, x1, efficiency = fetch_evaluation_metrics(objective, preds)

    return {"Accuracy": [efficiency], "F1-score": [x1], "Precision": [exactness]}


def _ent_metrics_computation(
    entity_results: List[entity_evaluation_res], interpreter: Interpreter
) -> entity_metrics:
    """Computes entity evaluation metrics and returns the results.

    Args:
        entity_results: entity evaluation results
        interpreter: the interpreter

    Returns: entity metrics
    """
    from convo.test import fetch_evaluation_metrics

    entity_metric_results: entity_metrics = defaultdict(lambda: defaultdict(list))
    fetch_extractors = fetch_ent_extractors(interpreter)

    if not fetch_extractors:
        return entity_metric_results

    preds_aligned = aligning_all_ent_preds(entity_results, fetch_extractors)

    targets_merged = merging_tags(preds_aligned)
    targets_merged = sub_labels(targets_merged, ENTITY_TAG_ABSENT, NOT_ENTITY)

    for extractor in fetch_extractors:
        preds_merged = merging_tags(preds_aligned, extractor)
        preds_merged = sub_labels(
            preds_merged, ENTITY_TAG_ABSENT, NOT_ENTITY
        )
        _, exactness, f1, efficiency = fetch_evaluation_metrics(
            targets_merged, preds_merged, exclude_label=NOT_ENTITY
        )
        entity_metric_results[extractor]["Accuracy"].append(efficiency)
        entity_metric_results[extractor]["F1-score"].append(f1)
        entity_metric_results[extractor]["Precision"].append(exactness)

    return entity_metric_results


def logging_ress(results: intent_metrics, dataset_name: Text) -> None:
    """Logs results of cross validation.

    Args:
        results: dictionary of results returned from cross validation
        dataset_name: string of which dataset the results are from, e.g. test/train
    """
    for k, v in results.items():
        log.info(
            "{} {}: {:.3f} ({:.3f})".format(dataset_name, k, np.mean(v), np.std(v))
        )


def log_ent_ress(results: entity_metrics, dataset_name: Text) -> None:
    """Logs entity results of cross validation.

    Args:
        results: dictionary of dictionaries of results returned from cross validation
        dataset_name: string of which dataset the results are from, e.g. test/train
    """
    for extractor, result in results.items():
        log.info(f"Entity extractor: {extractor}")
        logging_ress(result, dataset_name)
