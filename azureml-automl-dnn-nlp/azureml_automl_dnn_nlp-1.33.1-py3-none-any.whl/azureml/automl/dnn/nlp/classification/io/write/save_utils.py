# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Utility functions to write the final model and checkpoints during training"""

import os
import pickle

from azureml.automl.dnn.nlp.common.constants import OutputLiterals
from azureml.automl.dnn.nlp.classification.multilabel.model_wrapper import ModelWrapper


def save_model_wrapper(model: ModelWrapper) -> str:
    """Save a model to outputs directory.

    :param model: Trained model
    :type model: BERTClass
    """
    os.makedirs(OutputLiterals.OUTPUT_DIR, exist_ok=True)
    model_path = os.path.join(OutputLiterals.OUTPUT_DIR, OutputLiterals.MULTILABEL_MODEL_FILE_NAME)

    # Save the model
    with open(model_path, "wb") as f:
        pickle.dump(model, f)
    return model_path
