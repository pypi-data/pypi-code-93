# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Scoring functions that can load a serialized model and predict."""

import logging
import torch
import numpy as np
import pandas as pd

from sklearn.feature_extraction.text import CountVectorizer
from torch.utils.data import DataLoader
from typing import Union

from azureml.core import Dataset as AmlDataset
from azureml.core.run import Run
from azureml.automl.dnn.nlp.classification.common.constants import (
    MultiLabelParameters,
    DatasetLiterals
)
from azureml.automl.dnn.nlp.classification.io.read.pytorch_dataset_wrapper import PyTorchDatasetWrapper
from azureml.automl.dnn.nlp.classification.io.read.read_utils import load_model_wrapper
from azureml.automl.dnn.nlp.classification.io.read.dataloader import concat_text_columns
from azureml.automl.dnn.nlp.common.constants import Warnings


_logger = logging.getLogger(__name__)


class MultilabelInferencer:
    """Class to perform inferencing using training runId and on an unlabeled dataset"""

    def __init__(self,
                 run: Run,
                 device: Union[str, torch.device]):
        """Function to initialize the inferencing object

        :param: Run object
        :param device: device to be used for inferencing
        """
        self.run_object = run
        self.device = device

        if self.device == "cpu":
            _logger.warning(Warnings.CPU_DEVICE_WARNING)

        self.batch_size = MultiLabelParameters.VALID_BATCH_SIZE
        self.workspace = self.run_object.experiment.workspace

    def obtain_dataloader(self, df: pd.DataFrame, vectorizer: CountVectorizer,
                          label_column_name: str) -> DataLoader:
        """Get the Dataset, convert it to required format and create DataLoader

        :param df: The input dataframe
        :param vectorizer: vectorizer with label column names
        :param label_column_name: Name/title of the label column
        :return: Dataframe and DataLoader for the dataset to perform inferencing on
        """
        text_df = concat_text_columns(df, label_column_name)

        # Create dataloader
        inference_set = PyTorchDatasetWrapper(text_df)
        inference_data_loader = DataLoader(inference_set, batch_size=self.batch_size)

        return inference_data_loader

    def predict(self,
                model: torch.nn.Module,
                vectorizer: CountVectorizer,
                df: pd.DataFrame,
                inference_data_loader: DataLoader,
                label_column_name: str) -> pd.DataFrame:
        """Generate predictions using model

        :param model: Trained model
        :param vectorizer: vectorizer
        :param df: DataFrame to make predictions on
        :param inference_data_loader: dataloader
        :param label_column_name: Name/title of the label column
        :return: Dataframe with predictions
        """
        _logger.info("[start inference: batch_size: {}]".format(self.batch_size))

        model.to(self.device)
        model.eval()
        fin_outputs = []
        with torch.no_grad():
            for _, data in enumerate(inference_data_loader, 0):
                ids = data['ids'].to(self.device, dtype=torch.long)
                mask = data['mask'].to(self.device, dtype=torch.long)
                token_type_ids = data['token_type_ids'].to(self.device, dtype=torch.long)
                outputs = model(ids, mask, token_type_ids)
                fin_outputs.extend(torch.sigmoid(outputs).cpu().detach().numpy().tolist())

        # Create dataframes with label columns
        label_columns = vectorizer.get_feature_names()
        label_columns_str = ",".join(label_columns)
        formatted_outputs = [[label_columns_str, ",".join(map(str, list(xi)))] for xi in fin_outputs]
        predicted_labels_df = pd.DataFrame(np.array(formatted_outputs))
        predicted_labels_df.columns = [label_column_name, DatasetLiterals.LABEL_CONFIDENCE]
        predicted_df = pd.concat([df, predicted_labels_df], join='outer', axis=1)

        return predicted_df

    def score(self, input_dataset_id: str, label_column_name: str) -> pd.DataFrame:
        """Generate predictions from input files.

        :param input_dataset_id: The input dataset id
        :param label_column_name: Name/title of the label column
        :return: Dataframe with predictions
        """
        model_wrapper = load_model_wrapper(self.run_object)
        vectorizer = model_wrapper.vectorizer

        # Fetch AmlDataset object
        ds = AmlDataset.get_by_id(self.workspace, input_dataset_id)
        _logger.info("Type of input Dataset is: {}".format(type(ds)))

        # Convert AmlDataset to dataframe and obtain dataloader
        df = ds.to_pandas_dataframe()
        inference_data_loader = self.obtain_dataloader(df, vectorizer, label_column_name)

        return self.predict(model_wrapper.model, vectorizer, df, inference_data_loader, label_column_name)
