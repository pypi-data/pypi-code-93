# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Entry script that is invoked by the driver script from automl."""
import importlib
import logging
import os

from azureml.automl.dnn.nlp.classification.io.read import dataloader
from azureml.automl.dnn.nlp.classification.io.write.save_utils import save_model_wrapper
from azureml.automl.dnn.nlp.classification.multilabel.bert_class import BERTClass
from azureml.automl.dnn.nlp.classification.multilabel.trainer import PytorchTrainer
from azureml.automl.dnn.nlp.classification.multilabel.model_wrapper import ModelWrapper
from azureml.automl.dnn.nlp.classification.common.constants import ModelNames
from azureml.automl.dnn.nlp.common.constants import TaskNames, OutputLiterals
from azureml.automl.dnn.nlp.common.utils import save_script
from azureml.automl.dnn.nlp.classification.multilabel.distributed_trainer import HorovodDistributedTrainer
from azureml.automl.dnn.nlp.common import utils

from azureml.core.run import Run
from azureml._common._error_definition import AzureMLError
from azureml.automl.core.shared._diagnostics.automl_error_definitions import ExecutionFailure
from azureml.automl.core.shared.exceptions import ValidationException
from azureml.train.automl.runtime._entrypoints.utils import common

horovod_spec = importlib.util.find_spec("horovod")
has_horovod = horovod_spec is not None

_logger = logging.getLogger(__name__)


def run(automl_settings):
    """Invoke training by passing settings and write the output model.
    :param automl_settings: dictionary with automl settings
    """
    run = Run.get_context()
    workspace = run.experiment.workspace

    if utils.is_main_process():
        utils.prepare_run_properties(run, ModelNames.BERT_BASE_UNCASED)

    automl_settings_obj = common.parse_settings(run, automl_settings)  # Parse settings internally initializes logger

    is_gpu = automl_settings_obj.is_gpu if hasattr(automl_settings_obj, "is_gpu") else True  # Expect gpu by default
    dataset_id = automl_settings_obj.dataset_id
    if hasattr(automl_settings_obj, "validation_dataset_id"):
        valid_dataset_id = automl_settings_obj.validation_dataset_id
    else:
        valid_dataset_id = None

    label_column_name = automl_settings_obj.label_column_name
    if label_column_name is None:
        raise ValidationException._with_error(
            AzureMLError.create(
                ExecutionFailure,
                error_details="Need to pass in label_column_name argument for training"
            )
        )

    training_set, validation_set, num_label_cols, vectorizer = dataloader.dataset_loader(dataset_id, valid_dataset_id,
                                                                                         label_column_name, workspace,
                                                                                         is_multiclass_training=False)

    if hasattr(automl_settings_obj, "enable_distributed_dnn_training") and \
            automl_settings_obj.enable_distributed_dnn_training is True and has_horovod:
        trainer = HorovodDistributedTrainer(BERTClass, num_label_cols)
    else:
        trainer = PytorchTrainer(BERTClass, num_label_cols, is_gpu)
    model = trainer.train(training_set)

    if utils.is_main_process() and validation_set is not None:
        accuracy, f1_score_micro, f1_score_macro = trainer.compute_metrics(validation_set)

        # Log metrics
        run.log('accuracy', accuracy)
        run.log('f1_score_micro', f1_score_micro)
        run.log('f1_score_macro', f1_score_macro)

        model_wrapper = ModelWrapper(model, training_set.tokenizer, vectorizer, label_column_name)
        multilabel_directory = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                            "io", "write", TaskNames.MULTILABEL)
        model_path = save_model_wrapper(model_wrapper)

        save_script(OutputLiterals.SCORE_SCRIPT, multilabel_directory)
        deploy_script_path = save_script(OutputLiterals.DEPLOY_SCRIPT, multilabel_directory)

        conda_file_path = utils.save_conda_yml(run.get_environment())

        # 2147483648 bytes is 2GB
        # TODO: set the model size based on real model, tokenizer, etc size
        utils.prepare_post_run_properties(run,
                                          model_path,
                                          2147483648,
                                          conda_file_path,
                                          deploy_script_path,
                                          "accuracy",
                                          accuracy)
