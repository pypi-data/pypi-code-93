import logging

import numpy as np
import scipy.sparse
import tensorflow as tf

from sklearn.model_selection import train_test_split
from typing import (
    Optional,
    Dict,
    Text,
    List,
    Tuple,
    Any,
    Union,
    Generator,
    NamedTuple,
    ValuesView,
    ItemsView,
)
from collections import defaultdict
from convo.utils.tensorflow.constants import BALANCED_VALUE, SEQUENTIAL

log = logging.getLogger(__name__)


# Mapping of attribute name and feature name to a list of numpy arrays representing
# the actual features
# For example:
# "text" -> { "sentence": [
#   "numpy array containing dense features for every training example",
#   "numpy array containing sparse features for every training example"
# ]}
Data = Dict[Text, Dict[Text, List[np.ndarray]]]


class FeatureSign(NamedTuple):
    """Stores the shape and the type (sparse vs dense) of features."""

    is_sparse: bool
    feature_dimension: Optional[int]


class ConvoModelDataSet:
    """Data object used for all ConvoModels.

    It contains all features needed to train the models.
    """

    def __init__(
        self,
        label_key: Optional[Text] = None,
        label_sub_key: Optional[Text] = None,
        data: Optional[Data] = None,
    ) -> None:
        """
        Initializes the ConvoModelDataSet object.

        Args:
            label_key: the key of a label used for balancing, etc.
            label_sub_key: the sub key of a label used for balancing, etc.
            data: the data holding the features
        """

        self.data = data or defaultdict(lambda: defaultdict(list))
        self.label_key = label_key
        self.label_sub_key = label_sub_key
        # should be updated when features are added
        self.num_examples = self.no_of_examples()

    def get(
        self, key: Text, sub_key: Optional[Text] = None
    ) -> Union[Dict[Text, List[np.ndarray]], List[np.ndarray]]:
        """Get the data under the given keys.

        Args:
            key: The key.
            sub_key: The optional sub key.

        Returns:
            The requested data.
        """
        if sub_key is None and key in self.data:
            return self.data[key]

        if sub_key and key in self.data and sub_key in self.data[key]:
            return self.data[key][sub_key]

        return []

    def items(self) -> ItemsView:
        """Return the items of the data attribute.

        Returns:
            The items of data.
        """
        return self.data.items()

    def vals(self) -> ValuesView[Dict[Text, List[np.ndarray]]]:
        """Return the values of the data attribute.

        Returns:
            The values of data.
        """
        return self.data.values()

    def keys(self, key: Optional[Text] = None) -> List[Text]:
        """Return the keys of the data attribute.

        Args:
            key: The optional key.

        Returns:
            The keys of the data.
        """
        if key is None:
            return list(self.data.keys())

        if key in self.data:
            return list(self.data[key].keys())

        return []

    def first_data_exp(self) -> Data:
        """Return the data with just one feature example per key, sub-key.

        Returns:
            The simplified data.
        """
        output_data = {}
        for key, attribute_data in self.data.items():
            output_data[key] = {}
            for sub_key, features in attribute_data.items():
                output_data[key][sub_key] = [feature[:1] for feature in features]
        return output_data

    def feature_exist_check(self, key: Text, sub_key: Optional[Text] = None) -> bool:
        """Check if feature key (and sub-key) is present and features are available.

        Args:
            key: The key.
            sub_key: The optional sub-key.

        Returns:
            True, if no features for the given keys exists, False otherwise.
        """
        if sub_key:
            return (
                key not in self.data
                or not self.data[key]
                or sub_key not in self.data[key]
                or not self.data[key][sub_key]
            )

        return key not in self.data or not self.data[key]

    def empty_check(self) -> bool:
        """Checks if data is set."""

        return not self.data

    def no_of_examples(self, data_set: Optional[Data] = None) -> int:
        """Obtain number of examples in data.

        Args:
            data_set: The data.

        Raises: A ValueError if number of examples differ for different features.

        Returns:
            The number of examples in data.
        """
        if not data_set:
            data_set = self.data

        if not data_set:
            return 0

        example_len = [
            f.shape[0]
            for attribute_data in data_set.values()
            for features in attribute_data.values()
            for f in features
        ]

        if not example_len:
            return 0

        # check if number of examples is the same for all values
        if not all(length == example_len[0] for length in example_len):
            raise ValueError(
                f"Number of examples differs for keys '{data_set.keys()}'. Number of "
                f"examples should be the same for all data."
            )

        return example_len[0]

    def ftr_dimension(self, key: Text, sub_key: Text) -> int:
        """Get the feature dimension of the given key.

        Args:
            key: The key.
            sub_key: The optional sub-key.

        Returns:
            The feature dimension.
        """
        if key not in self.data or sub_key not in self.data[key]:
            return 0

        no_of_features = 0
        for data in self.data[key][sub_key]:
            if data.size > 0:
                no_of_features += data[0].shape[-1]

        return no_of_features

    def adding_new_data(self, data: Data, key_prefix: Optional[Text] = None) -> None:
        """Add incoming data to data.

        Args:
            data: The data to add.
            key_prefix: Optional key prefix to use in front of the key value.
        """
        for key, attribute_data in data.items():
            for sub_key, features in attribute_data.items():
                if key_prefix:
                    self.adding_features(f"{key_prefix}{key}", sub_key, features)
                else:
                    self.adding_features(key, sub_key, features)

    def adding_features(
        self, key: Text, sub_key: Text, features: Optional[List[np.ndarray]]
    ) -> None:
        """Add list of features to data under specified key.

        Should update number of examples.

        Args:
            key: The key
            sub_key: The sub-key
            features: The features to add.
        """
        if features is None:
            return

        for data in features:
            if data.size > 0:
                self.data[key][sub_key].append(data)

        if not self.data[key][sub_key]:
            del self.data[key][sub_key]

        # update number of examples
        self.num_examples = self.no_of_examples()

    def adding_len(
        self, key: Text, sub_key: Text, from_key: Text, from_sub_key: Text
    ) -> None:
        """Adds np.array of lengths of sequences to data under given key.

        Args:
            key: The key to add the lengths to
            sub_key: The sub-key to add the lengths to
            from_key: The key to take the lengths from
            from_sub_key: The sub-key to take the lengths from
        """
        if not self.data.get(from_key) or not self.data.get(from_key, {}).get(
            from_sub_key
        ):
            return

        self.data[key][sub_key] = []

        for data in self.data[from_key][from_sub_key]:
            if data.size > 0:
                len = np.array([x.shape[0] for x in data])
                self.data[key][sub_key].extend([len])
                break

    def split(
        self, number_of_test_examples: int, random_seed: int
    ) -> Tuple["ConvoModelDataSet", "ConvoModelDataSet"]:
        """Create random hold out test set using stratified split.

        Args:
            number_of_test_examples: Number of test examples.
            random_seed: Random seed.

        Returns:
            A tuple of train and test ConvoModelDataSet.
        """

        self.checking_label_key()

        if self.label_key is None or self.label_sub_key is None:
            # randomly split data as no label key is split
            multi_vals = [
                v
                for attribute_data in self.data.values()
                for data in attribute_data.values()
                for v in data
            ]
            solo_vals = [
                []
                for attribute_data in self.data.values()
                for data in attribute_data.values()
                for _ in data
            ]
            layered = None
        else:
            # make sure that examples for each label value are in both split sets
            tag_ids = self.creating_label_ids(
                self.data[self.label_key][self.label_sub_key][0]
            )
            label_counters = dict(zip(*np.unique(tag_ids, return_counts=True, axis=0)))

            self.checking_training_test_sizes(number_of_test_examples, label_counters)

            sum_up = np.array([label_counters[label] for label in tag_ids])
            # we perform stratified train test split,
            # which insures every label is present in the train and test data
            # this operation can be performed only for labels
            # that contain several data points
            multi_vals = [
                f[sum_up > 1]
                for attribute_data in self.data.values()
                for features in attribute_data.values()
                for f in features
            ]
            # collect data points that are unique for their label
            solo_vals = [
                f[sum_up == 1]
                for attribute_data in self.data.values()
                for features in attribute_data.values()
                for f in features
            ]

            layered = tag_ids[sum_up > 1]

        output_vals = train_test_split(
            *multi_vals,
            test_size=number_of_test_examples,
            random_state=random_seed,
            stratify=layered,
        )

        return self.convering_training_test_split(output_vals, solo_vals)

    def get_sign(self) -> Dict[Text, Dict[Text, List[FeatureSign]]]:
        """Get signature of ConvoModelDataSet.

        Signature stores the shape and whether features are sparse or not for every key.

        Returns:
            A dictionary of key and sub-key to a list of feature signatures
            (same structure as the data attribute).
        """

        return {
            key: {
                sub_key: [
                    FeatureSign(
                        True if isinstance(f[0], scipy.sparse.spmatrix) else False,
                        f[0].shape[-1] if f[0].shape else None,
                    )
                    for f in features
                ]
                for sub_key, features in attribute_data.items()
            }
            for key, attribute_data in self.data.items()
        }

    def as_tf_data_set(
        self, batch_size: int, batch_strategy: Text = SEQUENTIAL, shuffle: bool = False
    ) -> tf.data.Dataset:
        """Create tf dataset.

        Args:
            batch_size: The batch size to use.
            batch_strategy: The batch strategy to use.
            shuffle: Boolean indicating whether the data should be shuffled or not.

        Returns:
            The tf.data.Dataset.
        """

        structures, variety = self.fetch_shape_types()

        return tf.data.Dataset.from_generator(
            lambda batch_size_: self._generate_batch(batch_size_, batch_strategy, shuffle),
            output_types=variety,
            output_shapes=structures,
            args=([batch_size]),
        )

    def preparing_batch_data(
        self,
        data: Optional[Data] = None,
        start: Optional[int] = None,
        end: Optional[int] = None,
        tuple_sizes: Optional[Dict[Text, int]] = None,
    ) -> Tuple[Optional[np.ndarray]]:
        """Slices model data into batch using given start and end value.

        Args:
            data: The data to prepare.
            start: The start index of the batch
            end: The end index of the batch
            tuple_sizes: In case the feature is not present we propagate the batch with
              None. Tuple sizes contains the number of how many None values to add for
              what kind of feature.

        Returns:
            The features of the batch.
        """

        if not data:
            data = self.data

        batch_data_set = []

        for key, attribute_data in data.items():
            for sub_key, f_data in attribute_data.items():
                # add None for not present values during processing
                if not f_data:
                    if tuple_sizes:
                        batch_data_set += [None] * tuple_sizes[key]
                    else:
                        batch_data_set.append(None)
                    continue

                for v in f_data:
                    if start is not None and end is not None:
                        data = v[start:end]
                    elif start is not None:
                        data = v[start:]
                    elif end is not None:
                        data = v[:end]
                    else:
                        data = v[:]

                    if isinstance(data[0], scipy.sparse.spmatrix):
                        batch_data_set.extend(self.scipy_matrix_to_vals(data))
                    else:
                        batch_data_set.append(self.padding_dense_data(data))

        # len of batch_data is equal to the number of keys in model data
        return tuple(batch_data_set)

    def fetch_shape_types(self) -> Tuple:
        """Extract shapes and types from model data.

        Returns:
            A tuple of shapes and a tuple of types.
        """

        variety = []
        structures = []

        def shape_appended(features: np.ndarray) -> None:
            if isinstance(features[0], scipy.sparse.spmatrix):
                # scipy matrix is converted into indices, data, shape
                structures.append((None, features[0].ndim + 1))
                structures.append((None,))
                structures.append((features[0].ndim + 1))
            elif features[0].ndim == 0:
                structures.append((None,))
            elif features[0].ndim == 1:
                structures.append((None, features[0].shape[-1]))
            else:
                structures.append((None, None, features[0].shape[-1]))

        def add_type(features: np.ndarray) -> None:
            if isinstance(features[0], scipy.sparse.spmatrix):
                # scipy matrix is converted into indices, data, shape
                variety.append(tf.int64)
                variety.append(tf.float32)
                variety.append(tf.int64)
            else:
                variety.append(tf.float32)

        for attribute_data in self.data.values():
            for features in attribute_data.values():
                for f in features:
                    shape_appended(f)
                    add_type(f)

        return tuple(structures), tuple(variety)

    def shuffles_data_set(self, data: Data) -> Data:
        """Shuffle model data.

        Args:
            data: The data to shuffle

        Returns:
            The shuffled data.
        """

        ids = np.random.permutation(self.num_examples)
        return self.data_by_ids(data, ids)

    def data_balanced(self, data: Data, batch_size: int, shuffle: bool) -> Data:
        """Mix model data to account for class imbalance.

        This batching strategy puts rare classes approximately in every others batch,
        by repeating them. Mimics stratified batching, but also takes into account
        that more populated classes should appear more often.

        Args:
            data: The data.
            batch_size: The batch size.
            shuffle: Boolean indicating whether to shuffle the data or not.

        Returns:
            The balanced data.
        """
        self.checking_label_key()

        # skip balancing if labels are token based
        if (
            self.label_key is None
            or self.label_sub_key is None
            or data[self.label_key][self.label_sub_key][0][0].size > 1
        ):
            return data

        tag_ids = self.creating_label_ids(data[self.label_key][self.label_sub_key][0])

        dintinct_label_ids, label_ids_count = np.unique(
            tag_ids, return_counts=True, axis=0
        )
        label_ids_number = len(dintinct_label_ids)

        # group data points by their label
        # need to call every time, so that the data is shuffled inside each class
        data_acc_to_label = self.splitting_by_label_ids(data, tag_ids, dintinct_label_ids)

        # running index inside each data grouped by labels
        data_index = [0] * label_ids_number
        # number of cycles each label was passed
        number_of_data_cycles = [0] * label_ids_number
        # if a label was skipped in current batch
        ignored = [False] * label_ids_number

        new_data_set = defaultdict(lambda: defaultdict(list))

        while min(number_of_data_cycles) == 0:
            if shuffle:
                indexes_of_labels = np.random.permutation(label_ids_number)
            else:
                indexes_of_labels = range(label_ids_number)

            for index in indexes_of_labels:
                if number_of_data_cycles[index] > 0 and not ignored[index]:
                    ignored[index] = True
                    continue

                ignored[index] = False

                batch_size_of_index = (
                    int(label_ids_count[index] / self.num_examples * batch_size) + 1
                )

                for key, attribute_data in data_acc_to_label[index].items():
                    for sub_key, features in attribute_data.items():
                        for i, f in enumerate(features):
                            if len(new_data_set[key][sub_key]) < i + 1:
                                new_data_set[key][sub_key].append([])
                            new_data_set[key][sub_key][i].append(
                                f[data_index[index] : data_index[index] + batch_size_of_index]
                            )

                data_index[index] += batch_size_of_index
                if data_index[index] >= label_ids_count[index]:
                    number_of_data_cycles[index] += 1
                    data_index[index] = 0

                if min(number_of_data_cycles) > 0:
                    break

        final_data_set = defaultdict(lambda: defaultdict(list))
        for key, attribute_data in new_data_set.items():
            for sub_key, features in attribute_data.items():
                for f in features:
                    final_data_set[key][sub_key].append(np.concatenate(np.array(f)))

        return final_data_set

    def _generate_batch(
        self, batch_size: int, batch_strategy: Text = SEQUENTIAL, shuffle: bool = False
    ) -> Generator[Tuple[Optional[np.ndarray]], None, None]:
        """Generate batches.

        Args:
            batch_size: The batch size
            batch_strategy: The batch strategy.
            shuffle: Boolean indicating whether to shuffle the data or not.

        Returns:
            A generator over the batches.
        """

        data_set = self.data
        number_examples = self.num_examples

        if shuffle:
            data_set = self.shuffles_data_set(data_set)

        if batch_strategy == BALANCED_VALUE:
            data_set = self.data_balanced(data_set, batch_size, shuffle)
            # after balancing, number of examples increased
            number_examples = self.no_of_examples(data_set)

        number_examples = number_examples // batch_size + int(number_examples % batch_size > 0)

        for batch_num in range(number_examples):
            begin = batch_num * batch_size
            last = begin + batch_size

            yield self.preparing_batch_data(data_set, begin, last)

    def checking_training_test_sizes(
        self, number_of_test_examples: int, label_counts: Dict[Any, int]
    ) -> None:
        """Check whether the test data set is too large or too small.

        Args:
            number_of_test_examples: number of test examples
            label_counts: number of labels

        Raises:
            A ValueError if the number of examples does not fit.
        """

        if number_of_test_examples >= self.num_examples - len(label_counts):
            raise ValueError(
                f"Test set of {number_of_test_examples} is too large. Remaining "
                f"train set should be at least equal to number of classes "
                f"{len(label_counts)}."
            )
        if number_of_test_examples < len(label_counts):
            raise ValueError(
                f"Test set of {number_of_test_examples} is too small. It should "
                f"be at least equal to number of classes {label_counts}."
            )

    @staticmethod
    def data_by_ids(data: Optional[Data], ids: np.ndarray) -> Data:
        """Filter model data by ids.

        Args:
            data: The data to filter
            ids: The ids

        Returns:
            The filtered data
        """

        new_data_set = defaultdict(lambda: defaultdict(list))

        if data is None:
            return new_data_set

        for key, attribute_data in data.items():
            for sub_key, features in attribute_data.items():
                for f in features:
                    new_data_set[key][sub_key].append(f[ids])
        return new_data_set

    def splitting_by_label_ids(
        self, data: Optional[Data], label_ids: np.ndarray, unique_label_ids: np.ndarray
    ) -> List["ConvoModelDataSet"]:
        """Reorganize model data into a list of model data with the same labels.

        Args:
            data: The data
            label_ids: The label ids
            unique_label_ids: The unique label ids

        Returns:
            Reorganized ConvoModelDataSet
        """

        labelled_data = []
        for label_id in unique_label_ids:
            match_ids = label_ids == label_id
            labelled_data.append(
                ConvoModelDataSet(
                    self.label_key,
                    self.label_sub_key,
                    self.data_by_ids(data, match_ids),
                )
            )
        return labelled_data

    def checking_label_key(self) -> None:
        """Check if the label key exists.

        Raises:
            ValueError if the label key and sub-key is not in data.
        """
        if (
            self.label_key is not None
            and self.label_sub_key is not None
            and (
                self.label_key not in self.data
                or self.label_sub_key not in self.data[self.label_key]
                or len(self.data[self.label_key][self.label_sub_key]) > 1
            )
        ):
            raise ValueError(
                f"Key '{self.label_key}.{self.label_sub_key}' not in ConvoModelDataSet."
            )

    def convering_training_test_split(
        self, output_values: List[Any], solo_values: List[Any]
    ) -> Tuple["ConvoModelDataSet", "ConvoModelDataSet"]:
        """Converts the output of sklearn's train_test_split into model data.

        Args:
            output_values: output values of sklearn's train_test_split
            solo_values: list of solo values

        Returns:
            The test and train ConvoModelDataSet
        """

        data_training = defaultdict(lambda: defaultdict(list))
        data_value = defaultdict(lambda: defaultdict(list))

        # output_values = x_train, x_val, y_train, y_val, z_train, z_val, etc.
        # order is kept, e.g. same order as model data keys

        # train datasets have an even index
        idx = 0
        for key, attribute_data in self.data.items():
            for sub_key, features in attribute_data.items():
                for _ in features:
                    data_training[key][sub_key].append(
                        self.combining_ftrs(
                            output_values[idx * 2], solo_values[idx]
                        )
                    )
                    idx += 1

        # val datasets have an odd index
        idx = 0
        for key, attribute_data in self.data.items():
            for sub_key, features in attribute_data.items():
                for _ in features:
                    data_value[key][sub_key].append(output_values[(idx * 2) + 1])
                    idx += 1

        return (
            ConvoModelDataSet(self.label_key, self.label_sub_key, data_training),
            ConvoModelDataSet(self.label_key, self.label_sub_key, data_value),
        )

    @staticmethod
    def combining_ftrs(
        feature_1: Union[np.ndarray, scipy.sparse.spmatrix],
        feature_2: Union[np.ndarray, scipy.sparse.spmatrix],
    ) -> Union[np.ndarray, scipy.sparse.spmatrix]:
        """Concatenate features.

        Args:
            feature_1: Features to concatenate.
            feature_2: Features to concatenate.

        Returns:
            The combined features.
        """

        if isinstance(feature_1, scipy.sparse.spmatrix) and isinstance(
            feature_2, scipy.sparse.spmatrix
        ):
            if feature_2.shape[0] == 0:
                return feature_1
            if feature_1.shape[0] == 0:
                return feature_2
            return scipy.sparse.vstack([feature_1, feature_2])

        return np.concatenate([feature_1, feature_2])

    @staticmethod
    def creating_label_ids(label_ids: np.ndarray) -> np.ndarray:
        """Convert various size label_ids into single dim array.

        For multi-label y, map each distinct row to a string representation
        using join because str(row) uses an ellipsis if len(row) > 1000.
        Idea taken from sklearn's stratify split.

        Args:
            label_ids: The label ids.

        Returns:
            The single dim label array.
        """

        if label_ids.ndim == 1:
            return label_ids

        if label_ids.ndim == 2 and label_ids.shape[-1] == 1:
            return label_ids[:, 0]

        if label_ids.ndim == 2:
            return np.array([" ".join(row.astype("str")) for row in label_ids])

        if label_ids.ndim == 3 and label_ids.shape[-1] == 1:
            return np.array([" ".join(row.astype("str")) for row in label_ids[:, :, 0]])

        raise ValueError("Unsupported label_ids dimensions")

    @staticmethod
    def padding_dense_data(array_of_dense: np.ndarray) -> np.ndarray:
        """Pad data of different lengths.

        Sequential data is padded with zeros. Zeros are added to the end of data.

        Args:
            array_of_dense: The array to pad.

        Returns:
            The padded array.
        """

        if array_of_dense[0].ndim < 2:
            # data doesn't contain a sequence
            return array_of_dense.astype(np.float32)

        data_set_size = len(array_of_dense)
        max_sequence_length = max([x.shape[0] for x in array_of_dense])

        padded_data = np.zeros(
            [data_set_size, max_sequence_length, array_of_dense[0].shape[-1]],
            dtype=array_of_dense[0].dtype,
        )
        for i in range(data_set_size):
            padded_data[i, : array_of_dense[i].shape[0], :] = array_of_dense[i]

        return padded_data.astype(np.float32)

    @staticmethod
    def scipy_matrix_to_vals(sparse_arr: np.ndarray) -> List[np.ndarray]:
        """Convert a scipy matrix into indices, data, and shape.

        Args:
            sparse_arr: The sparse data array.

        Returns:
            A list of dense numpy arrays representing the sparse data.
        """

        # we need to make sure that the matrices are coo_matrices otherwise the
        # transformation does not work (e.g. you cannot access x.row, x.col)
        if not isinstance(sparse_arr[0], scipy.sparse.coo_matrix):
            sparse_arr = [x.tocoo() for x in sparse_arr]

        max_seq_len = max([x.shape[0] for x in sparse_arr])

        # get the indices of values
        indexes = np.hstack(
            [
                np.vstack([i * np.ones_like(x.row), x.row, x.col])
                for i, x in enumerate(sparse_arr)
            ]
        ).T

        data_set = np.hstack([x.data for x in sparse_arr])

        no_of_ftrs = sparse_arr[0].shape[-1]
        structures = np.array((len(sparse_arr), max_seq_len, no_of_ftrs))

        return [
            indexes.astype(np.int64),
            data_set.astype(np.float32),
            structures.astype(np.int64),
        ]
