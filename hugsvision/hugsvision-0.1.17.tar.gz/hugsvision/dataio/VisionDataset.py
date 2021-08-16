# -*- coding: utf-8 -*-

import math
import random
from collections import Counter

from PIL import Image, ImageEnhance

import torch
from torchvision.datasets import ImageFolder
from torch.utils.data.Dataset import Dataset
from datasets import DatasetDict

from tabulate import tabulate

class VisionDataset:
    
    @staticmethod
    def datasetFromDirectory(path: str, test_ratio = 0.15, balanced = True, augmentation = False):
        """
        Load data from one directory
        ↪ Directory
            ↪ sars_cov_2
            ↪ normal
            ↪ pneumonia
        """

        return VisionDataset.__splitDatasets(
            ImageFolder(path),
            test_ratio,
            balanced,
            augmentation,
        )
    
    @staticmethod
    def datasetFromDirectories(train: str, test: str, balanced = True):
        """
        Args:
            train (:obj:`str`): Path to the training dataset folder
            test  (:obj:`str`): Path to the test dataset folder
        Returns:
            :class:`DatasetDict`: The dataset containing Train and Test
        Example:
            ↪ Train/
                ↪ sars_cov_2/
                ↪ normal/
                ↪ pneumonia/
            ↪ Test/
                ↪ sars_cov_2/
                ↪ normal/
                ↪ pneumonia/
        Information:
            We build the dataset accordingly to the directory tree.
            So, each sub-directories will be accounted like a class.
        """

        return DatasetDict({
            "train": VisionDataset.__balance(
                ImageFolder(train),
                balanced
            ),
            "test": ImageFolder(test),
        })

    @staticmethod
    def getConfig(dataset:torch.utils.data.Dataset):

        labels2ids = {}
        ids2labels = {}

        for i, class_name in enumerate(dataset.classes):
            labels2ids[class_name] = str(i)
            ids2labels[str(i)] = class_name

        return labels2ids, ids2labels

    """
    🧬 Apply data augmentation on the input image
    Source: https://medium.com/lunit/photometric-data-augmentation-in-projection-radiography-bed3ae9f55c3
    """
    @staticmethod
    def __augmentation(image, beta=0.33):

        # Random augmentation in X % of cases
        if random.randint(0,100) < int(beta*100):
        
            # Random Contrast
            im3 = ImageEnhance.Contrast(image)
            im3.enhance(random.uniform(0.5, 1.0)).show()
        
            # Random Noise
            # Not implemented yet!

        return image

    """
    ⚖️ Balance the dataset according to the less represented class
    """
    @staticmethod
    def __balance(train_ds, balanced):
        
        # If balanced isn't enabled
        if balanced == False:
            return train_ds

        ct_train = Counter([label for _, label in train_ds])
        train_classes = [ct_train[a] for a in sorted(ct_train)]

        # Get the less represented label in train
        less_represented_train = min(train_classes)

        labels = {}

        # For each image
        for img, label in train_ds:

            # Create the label array if isn't
            if label not in labels:
                labels[label] = []

            # Add the image to the array
            labels[label].append(img)

        # New dataset
        balanced_ds = []

        # For each label
        for label in labels:

            # Get images
            imgs = labels[label]

            # For each image
            for img in imgs[0:less_represented_train]:

                # Create a tuple: image and label 
                t = (img, label)

                # Add it
                balanced_ds.append(t)

        print("The less represented label in train as " + str(less_represented_train) + " occurrences")
        print("Size of train after balancing is " + str(len(balanced_ds)))

        return balanced_ds

    """
    ✂️ Split the dataset into sub-datasets
    """
    @staticmethod
    def __splitDatasets(dataset: torch.utils.data.Dataset, test_ratio = 0.15, balanced = True, augmentation = False):

        print("Split Datasets...")

        label2id, id2label = VisionDataset.getConfig(dataset)

        # Train Ratio
        train_ratio = 1 - test_ratio
        
        # Generate index from 0 to N where N is the len of the dataset
        indices = torch.randperm(len(dataset)).tolist()

        # Index of the validation corpora
        elements_test_dev = math.floor(len(indices) * .15)

        # Get end indexes
        train_index = int(len(dataset) * train_ratio)

        # TRAIN
        train_ds = torch.utils.data.Subset(dataset, indices[0:train_index])
        ct_train = Counter([label for _, label in train_ds])
        train_classes = [ct_train[a] for a in sorted(ct_train)]
        
        # If balanced is enabled 
        train_ds = VisionDataset.__balance(train_ds, balanced)
        
        # Compute again the stats
        ct_train = Counter([label for _, label in train_ds])
        train_classes = [ct_train[a] for a in sorted(ct_train)]

        # If data augmentation is enabled
        if augmentation == True:

            new_ds = []

            # For each annotated image
            for img, label in train_ds:

                # Augment it
                new_ds.append((VisionDataset.__augmentation(img), label))
            
            # Replace by the augmented data
            train_ds = new_ds

        # TEST
        test_ds = torch.utils.data.Subset(dataset, indices[train_index:])
        ct_test = Counter([label for _, label in test_ds])
        test_classes = [ct_test[a] for a in sorted(ct_test)]

        # Make a table with all the information about the repartition of the dataset
        table_repartition = [
            ["Train"] + train_classes + [str(len(train_ds))],
            ["Test"] + test_classes + [str(len(test_ds))],
        ]
        repartitions_table = tabulate(table_repartition, ["Dataset"] + list(id2label.values()) + ["Total"], tablefmt="pretty")
        print(repartitions_table)

        return DatasetDict({
            "train": train_ds,
            "test": test_ds,
        })
