"""Module containing the evaluator base class and some default evaluators."""
import datetime
import json
import os
import pickle
import warnings

import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn import metrics
from sklearn.model_selection import BaseCrossValidator
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import PredefinedSplit
from sklearn.utils.validation import indexable

from .base import Evaluator
from .utils import LOGGER


def _check_fixed_split_data_shape(data):
    assert (len(data) == 2) or (len(data) == 3)
    assert len(data[0]) == 2

    if len(data) == 2:
        assert len(data[1]) == 2
    else:
        assert len(data[2]) == 2


def _extract_train_test_data(data):
    _check_fixed_split_data_shape(data)

    if len(data) == 2:
        return data
    else:
        train, _, test = data
        return train, test


class ModelCallbackWrapper(Evaluator):
    """Allows a callback to do something with the fitted model.

    E.g. predict or store in a pickle).
    """

    def __init__(self, wrapped_evaluator, callback, *callback_args,
                 **callback_kwargs):
        """Initializes the model callback wrapper object.

        Returns the fitted model to the callback method after evaluating
        using the wrapped evluator.
        """
        if not hasattr(wrapped_evaluator, 'fitted_model'):
            raise ValueError(
                f'the wrapped evaluator {wrapped_evaluator.__class__.__name__}'
                'does not have a fitted_model attribute.')
        self.wrapped_evaluator = wrapped_evaluator
        self.callback = callback
        self.callback_args = callback_args
        self.callback_kwargs = callback_kwargs

    def evaluate(self, model, data):
        """
        Evaluates the pipeline based on the given dataset.

        Args:
            model: the model given in the pipeline.
            data: the data needed for this run, passed to grid as:
                grid.fit(*data) therefore, the data can also contain groups.

        Returns: the result of the wrapped evaluator.
        """
        result = self.wrapped_evaluator.evaluate(model, data)
        fitted_model = self.wrapped_evaluator.fitted_model
        self.callback_result_ = self.callback(fitted_model,
                                              *self.callback_args,
                                              **self.callback_kwargs)
        return result

    @property
    def configuration(self):
        """A json-like representation of the configuration."""
        return {
            'model_callback': self.callback.__name__,
            'wrapped_evaluator': self.wrapped_evaluator.__class__.__name__,
            'wrapped_configuration': self.wrapped_evaluator.configuration,
        }


class GridEvaluator(Evaluator):
    """Evalutaor that performs a grid search."""

    def __init__(self, parameters, grid_parameters):
        """
        Creates a new instance.

        Args:
            parameter: passed to the GridSearchCV as configuration.
            grid_parameter: passed to the GridSearchCV to configure the
                gridsearch.
        """
        self.parameters = parameters
        self.grid_parameters = grid_parameters
        self.model_ = None

    def evaluate(self, model, data):
        """
        Evaluates the pipline based on the given dataset.

        Args:
            model: the model given in the pipeline.
            data: the data needed for this run, passed to grid as:
                grid.fit(*data) therefore, the data can also contain groups.

        Returns: A dict containting the results of the grid search.
        """
        grid = GridSearchCV(model, self.parameters, **self.grid_parameters)
        grid.fit(*data)
        # FIXME is it intended that the default is refitting?
        if self.grid_parameters.get('refit', True):
            self.model_ = grid.best_estimator_

        try:
            best_score = grid.best_score_
            best_params = grid.best_params_
        except AttributeError:
            best_score = None
            best_params = None

        return {
            'cv_results': pd.DataFrame(grid.cv_results_).to_dict(),
            'best_score': best_score,
            'best_params': best_params,
        }

    @property
    def fitted_model(self):
        """Contains the filtered model."""
        if self.model_ is None and \
                'refit' in self.grid_parameters and \
                self.grid_parameters['refit'] is False:
            warnings.warn('you have set refit=False, but are trying to access'
                          'the fitted model. It will always be None with this'
                          'configuration.')
        return self.model_

    @property
    def configuration(self):
        """
        Returns a dict-like representation of this evaluator.

        This is for storing its state in the database.
        """
        grid_parameters = {}
        for name, param in self.grid_parameters.items():
            try:
                # this checks if the parameter can be stored in the database,
                # and falls back if it is not hashable.
                json.dumps(param)
                grid_parameters[name] = param
            except TypeError:
                grid_parameters[name] = str(param)

        return {
            'pipeline_parameters': self.parameters,
            'grid_parameters': grid_parameters,
        }


