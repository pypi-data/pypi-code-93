from typing import Any, Callable, Dict, List, Optional, Tuple, Union

import numpy as np
from sarus.tensorflow import SarusTensorflowDataset

import tensorflow as tf

Transform = Tuple[str, Dict[str, Any]]
Data = Any


class Model(tf.keras.Model):
    """A class similar to a keras Model and allowing private remote training.

    The sarus.keras.Model class is a wrapper around the
    `tensorflow.keras.Model` class. This class differs from its parent only on
    the `fit` method. The `fit` method accepts a `target_epsilon`.

        - If the specified `target_epsilon` is equal to 0 (default value), then the `Model` class launches a standard keras training on the synthetic data.
        - If the specified `target_epsilon` is strictly greater than 0, then the`Model` class calls the API to launch a remote private training.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super(Model, self).__init__(self, *args, **kwargs)

    def predict(
        self,
        x: Data,
        batch_size: Optional[int] = None,
        verbose: int = 0,
        steps: Optional[int] = None,
        callbacks: Optional[List[tf.keras.callbacks.Callback]] = None,
        max_queue_size: int = 10,
        workers: int = 1,
        use_multiprocessing: bool = False,
    ) -> np.ndarray:
        """Generate output predictions for the input samples.

        Computation is done in batches. This method is designed for performance
        in large scale inputs. For small amount of inputs that fit in one batch,
        directly using `__call__` is recommended for faster execution, e.g.,
        `model(x)`, or `model(x, training=False)` if you have layers such as
        `tf.keras.layers.BatchNormalization` that behaves differently during
        inference. Also, note the fact that test loss is not affected by
        regularization layers like noise and dropout.

        Args:

        x: Input samples.
            It could be:

            - A Numpy array (or array-like), or a list of arrays
                (in case the model has multiple inputs).
            - A TensorFlow tensor, or a list of tensors
                (in case the model has multiple inputs).
            - A `tf.data` dataset.
                Should return a tuple
                of either `(inputs, targets)`
            - A `SarusTensorflowDataset` dataset.
                Should return a tuple
                of either `(inputs, targets)`
            - A generator or `keras.utils.Sequence` instance.
                returning `(inputs, targets)`

            A more detailed description of unpacking behavior for iterator types
            (Dataset, generator, Sequence) is given in the `Unpacking behavior
            for iterator-like inputs` section of `Model.fit`.

        batch_size (int, optional):
            Number of samples per batch.
            If unspecified, `batch_size` will default to 32.
            Do not specify the `batch_size` if your data is in the
            form of dataset, generators, or `keras.utils.Sequence` instances
            (since they generate batches).

        verbose (int):
            Verbosity mode, 0 or 1.

        steps (int):
            Total number of steps (batches of samples)
            before declaring the prediction round finished.
            Ignored with the default value of `None`. If x is a `tf.data`
            dataset and `steps` is None, `predict` will
            run until the input dataset is exhausted.

        callbacks: List of `keras.callbacks.Callback` instances.
            List of callbacks to apply during prediction.
            See [callbacks](/api_docs/python/tf/keras/callbacks).

        max_queue_size (int):
            Used for generator or `keras.utils.Sequence`
            input only. Maximum size for the generator queue.
            If unspecified, `max_queue_size` will default to 10.

        workers (int):
            Used for generator or `keras.utils.Sequence` input
            only. Maximum number of processes to spin up when using
            process-based threading. If unspecified, `workers` will default
            to 1.

        use_multiprocessing (bool):
            Used for generator or
            `keras.utils.Sequence` input only. If `True`, use process-based
            threading. If unspecified, `use_multiprocessing` will default to
            `False`. Note that because this implementation relies on
            multiprocessing, you should not pass non-picklable arguments to
            the generator as they can't be passed easily to children
            processes.

        See the discussion of `Unpacking behavior for iterator-like inputs` for
        `Model.fit`. Note that Model.predict uses the same interpretation rules
        as`Model.fit` and `Model.evaluate`, so inputs must be unambiguous for
        allthree methods.
        `Model.predict` is not yet supported with
        `tf.distribute.experimental.ParameterServerStrategy`.

        Returns:
            Numpy array(s) of predictions.

        Raises:
            RuntimeError:
                If `model.predict` is wrapped in `tf.function`.

            ValueError:
                In case of mismatch between the provided
                input data and the model's expectations,
                or in case a stateful model receives a number of samples
                that is not a multiple of the batch size.
        """
        if isinstance(x, SarusTensorflowDataset):
            x = x._tensorflow()
        return super().predict(
            x=x,
            batch_size=batch_size,
            verbose=verbose,
            steps=steps,
            callbacks=callbacks,
            max_queue_size=max_queue_size,
            workers=workers,
            use_multiprocessing=use_multiprocessing,
        )

    def evaluate(
        self,
        x: Data = None,
        y: Data = None,
        batch_size: Optional[int] = None,
        verbose: int = 1,
        sample_weight: Optional[np.ndarray] = None,
        steps: Optional[int] = None,
        callbacks: Optional[List[tf.keras.callbacks.Callback]] = None,
        max_queue_size: int = 10,
        workers: int = 1,
        use_multiprocessing: bool = False,
        return_dict: bool = False,
        **kwargs: Any,
    ) -> Union[float, List[float]]:
        """Return the loss value and metrics values for the model in test mode.

        Computation is done in batches (see the `batch_size`).

        Args:

        x: Input data.
            It could be:

            - A Numpy array (or array-like), or a list of arrays
                (in case the model has multiple inputs).
            - A TensorFlow tensor, or a list of tensors
                (in case the model has multiple inputs).
            - A dict mapping input names to the corresponding array/tensors,
                if the model has named inputs.
            - A `tf.data` dataset.
                Should return a tuple
                of either `(inputs, targets)` or
                `(inputs, targets, sample_weights)`.
            - A `SarusTensorflowDataset` dataset.
                Should return a tuple
                of either `(inputs, targets)` or
                `(inputs, targets, sample_weights)`.
            - A generator or `keras.utils.Sequence`
                returning `(inputs, targets)` or `(inputs, targets,
                sample_weights)`.

            A more detailed description of unpacking behavior for iterator types
            (Dataset, generator, Sequence) is given in the `Unpacking behavior
            for iterator-like inputs` section of `Model.fit`.

        y: Target data.
            Like the input data `x`, it could be either Numpy
            array(s) or TensorFlow tensor(s). It should be consistent with
            `x` (you cannot have Numpy inputs and tensor targets, or
            inversely). If `x` is a dataset, generator or `keras.utils.
            Sequence` instance, `y` should not be specified (since targets
            will be obtained from the iterator/dataset).

        batch_size (int, optional):
            Number of samples per batch of
            computation. If unspecified, `batch_size` will default to 32. Do not
            specify the `batch_size` if your data is in the form of a dataset,
            generators, or `keras.utils.Sequence` instances (since they generate
            batches).

        verbose (int): 0 or 1.
            Verbosity mode. 0 = silent, 1 = progress bar.

        sample_weight:
            Optional Numpy array of weights for the test samples,
            used for weighting the loss function. You can either pass a flat
            (1D) Numpy array with the same length as the input samples
            (1:1 mapping between weights and samples), or in the case of
            temporal data, you can pass a 2D array with shape `(samples,
            sequence_length)`, to apply a different weight to every timestep
            of every sample. This argument is not supported when `x` is a
            dataset, instead pass sample weights as the third element of `x`.

        steps (int, optional):
            Total number of steps (batches of samples)
            before declaring the evaluation round finished. Ignored with the
            default value of `None`. If x is a `tf.data` dataset and `steps` is
            None, 'evaluate' will run until the dataset is exhausted. This
            argument is not supported with array inputs.

        callbacks: List of `keras.callbacks.Callback` instances.
            List of callbacks to apply during evaluation. See
            [callbacks](/api_docs/python/tf/keras/callbacks).
            max_queue_size: Integer. Used for generator or `keras.utils.
            Sequence` input only. Maximum size for the generator queue. If
            unspecified, `max_queue_size` will default to 10.

        workers (int):
            Used for generator or `keras.utils.Sequence` input
            only. Maximum number of processes to spin up when using
            process-based threading. If unspecified, `workers` will default to
            1. use_multiprocessing: Boolean. Used for generator or
            `keras.utils.Sequence` input only. If `True`, use process-based
            threading. If unspecified, `use_multiprocessing` will default to
            `False`. Note that because this implementation relies on
            multiprocessing, you should not pass non-picklable arguments to the
            generator as they can't be passed easily to children processes.
            return_dict: If `True`, loss and metric results are returned as a
            dict, with each key being the name of the metric. If `False`, they
            are returned as a list.

        **kwargs:
            Unused at this time.

        See the discussion of `Unpacking behavior for iterator-like inputs` for
        `Model.fit`.
        `Model.evaluate` is not yet supported with
        `tf.distribute.experimental.ParameterServerStrategy`.

        Returns:
            Scalar test loss (if the model has a single output and no metrics)
            or list of scalars (if the model has multiple outputs
            and/or metrics). The attribute `model.metrics_names` will give you
            the display labels for the scalar outputs.

        Raises:
            RuntimeError:
                If `model.evaluate` is wrapped in `tf.function`.

            ValueError:
                in case of invalid arguments.
        """
        if isinstance(x, SarusTensorflowDataset):
            x = x._tensorflow()
        return super().evaluate(
            x=x,
            y=y,
            batch_size=batch_size,
            verbose=verbose,
            sample_weight=sample_weight,
            steps=steps,
            callbacks=callbacks,
            max_queue_size=max_queue_size,
            workers=workers,
            use_multiprocessing=use_multiprocessing,
            return_dict=return_dict,
            **kwargs,
        )

    def fit(
        self,
        x: Data = None,
        validation_data: Data = None,
        target_epsilon: float = 0.0,
        epochs: Optional[int] = None,
        l2_norm_clip: float = 1.0,
        noise_multiplier: float = 0.1,
        num_microbatches: Optional[int] = None,  # default: batch size
        verbose: bool = True,
        **kwargs: Any,
    ) -> Optional[tf.keras.callbacks.History]:
        """Trains the model for a fixed number of epochs.

        Args:

        x: The training data.
            It could be:

            - a SarusTensorflowDataset
            - a tensorflow.data.Dataset

            If `target_epsilon` is greater than 0 then `x` must be a
            `SarusTensorflowDataset`.

        validation_data: Defaults to None.
            Data on which to evaluate the loss and any model
            metrics at the end of each epoch. The model will not be trained on
            this data. Thus, note the fact that the validation loss of data
            provided using validation_split or `validation_data` is not affected
            by regularization layers like noise and dropout. `validation_data`
            will override validation_split. `validation_data` could be:

            - a SarusTensorflowDataset
            - a tensorflow.data.Dataset

            If `target_epsilon` is greater than 0 then `validation_data` must
            be None.


        epochs (int): Number of epochs to train the model.
            An epoch is an iteration over the entire data provided. Defaults to
            None.

        target_epsilon (float):
            Target epsilon for differentially private
            training. Defaults to 0.0. If `target_epsilon` is 0.0, the training
            is performed locally on the synthetic data. If If `target_epsilon`
            greater than 0.0, training is performed remotely with DP-SDG.

        l2_norm_clip (float):
            Defaults to 1.0.

        noise_multiplier (float):
            Defaults to 0.1.

        num_microbatches (int): Defaults to None.
            If `None` will default to `batch_size` of the dataset.

        Returns:
            History (History, optional):
                Returns a history object if trained locally, None otherwise.


        """
        if target_epsilon < 0:
            raise ValueError(
                f"`target_epsilon` must be positive, got {target_epsilon}"
            )

        if target_epsilon == 0:
            if epochs is None:
                raise ValueError(
                    "The number of `epochs` should be provided when "
                    "`target_epsilon` is 0."
                )
            return self._fit_local(
                x=x, epochs=epochs, validation_data=validation_data, **kwargs
            )
        else:
            if not isinstance(x, SarusTensorflowDataset):
                raise TypeError(
                    "Expected `x` to be a SarusTensorflowDataset "
                    f"with `target_epsilon`={target_epsilon}"
                )
            if validation_data:
                print(
                    "Warning: ignoring `validation_data` with remote training. "
                    "Not supported yet."
                )
            return self._fit_remote(
                x=x,
                target_epsilon=target_epsilon,
                l2_norm_clip=l2_norm_clip,
                noise_multiplier=noise_multiplier,
                num_microbatches=num_microbatches,
                verbose=verbose,
            )

    def _fit_local(
        self, x: Data, epochs: int, validation_data: Data, **kwargs: Any
    ) -> tf.keras.callbacks.History:
        if isinstance(x, SarusTensorflowDataset):
            x = x._tensorflow()
            print("Fitting model locally on synthetic data.")
        if isinstance(validation_data, SarusTensorflowDataset):
            validation_data = validation_data._tensorflow()
        history = super().fit(
            x=x, epochs=epochs, validation_data=validation_data, **kwargs
        )
        print("Actual privacy consumption (epsilon): 0.0")
        return history

    def _fit_remote(
        self,
        x: SarusTensorflowDataset,
        target_epsilon: float,
        l2_norm_clip: Optional[float] = None,
        noise_multiplier: Optional[float] = None,
        num_microbatches: Optional[int] = None,  # default: batch size
        verbose: bool = True,
        wait_for_completion: bool = True,
        **kwargs: Any,
    ) -> None:
        client = x.dataset.client
        if client is None:
            raise ValueError(
                f"The Sarus Dataset client is None: can not fit "
                f"remotely with `target_epsilon`={target_epsilon}."
            )

        batch_size, transforms = Model._refactor_transforms(
            x.dataset.transforms
        )
        transform_def = Model._make_transform_def(transforms)

        # Set loss reduction to None for DP-SGD
        previous_reduction = self.loss.reduction
        self.loss.reduction = tf.keras.losses.Reduction.NONE
        if previous_reduction != tf.keras.losses.Reduction.NONE:
            print("Changing loss reduction to NONE for DP-SGD.")

        task_id = client._fit(
            transform_def=transform_def,
            keras_model_def=lambda: self,
            x=x.dataset,
            target_epsilon=target_epsilon,
            batch_size=batch_size,
            non_DP_training=False,
            dp_l2_norm_clip=l2_norm_clip,
            dp_noise_multiplier=noise_multiplier,
            dp_num_microbatches=num_microbatches,  # default: batch size
            seed=None,
            verbose=verbose,
            wait_for_completion=wait_for_completion,
            **kwargs,
        )

        # Set fetched weights to model
        if "error_message" not in client._training_status(task_id):
            trained_model: tf.keras.Model = client._fetch_model(task_id)
            self.set_weights(trained_model.get_weights())

        # Restore previous loss reduction
        self.loss.reduction = previous_reduction

    @staticmethod
    def _refactor_transforms(
        transforms: List[Transform],
    ) -> Tuple[int, List[Transform]]:
        """Refactor the `transforms`.

        Merge consecutive `batch` and `unbatch` operations for more efficient
        processign on the API side.

        NB: this could be removed once the API does not batch by default.
        """
        if transforms[0][0] == "unbatch" and transforms[1][0] == "batch":
            batch_size = transforms[1][1]["batch_size"]
            transforms = transforms[2:]
        else:
            batch_size = 1
        return batch_size, transforms

    @staticmethod
    def _make_transform_def(transforms: List[Transform]) -> Callable:
        def transform_def(
            ds: tf.data.Dataset, features: Optional[Dict] = None
        ) -> tf.data.Dataset:
            """Build a function to be sent remotely.

            This function should not make use of objects or functions defined
            in the Sarus module to avoid it being listed as a closure by
            cloudpickle.
            """
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

        return transform_def
