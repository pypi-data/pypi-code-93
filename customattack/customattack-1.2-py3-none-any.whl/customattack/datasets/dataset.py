from collections import OrderedDict
import random

import torch


class Dataset(torch.utils.data.Dataset):
    def __init__(
        self,
        dataset,
        input_columns=["text"],
        label_map=None,
        label_names=None,
        output_scale_factor=None,
        shuffle=False,
    ):
        self._dataset = dataset
        self.input_columns = input_columns
        self.label_map = label_map
        self.label_names = label_names
        if label_map:
            # If labels are remapped, the label names have to be remapped as well.
            self.label_names = [
                self.label_names[self.label_map[i]] for i in self.label_map
            ]
        self.shuffled = shuffle
        self.output_scale_factor = output_scale_factor

        if shuffle:
            random.shuffle(self._dataset)

    def _format_as_dict(self, example):
        output = example[1]
        if self.label_map:
            output = self.label_map[output]
        if self.output_scale_factor:
            output = output / self.output_scale_factor

        if isinstance(example[0], str):
            if len(self.input_columns) != 1:
                raise ValueError(
                    "Mismatch between the number of columns in `input_columns` and number of columns of actual input."
                )
            input_dict = OrderedDict([(self.input_columns[0], example[0])])
        else:
            if len(self.input_columns) != len(example[0]):
                raise ValueError(
                    "Mismatch between the number of columns in `input_columns` and number of columns of actual input."
                )
            input_dict = OrderedDict(
                [(c, example[0][i]) for i, c in enumerate(self.input_columns)]
            )
        return input_dict, output

    def shuffle(self):
        random.shuffle(self._dataset)
        self.shuffled = True

    def filter_by_labels_(self, labels_to_keep):
        """Filter items by their labels for classification datasets. Performs
        in-place filtering.

        Args:
            labels_to_keep (:obj:`Union[Set, Tuple, List, Iterable]`):
                Set, tuple, list, or iterable of integers representing labels.
        """
        if not isinstance(labels_to_keep, set):
            labels_to_keep = set(labels_to_keep)
        self._dataset = filter(lambda x: x[1] in labels_to_keep, self._dataset)

    def __getitem__(self, i):
        """Return i-th sample."""
        if isinstance(i, int):
            return self._format_as_dict(self._dataset[i])
        else:
            # `idx` could be a slice or an integer. if it's a slice,
            # return the formatted version of the proper slice of the list
            return [self._format_as_dict(ex) for ex in self._dataset[i]]

    def __len__(self):
        """Returns the size of dataset."""
        return len(self._dataset)
