from __future__ import annotations  # noqa: F407

from typing import Any, Callable, Dict, Iterator, List, Optional, Tuple

import tensorflow as tf

Transform = Tuple[str, Dict[str, Any]]


class SarusTensorflowDataset:
    """A class allowing to manipulate a Sarus dataset as a Tensorflow dataset.

    The `SarusTensorflowDataset` class allows to manipulate a Sarus Dataset
    as if it were a `tensorflow.data.Dataset` instance.

    Similarly to a Sarus Dataset, a `SarusTensorflowDataset` uses synthetic data
    locally, which allows interactions with the data while preserving privacy.
    This allows data practitionners to design their ML models, processing
    pipelines locally as if they were working with a tensorflow dataset.

    Under the hood, the class memorizes the transformations that will be applied
    to the private dataset when training remotely with differential privacy.
    """

    def __init__(
        self,
        dataset,
    ) -> None:
        self.dataset = dataset

    def map(
        self,
        map_func: Callable,
        num_parallel_calls: Optional[int] = None,
        deterministic: Optional[bool] = None,
    ) -> SarusTensorflowDataset:
        """Map `map_func` across the elements of this dataset.

        This transformation applies `map_func` to each element of this
        dataset, and returns a new dataset containing the transformed
        elements, in the same order as they appeared in the input. `map_func`
        can be used to change both the values and the structure of a dataset's
        elements. Supported structure constructs are documented
        [here](https://www.tensorflow.org/guide/data#dataset_structure).
        For example, `map` can be used for adding 1 to each element, or
        projecting a subset of element components.

        >>> sarus_tf_dataset = sarus_dataset.as_tensorflow()  # ==> [ 1, 2, 3, 4, 5 ]
        >>> sarus_tf_dataset = sarus_tf_dataset.map(lambda x: x + 1)
        >>> list(sarus_tf_dataset.as_numpy_iterator())
        [2, 3, 4, 5, 6]

        The input signature of `map_func` is determined by the structure of each
        element in this dataset.

        >>> sarus_tf_dataset = sarus_dataset.as_tensorflow()  # ==> range(5)
        >>> # `map_func` takes a single argument of type `tf.Tensor` with the same
        >>> # shape and dtype.
        >>> result = dataset.map(lambda x: x + 1)

        >>> # Each element is a tuple containing two `tf.Tensor` objects.
        >>> # elements = [(1, "foo"), (2, "bar"), (3, "baz")]
        >>> # `map_func` takes two arguments of type `tf.Tensor`. This function
        >>> # projects out just the first component.
        >>> sarus_tf_dataset = sarus_tf_dataset.map(lambda x_int, y_str: x_int)
        >>> list(sarus_tf_dataset.as_numpy_iterator())
        [1, 2, 3]

        >>> # Each element is a dictionary mapping strings to `tf.Tensor` objects.
        >>> elements =  ([{"a": 1, "b": "foo"},
        ...               {"a": 2, "b": "bar"},
        ...               {"a": 3, "b": "baz"}])
        >>> # `map_func` takes a single argument of type `dict` with the same keys
        >>> # as the elements.
        >>> sarus_tf_dataset = sarus_tf_dataset.map(lambda d: str(d["a"]) + d["b"])


        For more information on `map` please refer to the
        [Tensorflow documentation](https://www.tensorflow.org/api_docs/python/tf/data/Dataset#map).

        Args:

        map_func:
            A function mapping a dataset element to another dataset element.

        num_parallel_calls:
            (Optional.) A `tf.int64` scalar `tf.Tensor`,
            representing the number elements to process asynchronously in parallel.
            If not specified, elements will be processed sequentially. If the value
            `tf.data.AUTOTUNE` is used, then the number of parallel
            calls is set dynamically based on available CPU.

        deterministic:
            (Optional.) When `num_parallel_calls` is specified, if this
            boolean is specified (`True` or `False`), it controls the order in which
            the transformation produces elements. If set to `False`, the
            transformation is allowed to yield elements out of order to trade
            determinism for performance. If not specified, the
            `tf.data.Options.experimental_deterministic` option
            (`True` by default) controls the behavior.

        Returns:
            Dataset: A `Dataset`.
        """
        transform = (
            "map",
            {
                "map_func": map_func,
                "num_parallel_calls": num_parallel_calls,
                "deterministic": deterministic,
            },
        )
        new_dataset = self.dataset._add_transform(transform)
        return SarusTensorflowDataset(new_dataset)

    def unbatch(self) -> SarusTensorflowDataset:
        """Split elements of a dataset into multiple elements.

        For example, if elements of the dataset are shaped `[B, a0, a1, ...]`,
        where `B` may vary for each input element, then for each element in the
        dataset, the unbatched dataset will contain `B` consecutive elements
        of shape `[a0, a1, ...]`.

        >>> sarus_tf_dataset = sarus_dataset.as_tensorflow()
        >>> print(next(iter(sarus_tf_dataset)).take(3))
        [ [1, 2, 3], [1, 2], [1, 2, 3, 4] ]
        >>> sarus_tf_dataset = sarus_tf_dataset.unbatch()
        >>> print(next(iter(sarus_tf_dataset)).take(9))
        [1, 2, 3, 1, 2, 1, 2, 3, 4]

        Note: `unbatch` requires a data copy to slice up the batched tensor into
        smaller, unbatched tensors. When optimizing performance, try to avoid
        unnecessary usage of `unbatch`.

        Returns:
            A `SarusTensorflowDataset`.
        """
        transform: Transform = ("unbatch", {})
        new_dataset = self.dataset._add_transform(transform)
        return SarusTensorflowDataset(new_dataset)

    def batch(
        self,
        batch_size: int,
        drop_remainder: bool = True,
        num_parallel_calls: Optional[int] = None,
        deterministic: Optional[bool] = None,
    ) -> SarusTensorflowDataset:
        """Combine consecutive elements of this dataset into batches.

        >>> sarus_tf_dataset = sarus_dataset.as_tensorflow()
        >>> sarus_tf_dataset = sarus_tf_dataset.batch(3)

        The components of the resulting element will have an additional outer
        dimension, which will be `batch_size`. Currently, only a value of True
        is accepted. If you set the value to False, it will be reset to True.

        Args:

        batch_size:
            A `tf.int64` scalar `tf.Tensor`, representing the number of
            consecutive elements of this dataset to combine in a single batch.

        drop_remainder:
            (Optional.) A `tf.bool` scalar `tf.Tensor`, representing whether the
            last batch should be dropped in the case it has fewer than
            `batch_size` elements; Currently, only a value of True is accepted.
            If you set the value to False, it will be reset to True.

        num_parallel_calls:
            (Optional.) A `tf.int64` scalar `tf.Tensor`, representing the number
            of batches to compute asynchronously in parallel. If not specified,
            batches will be computed sequentially. If the value
            `tf.data.AUTOTUNE` is used, then the number of parallel calls is set
            dynamically based on available resources.

        deterministic:
            (Optional.) When `num_parallel_calls` is specified, if this boolean
            is specified (`True` or `False`), it controls the order in which the
            transformation produces elements. If set to `False`, the
            transformation is allowed to yield elements out of order to trade
            determinism for performance. If not specified, the
            `tf.data.Options.experimental_deterministic` option (`True` by
            default) controls the behavior.

        Returns:
            SarusTensorflowDataset: A `SarusTensorflowDataset`.
        """
        # TODO `drop_remainder` = False not supported yet
        if drop_remainder is False:
            print(
                "Changing `drop_remainder` to True as setting it to False "
                "is not supported yet."
            )
            drop_remainder = True

        transform = (
            "batch",
            {
                "batch_size": batch_size,
                "drop_remainder": drop_remainder,
                "num_parallel_calls": num_parallel_calls,
                "deterministic": deterministic,
            },
        )
        new_dataset = self.dataset._add_transform(transform)
        return SarusTensorflowDataset(new_dataset)

    def filter(self, predicate: Callable) -> SarusTensorflowDataset:
        """Filter this dataset according to `predicate`.

        >>> sarus_tf_dataset = sarus_dataset.as_tensorflow() # ==> [1, 2, 3]
        >>> sarus_tf_dataset = sarus_tf_dataset.filter(lambda x: x < 3)
        >>> list(sarus_tf_dataset.as_numpy_iterator())
        [1, 2]

        >>> # `tf.math.equal(x, y)` is required for equality comparison
        >>> def filter_fn(x):
        ...   return tf.math.equal(x, 1)
        >>> sarus_tf_dataset = sarus_tf_dataset.filter(filter_fn)
        >>> list(sarus_tf_dataset.as_numpy_iterator())
        [1]

        Args:
        predicate:
            A function mapping a dataset element to a boolean.

        Returns:
        Dataset:
            The `SarusTensorflowDataset` containing the elements of this dataset
            for which `predicate` is `True`.
        """
        transform = ("filter", {"predicate": predicate})
        new_dataset = self.dataset._add_transform(transform)
        return SarusTensorflowDataset(new_dataset)

    def _tensorflow(self) -> tf.data.Dataset:
        ds = self.dataset._synthetic_as_tf_dataset(
            batch_size=1,
            # TODO rows_number=int(self.dataset.marginals["rows"])
        )
        return _apply_transforms(ds, self.dataset.transforms)

    def __iter__(self) -> Iterator:
        return self._tensorflow().__iter__()


def _apply_transforms(
    ds: tf.data.Dataset, transforms: List[Transform]
) -> tf.data.Dataset:
    for name, params in transforms:
        if name == "map":
            ds = ds.map(**params)
        elif name == "unbatch":
            ds = ds.unbatch(**params)
        elif name == "batch":
            ds = ds.batch(**params)
        elif name == "filter":
            ds = ds.filter(**params)
        elif name == "split":
            size = params["end"] - params["start"]
            ds = ds.skip(params["start"]).take(size)
    return ds
