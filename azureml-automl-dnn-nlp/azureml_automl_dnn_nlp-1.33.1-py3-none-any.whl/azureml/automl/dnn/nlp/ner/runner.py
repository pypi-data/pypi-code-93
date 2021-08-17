# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Entry script that is invoked by the driver script from automl."""

import logging
import os

from transformers import (
    AutoTokenizer
)

from azureml.core.run import Run
from azureml.train.automl.runtime._entrypoints.utils.common import parse_settings
from azureml.automl.dnn.nlp.common.constants import DataLiterals, NERModelParameters, OutputLiterals
from azureml.automl.dnn.nlp.ner.io.read.dataloader import load_dataset
from azureml.automl.dnn.nlp.ner.trainer import NERPytorchTrainer
from azureml.automl.dnn.nlp.common.utils import save_script

_logger = logging.getLogger(__name__)


def run(automl_settings):
    """Invoke training by passing settings and write the output model.

    :param automl_settings: dictionary with automl settings
    """
    # Get Run Info
    run = Run.get_context()

    # Check whether the run is for labeling service. If so, it needs extra input data conversion.
    # current run id: AutoML_<guid>_HD_0
    # parent HD run id: run.parent AutoML_<guid>_HD
    # original parent AutoML run: run.parent.parent AutoML_<guid>
    run_source = run.parent.parent.properties.get(Run._RUNSOURCE_PROPERTY, None)
    is_labeling_run = True if run_source == 'Labeling' else False

    workspace = run.experiment.workspace

    # Get dataset id
    automl_settings_obj = parse_settings(run, automl_settings)
    dataset_id = automl_settings_obj.dataset_id
    if hasattr(automl_settings_obj, "validation_dataset_id"):
        validation_dataset_id = automl_settings_obj.validation_dataset_id
    else:
        validation_dataset_id = None

    # Set Defaults
    data_dir = DataLiterals.NER_DATA_DIR
    output_dir = OutputLiterals.OUTPUT_DIR
    labels_filename = OutputLiterals.LABELS_FILE

    # Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained(NERModelParameters.MODEL_NAME)

    # Save and load dataset
    train_dataset, eval_dataset, label_list = load_dataset(
        workspace,
        data_dir,
        output_dir,
        labels_filename,
        tokenizer,
        dataset_id,
        validation_dataset_id,
        is_labeling_run
    )

    # Train model
    trainer = NERPytorchTrainer(
        label_list,
        output_dir
    )
    trainer.train(train_dataset)
    if trainer.trainer.is_world_process_zero():
        tokenizer.save_pretrained(output_dir)

    # Validate model if validation dataset is provided
    if eval_dataset:
        results = trainer.validate(eval_dataset)
        # Log results
        run.log('f1_score_micro', results['eval_f1'])
        run.log('accuracy', results['eval_accuracy'])

    # Save scoring script
    save_script(OutputLiterals.SCORE_SCRIPT, os.path.join(os.path.dirname(os.path.abspath(__file__)), "io", "write"))