class CustomCvGridEvaluator(GridEvaluator):
    """Use this evaluator if your dataloader returns a custom cv object."""

    def __init__(self, params, grid_params):
        """Initializes the grid evaluator object.

        Args:
            params: are passed to the sklearn gridsearch.
            grid_parameters: are passed to the sklearn gridsearch.
        """
        for param in ['cv']:
            if param in grid_params:
                warnings.warn(
                    f'{param}={grid_params[param]} was set in '
                    'grid_params, but this will be overwritten by the '
                    'evaluation method. Remove this parameter to silence '
                    'this warning.', UserWarning)
        super(CustomCvGridEvaluator, self).__init__(params, grid_params)

    def evaluate(self, model, data):
        """
        Evaluates the pipline based on the given dataset.

        Args:
            model: the model given in the pipeline.
            data: the data used to load explicit train and test data.

        Returns: A dict-like object containing the results.
        """
        assert len(data) == 3
        x, y, cv = data
        self.grid_parameters['cv'] = cv
        return super().evaluate(model, (x, y))


class FixedSplitGridEvaluator(GridEvaluator):
    """Runs eval on a fixed split.

    Use this evaluator if your dataloader returns explicit train / test
    samples. This evaluator will then use a PredefinedSplit to create one
    single run for each grid configuration.
    """

    def __init__(self, params, grid_params):
        """Initializes the grid evaluator object.

        Args:
            params: are passed to the sklearn gridsearch.
            grid_parameters: are passed to the sklearn gridsearch.
        """
        self.grid = None
        for param in ['cv']:
            if param in grid_params:
                warnings.warn(
                    f'{param}={grid_params[param]} was set in '
                    'grid_params, but this will be overwritten by the '
                    'evaluation method. Remove this parameter to silence '
                    'this warning.', UserWarning)
        super(FixedSplitGridEvaluator, self).__init__(params, grid_params)

    def evaluate(self, model, data):
        """
        Evaluates the pipline based on the given dataset.

        Args:
            model: the model given in the pipeline.
            data: the data used to load explicit train and test data.

        Returns: A dict containting the results of the grid search.
        """
        (xtrain, ytrain), (xtest, ytest) = _extract_train_test_data(data)
        # index=-1 means that these samples will never be used for testing
        target_indices = [-1] * len(xtrain) + [0] * len(xtest)
        self.grid_parameters['cv'] = PredefinedSplit(target_indices)

        # make sure that we have numpy-compatible data
        if type(xtrain) == list:
            xtrain = np.array(xtrain)
        if type(ytrain) == list:
            ytrain = np.array(ytrain)
        if type(xtest) == list:
            xtest = np.array(xtest)
        if type(ytest) == list:
            ytest = np.array(ytest)

        if type(xtrain) == np.ndarray:
            x = np.concatenate((xtrain, xtest))
        elif type(xtrain) in [pd.DataFrame, pd.Series]:
            x = pd.concat((xtrain, xtest))
        else:
            raise ValueError('don\'t know how to concatenate ', type(xtrain),
                             type(xtest))

        if type(ytrain) == np.ndarray:
            y = np.concatenate((ytrain, ytest))
        elif type(ytrain) in [pd.DataFrame, pd.Series]:
            y = pd.concat((ytrain, ytest))
        else:
            raise ValueError('don\'t know how to concatenate ', type(ytrain),
                             type(ytest))

        return super().evaluate(model, (x, y))


class FixedSplitEvaluator(Evaluator):
    """Evaluator that runs basic classification metrics on the pipline."""

    def __init__(self, scoring):
        """
        Creates a new instance.

        Args:
            scoring: if None, then f1, accuracy, recall, precision and the
                confusion matrix are computed. Otherwise, scoring has to be a
                dict where key is the name of the score and the value contains
                a scorer.
        """
        self.scoring = scoring
        self.model_ = None

    def evaluate(self, model, data):
        """
        Evaluates the pipline based on the given dataset.

        Args:
            model: the model given in the pipeline.
            data: a tuple of (xtrain, ytrain, xtest, ytest)

        Returns: A dict containting f1, accuracy, recall, precision and the
        confusion matrix.
        """
        (xtrain, ytrain), (xtest, ytest) = _extract_train_test_data(data)
        model.fit(xtrain, ytrain)

        self.model_ = model

        result = {}
        for name, scorer in self.scoring.items():
            score = scorer(model, xtest, ytest)
            if isinstance(score, np.ndarray):
                result[name] = score.tolist()
            else:
                result[name] = score
        return result

    @property
    def fitted_model(self):
        """Contains the fitted model after training."""
        return self.model_

    @property
    def configuration(self):
        """
        Returns a dict-like representation of this evaluator.

        This is for storing its state in the database.
        """
        return {
            'scoring': list(self.scoring.keys()),
        }


