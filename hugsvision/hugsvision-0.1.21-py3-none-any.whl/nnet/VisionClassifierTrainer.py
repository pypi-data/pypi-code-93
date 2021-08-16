# -*- coding: utf-8 -*-

import os
import math
import random
import argparse
from pathlib import Path
from datetime import datetime
from collections import Counter

import torch
import torchmetrics
from torchmetrics import Accuracy
from torch.utils.data import DataLoader

from PIL import Image, ImageEnhance
from sklearn.metrics import precision_recall_fscore_support as f_score

from transformers import Trainer
from transformers import default_data_collator
from transformers.training_args import TrainingArguments
from transformers.feature_extraction_utils import FeatureExtractionMixin

from tqdm import tqdm
from tabulate import tabulate

from hugsvision.dataio.ImageClassificationCollator import ImageClassificationCollator

class VisionClassifierTrainer:

  """
  🤗 Constructor for the image classifier trainer
  """
  def __init__(
    self,
    ids2labels,
    model             :torch.nn.Module,
    feature_extractor :FeatureExtractionMixin,
    dataset           :torch.utils.data.Dataset,
    model_name        :str,
    output_dir        :str,
    lr           = 2e-5,
    batch_size   = 8,
    max_epochs   = 1,
    cores        = 4,
    eval_metric  = "accuracy",
    shuffle      = True,
    fp16         = True,
    balanced     = False,
    augmentation = False,
  ):

    self.model_name        = model_name
    self.dataset           = dataset
    self.output_dir        = output_dir
    self.lr                = lr
    self.batch_size        = batch_size
    self.max_epochs        = max_epochs
    self.shuffle           = shuffle
    self.model             = model
    self.feature_extractor = feature_extractor
    self.cores             = cores
    self.fp16              = fp16
    self.eval_metric       = eval_metric
    self.ids2labels        = ids2labels
    self.balanced          = balanced
    self.augmentation      = augmentation

    # Processing device (CPU / GPU)
    self.device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

    # Setup the metric
    self.metric = torchmetrics.Accuracy()
    
    # Get the classifier collator
    self.collator = ImageClassificationCollator(self.feature_extractor)

    # Get the model output path
    self.output_path = self.__getOutputPath()
    self.logs_path = self.output_path
    
    # Open the logs file
    self.__openLogs()

    """
    🏗️ Build the trainer
    """
    self.training_args = TrainingArguments(
        output_dir                  = self.output_path,
        save_steps                  = 10000,
        save_total_limit            = 2,
        weight_decay                = 0.01,
        learning_rate               = self.lr,
        per_device_train_batch_size = self.batch_size,
        per_device_eval_batch_size  = self.batch_size,
        num_train_epochs            = self.max_epochs,
        metric_for_best_model       = self.eval_metric,
        logging_dir                 = self.logs_path,
        fp16                        = self.fp16,
        evaluation_strategy         = "epoch",
        overwrite_output_dir        = True,
        load_best_model_at_end      = False,
    )
    
    self.trainer = Trainer(
      self.model,
      self.training_args,
      train_dataset = self.dataset["train"],
      eval_dataset  = self.dataset["test"],
      data_collator = self.collator,
    )
    print("Trainer builded!")

    """
    ⚙️ Train the given model on the dataset
    """
    print("Start Training!")
    self.trainer.train()
    self.trainer.save_model(self.output_path + "/trainer/")
    self.model.save_pretrained(self.output_path + "/model/")
    self.feature_extractor.save_pretrained(self.output_path + "/feature_extractor/")
    print("Model saved at: \033[93m" + self.output_path + "\033[0m")

    # Close the logs file
    self.logs_file.close()

  """
  📜 Open the logs file
  """
  def __openLogs(self):    

    # Open the logs file
    self.logs_file = open(self.logs_path + "/logs.txt", "a")

  """
  📍 Get the path of the output model
  """
  def __getOutputPath(self):

    path = os.path.join(
      self.output_dir,
      self.model_name.upper() + "/" + str(self.max_epochs) + "_" + datetime.today().strftime("%Y-%m-%d-%H-%M-%S")
    )

    # Create the full path if doesn't exist yet
    if not os.path.isdir(path):
        os.makedirs(path)

    return path

  """
  🧪 Evaluate the performances of the system of the test sub-dataset
  """
  def __evaluate(self):
        
    all_preds  = []
    all_target = []

    # For each image
    for image, label in tqdm(self.dataset["test"]):

        # Compute
        inputs  = self.feature_extractor(images=image, return_tensors="pt").to(self.device)
        outputs = self.model(**inputs)

        # Get predictions from the softmax layer
        preds = outputs.logits.softmax(1).argmax(1).tolist()
        all_preds.extend(preds)

        # Get hypothesis
        all_target.append(label)

    return all_preds, all_target

  """
  🧪 Evaluate the performances of the system of the test sub-dataset given a f1-score
  """
  def evaluate_f1_score(self):

    # Get the hypothesis and predictions
    all_target, all_preds = self.__evaluate()

    # Get the labels as a list
    labels = list(self.ids2labels.keys())

    # Compute f-score
    precision, recall, fscore, support = f_score(all_target, all_preds)

    table_f_score = []

    # Add macro scores for each classes
    for i in range(len(labels)):
        table_f_score.append(
            [
                self.ids2labels[labels[i]],
                str(round(precision[i] * 100,2)) + " %",
                str(round(recall[i] * 100,2)) + " %",
                str(round(fscore[i] * 100,2)) + " %",
                support[i],
            ]
        )

    # Add global macro scores
    table_f_score.append(
        [
            "Macro",
            str(round((sum(precision) / len(precision)) * 100, 2)) + " %",
            str(round((sum(recall)    / len(recall))    * 100, 2)) + " %",
            str(round((sum(fscore)    / len(fscore))    * 100, 2)) + " %",
            str(sum(support)),
        ]
    )

    # Print precision, recall, f-score and support for each classes
    f_score_table = tabulate(table_f_score, tablefmt="psql", headers=["Label", "Precision", "Recall", "F-Score", "Support"])
    print(f_score_table)

    # Write logs
    self.__openLogs()
    self.logs_file.write(f_score_table + "\n")
    self.logs_file.close()

    print("Logs saved at: \033[93m" + self.logs_path + "\033[0m")

    return all_target, all_preds

  """
  🧪 Test on a single image
  """
  def testing(self, img,expected):
    image_array = Image.open(img)
    inputs      = self.feature_extractor(images=image_array, return_tensors="pt").to(self.device)
    outputs     = self.model(**inputs)
    preds       = outputs.logits.softmax(1).argmax(1).tolist()[0]
    print(
      "Predicted class: ",
      self.ids2labels[str(preds)],
      "(", str(preds), " - ", self.ids2labels[str(expected)], ") ",
      str(preds == expected)
    )
    return preds