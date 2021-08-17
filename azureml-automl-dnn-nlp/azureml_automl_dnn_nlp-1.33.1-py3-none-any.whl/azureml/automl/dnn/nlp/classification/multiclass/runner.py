# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Entry script that is invoked by the driver script from automl."""
import os
from azureml.core.run import Run
from azureml._common._error_definition import AzureMLError
from azureml.automl.core.shared._diagnostics.automl_error_definitions import ExecutionFailure
from azureml.automl.core.shared.exceptions import ValidationException
from azureml.automl.dnn.nlp.classification.io.read import dataloader
from azureml.automl.dnn.nlp.classification.multiclass.trainer import TextClassificationTrainer
from azureml.automl.dnn.nlp.common.constants import TaskNames, OutputLiterals
from azureml.automl.dnn.nlp.common.utils import save_script
from azureml.train.automl.runtime._entrypoints.utils.common import parse_settings


def run(automl_settings):
    """Invoke training by passing settings and write the output model.
    :param automl_settings: dictionary with automl settings
    """
    run = Run.get_context()
    workspace = run.experiment.workspace

    automl_settings_obj = parse_settings(run, automl_settings)  # Parse settings internally initializes logger

    dataset_id = automl_settings_obj.dataset_id
    if hasattr(automl_settings_obj, "validation_dataset_id"):
        validation_dataset_id = automl_settings_obj.validation_dataset_id
    else:
        validation_dataset_id = None

    dataset_language = automl_settings_obj.language
    label_column_name = automl_settings_obj.label_column_name
    if label_column_name is None:
        raise ValidationException._with_error(
            AzureMLError.create(
                ExecutionFailure,
                error_details="Need to pass in label_column_name argument for training"
            )
        )

    training_set, validation_set, label_list = dataloader.dataset_loader(dataset_id, validation_dataset_id,
                                                                         label_column_name, workspace,
                                                                         dataset_language,
                                                                         is_multiclass_training=True)
    trainer_class = TextClassificationTrainer(label_list, dataset_language)
    trainer_class.train(training_set)
    if validation_set is not None:
        results = trainer_class.validate(validation_set)
        run.log('accuracy', results['eval_accuracy'])

    save_script(OutputLiterals.SCORE_SCRIPT,
                os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                             "io", "write", TaskNames.MULTICLASS))