class ClassificationEvaluator(FixedSplitEvaluator):
    """Evaluator that runns basic classification metrics on the pipline."""

    def __init__(self, average='macro'):
        """
        Creates a new instance.

        Args:
            average: see the sklearn doc for e.g. f1_score .
        """
        super().__init__(
            scoring={
                'f1':
                    metrics.make_scorer(metrics.f1_score, average=average),
                'accuracy':
                    metrics.get_scorer('accuracy'),
                'recall':
                    metrics.make_scorer(metrics.recall_score, average=average),
                'precision':
                    metrics.make_scorer(metrics.precision_score,
                                        average=average),
                'confusion_matrix':
                    metrics.make_scorer(metrics.confusion_matrix),
            })
        self.average = average

    @property
    def configuration(self):
        """
        Returns a dict-like representation of this evaluator.

        This is for storing its state in the database.
        """
        return {
            'average': self.average,
            **super().configuration,
        }


class EpochEvaluator(FixedSplitEvaluator):
    """Evaluator that calculates multiple scorings based on training epochs."""

    def __init__(self, scoring, scoring_step_size=10):
        """Initializes the new instance.

        Args:
            scoring: has to be a dict where key is the name of the score and
                the value contains a scorer.
            scoring_step_size: is number of epochs between each scoring call.
        """
        super().__init__(scoring=scoring)
        self.scoring_step_size = scoring_step_size

    def evaluate(self, model, data):
        """
        Evaluates the pipline based on the given dataset.

        Args:
            model: the model given in the pipeline.
            data: a tuple of (xtrain, ytrain, xtest, ytest)

        Returns: A dict-like object containing the results.
        """
        (xtrain, ytrain), (xtest, ytest) = _extract_train_test_data(data)

        try:
            model_epochs = model.epochs
        except AttributeError:
            # assume that it is a sklearn pipeline object and only the last
            # estimator supports epochs.
            model_epochs = model[-1].epochs

        assert self.scoring_step_size <= model_epochs

        trained_epochs = 0
        result = {}
        while trained_epochs < model_epochs:
            if (model_epochs - trained_epochs) < self.scoring_step_size:
                epochs = model_epochs - trained_epochs
            else:
                epochs = self.scoring_step_size
            trained_epochs += epochs
            try:
                model.fit(xtrain, ytrain, epochs=epochs)
            except ValueError:
                # assume that it is a sklearn pipeline object and only the last
                # estimator supports epochs.
                name, _ = model.steps[-1]
                fit_params = dict([(name + '__epochs', epochs)])
                model.fit(xtrain, ytrain, **fit_params)

            result[trained_epochs] = self._calc_scoring(model, xtest, ytest)

        self.model_ = model

        return result

    def _calc_scoring(self, model, xtest, ytest):
        result = {}
        for name, scorer in self.scoring.items():
            score = scorer(model, xtest, ytest)
            if isinstance(score, np.ndarray):
                result[name] = score.tolist()
            else:
                result[name] = score
        return result


class CvEpochEvaluator(Evaluator):
    """CV evaluator calculating multiple scorings based on epochs.

    For each train-test split produced by the cross-validator this evaluator
    evaluates the model after a given number of epochs using all scoring
    metrics passed as done by EpochEvaluator.
    """

    def __init__(self, cv: BaseCrossValidator, scoring, scoring_step_size=10):
        """Initializes the new instance.

        Args:
            cv: cross-validation generator that determines the cross-validation
                splitting strategy.
            scoring: has to be a dict where key is the name of the score and
                the value contains a scorer.
            scoring_step_size: is number of epochs between each scoring call.
        """
        self.scoring = scoring
        self.scoring_step_size = scoring_step_size
        self.cv = cv

    def evaluate(self, model, data):
        """
        Evaluates the pipline based on the given dataset.

        Args:
            model: the model given in the pipeline.
            data: a tuple of (data, target)

        Returns: A dict-like object containing the results.
        """
        x, y = indexable(*data)
        base_model = clone(model)

        results = {}
        for split_id, split_indices in enumerate(self.cv.split(x, y)):
            evaluator = EpochEvaluator(
                scoring=self.scoring,
                scoring_step_size=self.scoring_step_size,
            )
            train_indices, test_indices = split_indices
            split_data = (
                (x[train_indices], y[train_indices]),
                (x[test_indices], y[test_indices]),
            )
            results[split_id] = evaluator.evaluate(
                clone(base_model),
                split_data,
            )

        for epoch, scoring in _aggregate_score_dicts(results):
            try:
                results['mean'][epoch] = {}
            except KeyError:
                results['mean'] = {}
                results['mean'][epoch] = {}

            try:
                results['stdev'][epoch] = {}
            except KeyError:
                results['stdev'] = {}
                results['stdev'][epoch] = {}

            for metric, values in scoring.items():
                values = np.array(values, dtype=np.float64)
                results['mean'][epoch][metric] = np.average(
                    values,
                    axis=0,
                ).tolist()
                results['stdev'][epoch][metric] = np.std(
                    values,
                    axis=0,
                ).tolist()

        return results

    @property
    def configuration(self):
        """
        Returns a dict-like representation of this evaluator.

        This is for storing its state in the database.
        """
        return {
            'scoring': list(self.scoring.keys()),
            'scoring_step_size': self.scoring_step_size,
            'cross_validator': self.cv.__class__.__name__,
            'number_of_splits': self.cv.get_n_splits(),
        }


def _aggregate_score_dicts(scores):
    scores = list(scores.values())
    for epoch, result in scores[0].items():
        yield epoch, {
            key: np.asarray([score[epoch][key] for score in scores
                            ]) for key in result.keys()  # noqa E124
        }


def split_df_input_and_target(df, columns):
    """
    Splits a DataFrame by removing the specified columns.

    Args:
        df: The input DataFrame to split
        columns: Either a list of strings or a string denoting the columns that
            are returned as target.

    Returns:
        a tuple (x, y), where x is the DataFrame without the columns specified
        in columns, and y is either a pandas series if columns is a string,
        or y is a pandas DataFrame if columns is a list of strings.
    """
    if type(columns) == str:
        return df.drop(columns=[columns]), df[columns]
    return df.drop(columns=columns), df[columns]


class DataframeEvaluatorWrapper(Evaluator):
    """A wrapper for Evaluators for DataFrames as input."""

    def __init__(self, target_columns, wrapped_class, *args, **kwargs):
        """
        Initializes the Wrapper.

        Args:
            target_columns: a string or list of strings to use as target
                columns.
            wrapped_class: the evaluator to be wrapped.
            *args: arguments passed to the __init__ method of the wrapped class
            **kwargs: keyword args passed to the __init__ of the wrapped class
        """
        self.target_columns = target_columns
        self.wrapped_class = wrapped_class
        self.evaluator = wrapped_class(*args, **kwargs)

    def evaluate(self, model, df_data):
        """
        Evaluates the model based on a DataFrame containing all data.

        Args:
            model: the pipeline object from your plan file
            df_data: either a tuple of (train, [validate,] test) DataFrames, or
                a single DataFrame containing the data. All DataFrames must
                include all target columns with the name specified in the
                __init__ method of this evaluator.

        Returns:
            A dictionary of grid search results.
        """
        if type(df_data) == pd.DataFrame:
            result = split_df_input_and_target(df_data, self.target_columns)
        elif type(df_data) == tuple:
            result = tuple([
                split_df_input_and_target(x, self.target_columns)
                for x in df_data
            ])
        else:
            raise ValueError('unable to interpret DataFrames from data')
        return self.evaluator.evaluate(model, result)

    @property
    def configuration(self):
        """Returns the configuration of this evaluator."""
        return {
            'target_columns': self.target_columns,
            'wrapped_evaluator': self.wrapped_class.__name__,
            'wrapped_configuration': self.evaluator.configuration,
        }


def _ensure_unique_file(name, append_timestamp=True):
    if append_timestamp:
        parts = os.path.splitext(name)
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d__%H-%M-%S')
        name = f'{parts[0]}_{timestamp}{parts[1]}'
    i = 0
    while os.path.isfile(name):
        parts = os.path.splitext(name)
        name = f'{parts[0]}_{i}{parts[1]}'
        i += 1
    return name


def pickle_model_callback(fitted_model, output_path):
    """Pickles fitted models, for ModelCallbackEvaluator."""
    unique_name = _ensure_unique_file(output_path)
    with open(unique_name, 'wb') as output_f:
        LOGGER.info('writing fitted model to %s', unique_name)
        pickle.dump(fitted_model, output_f)
        return unique_name
