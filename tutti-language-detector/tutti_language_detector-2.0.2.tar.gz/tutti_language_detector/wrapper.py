import os
import re
import string
import subprocess
import unicodedata
from logging import getLogger
from typing import List

import numpy as np
import pandas as pd
import pkg_resources
from sklearn.metrics import accuracy_score, log_loss

logger = getLogger('VWMultiClassifier')


def remove_bad_chars(text: str) -> str:
    """
    Remove control characters from input string
    :param text: input string
    :type text: str
    :return: input text without control characters
    :rtype: str
    """
    text = text.replace('\n', ' ').translate(str.maketrans('', '', string.punctuation))
    return ''.join(ch for ch in text if unicodedata.category(ch) != 'Cc')


def vw_pretrained_model(version: str = '0.0.2'):
    """
    Get a VW pretrained model from the ones that are included in the package

    :param version: version of the model to get (has to be one of the versions included in the package) 
    """
    if version not in VWMultiClassifier.get_pretrained_versions():
        raise ValueError('Model version unknown')
    return VWMultiClassifier(model=VWMultiClassifier.get_language_model_path(version=version))


class VWMultiClassifier:
    """
    This class acts as a non-generic classifier for Vowpal Wabbit. It is non generic as it is specialised
    for the task of detecting tutti.ch ads language
    """
    params = dict()

    def __init__(self, random_seed: int = 42, ngram_size: int = 0, passes: int = 20, bit_precision: int = 25,
                 l2: float = 0, model: str = None, loss_function: str = 'logistic', multiclass: bool = False,
                 oaa: int = 0, cache_file: str = None):
        """
        Constructor for the Vowpal Wabbit wrapper class that has methods for training/testing language datasets
        :param random_seed: random seed
        :param ngram_size: size of the N grams, if ngram_size=0 no N grams used
        :param passes: number of passes over the train set
        :param bit_precision: bit precision used by VW
        :param l2: L2 constraint to the model, if l2=0 the model is not regularized
        :param model: name of a model to load (NOTE: if model is loaded and no train is performed, the object will use
        this model to make predictions regardless of the rest of arguments in this constructor.)
        :param multiclass: flag that tells the model if there are more than 2 classes
        :param oaa: (One Against All) number of classes to predict from (only relevant for multiclass=True)
        :param loss_function: loss function to use, the available values are the ones available to the vw binary
        :param cache_file: name of the cache file to use (default is dataset_name.vw.cache)
        """
        # Reset params
        self.params = {'quiet': True}

        # Params checks
        if ngram_size == 1:
            ngram_size = 0
        if multiclass:
            if oaa < 3:
                raise ValueError('If multiclass=True, oaa must be at least 3.')
        if model:
            if not os.path.isfile(model):
                raise ValueError('The provided model file does not exist.')

        args = dict(locals())
        for k, v in args.items():
            if k != 'self' and k != '__class__' and v is not None:
                self.params[k] = v

    @staticmethod
    def get_pretrained_versions() -> List[str]:
        model_versions = ['0.0.1', '0.0.2', '0.0.3']
        return model_versions

    @staticmethod
    def get_language_model_path(version: str):
        """
        Get the path to the pretrained model given a version number
        :param version: model version number
        """
        resource_package = __name__
        resource_path = os.path.join('models', 'vw-{}.model'.format(version))
        return pkg_resources.resource_filename(resource_package, resource_path)

    @staticmethod
    def to_vw(df: pd.DataFrame, filepath: str = 'out.vw', columns: List[str] = None, target: str = None,
              tag: str = None, shuffle: bool = True, train_test_split: bool = False, **kwargs) -> None:
        """
        Generic function to convert a pandas DataFrame into a Vowpal Wabbit formatted file. This function accepts
        features such as tags, string features and numeric features.

        NOTE:
         - This function supports only a single (optionally named) namespace.
         - This function expects the target to consist of integer labels (1, 2, ...), or (-1, 1) in case of binary
         classification. Otherwise VW won't work with the generated vw file
        Source: modified version of https://gist.github.com/maxpagels/6685efe304180e5a499540c85158b287

        :param df: input dataframe
        :param filepath: path to output file in Vowpal Wabbit format
        :param columns: list of columns to include into the output file (list of features, can include tag and
            target here too)
        :param target: name of the target column (if exists)
        :param tag: name of the tag column (if exists)
        :param shuffle: indicates if function should shuffle the input dataset (VW is an online learner and performs
            best with shuffled data files where classes are not grouped together)
        :param train_test_split: flag that tells the function to split the dataset into train/test to get 3 .vw files
            in one single execution instead of calling to_vw on every DataFrame
        :key train_path: path to output train file. Default is filepath + '_train.vw' (only used if
            train_test_split == True)
        :key test_path: path to output test file. Default is filepath + '_test.vw' (only used if train_test_split
            == True)
        :key test_size: float, proportion of rows of input dataset to use as test set (only used if
            train_test_split == True)
        :key random_seed: seed to use for random related functions (only applies if shuffle == True and/or
            train_test_split == True)
        """
        # If no columns specified, we use them all, except the target and tag
        if columns is None:
            columns = df.columns.tolist()
        if target in columns:
            columns.remove(target)
        if tag:
            columns.remove(tag)

        if 'random_seed' in kwargs:
            random_seed = kwargs['random_seed']
            np.random.seed(seed=random_seed)
            if shuffle:
                df = df.sample(frac=1, random_state=random_seed).reset_index(drop=True)

        # Check if we need to do a train/test split
        if train_test_split:
            if 'test_size' in kwargs:
                test_size = kwargs['test_size']
            else:
                test_size = 0.3
            if 'train_path' in kwargs:
                train_path = kwargs['train_path']
            else:
                train_path = filepath[:-3] + '_train.vw'
            if 'test_path' in kwargs:
                test_path = kwargs['test_path']
            else:
                test_path = filepath[:-3] + '_test.vw'

            num_rows = len(df.index)
            num_rows_test = np.int32(num_rows * test_size)
            test_idxs = sorted(np.random.choice(num_rows, num_rows_test, replace=False))

            with open(filepath, 'w') as fd_total, open(train_path, 'w') as fd_train, open(test_path, 'w') as fd_test:
                test_counter = 0
                for idx, row in df.iterrows():
                    if target:
                        s = '{target} '.format(target=row[target])
                        fd_total.write(s)
                        if idx == test_idxs[test_counter]:
                            fd_test.write(s)
                        else:
                            fd_train.write(s)
                    if tag:
                        s = '\'{tag} '.format(tag=row[tag])
                        fd_total.write(s)
                        if idx == test_idxs[test_counter]:
                            fd_test.write(s)
                        else:
                            fd_train.write(s)
                    s = '| '
                    fd_total.write(s)
                    if idx == test_idxs[test_counter]:
                        fd_test.write(s)
                    else:
                        fd_train.write(s)
                    last_feature = columns[-1]
                    for col, val in row.iteritems():
                        if col not in columns:
                            continue
                        if isinstance(val, str):
                            s = remove_bad_chars(val)
                            fd_total.write(s)
                            if idx == test_idxs[test_counter]:
                                fd_test.write(s)
                            else:
                                fd_train.write(s)
                        elif isinstance(val, float) or isinstance(val, int):
                            if not np.isnan(val):
                                s = '{name}:{value}'.format(name=col.replace(' ', '_').replace(':', '_'), value=val)
                                fd_total.write(s)
                                if idx == test_idxs[test_counter]:
                                    fd_test.write(s)
                                else:
                                    fd_train.write(s)
                            else:
                                continue
                        else:
                            fd_total.write(val)
                            if idx == test_idxs[test_counter]:
                                fd_test.write(val)
                            else:
                                fd_train.write(val)
                        if col != last_feature:
                            s = ' '
                            fd_total.write(s)
                            if idx == test_idxs[test_counter]:
                                fd_test.write(s)
                            else:
                                fd_train.write(s)
                    s = '\n'
                    fd_total.write(s)
                    if idx == test_idxs[test_counter]:
                        fd_test.write(s)
                        # Increase counter of written test rows
                        test_counter = test_counter + 1
                        # If all test rows have been written we set test_counter to a valid index that will never
                        # trigger a false positive
                        if test_counter >= num_rows_test:
                            test_counter = 0
                    else:
                        fd_train.write(s)
        else:
            with open(filepath, 'w') as fd_total:
                for _, row in df.iterrows():
                    if target:
                        fd_total.write('{target} '.format(target=row[target]))
                    if tag:
                        fd_total.write('\'{tag} '.format(tag=row[tag]))
                    fd_total.write('| ')
                    last_feature = columns[-1]
                    for col, val in row.iteritems():
                        if col not in columns:
                            continue
                        if isinstance(val, str):
                            fd_total.write(remove_bad_chars(val))
                        elif isinstance(val, float) or isinstance(val, int):
                            if not np.isnan(val):
                                fd_total.write('{name}:{value}'.format(name=col.replace(' ', '_').replace(':', '_'),
                                                                       value=val))
                            else:
                                continue
                        else:
                            fd_total.write(val)
                        if col != last_feature:
                            fd_total.write(' ')
                    fd_total.write('\n')

    def fit(self, train_file: str, output_model: str = 'detect_oaa.model'):
        """
        Train a Vowpal Wabbit logistic One Against All classifier for 3 classes (languages) with settings
        :param train_file: train dataset in Vowpal Wabbit format
        :param output_model: name of output model file
        :return:
        """
        # Construction of fit command
        command = ['vw']
        if self.params['multiclass']:
            command.append('--oaa={}'.format(self.params['oaa']))
        if self.params['ngram_size'] > 1:
            command.append('--ngram={}'.format(self.params['ngram_size']))
        command = command + [
            '--data={}'.format(train_file),
            '--loss_function={}'.format(self.params['loss_function']),
            '--final_regressor={}'.format(output_model),
            '--cache',
            '--passes={}'.format(self.params['passes']),
            '--bit_precision={}'.format(self.params['bit_precision'])
        ]
        if 'cache_file' in self.params:
            command.append('--cache_file={}'.format(self.params['cache_file']))
        if self.params['l2'] != 0:
            command.append('--l2={}'.format(self.params['l2']))
        command.append('--random_seed={}'.format(self.params['random_seed']))

        # Run fit command
        out = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding='utf-8', check=True)
        logger.debug(out.stdout)

        # Store model in class
        self.params['model'] = output_model

    def load_model(self, model_name: str, loss_function: str = None) -> None:
        """
        Load a model file into the class to use for predictions
        :param model_name: name of the file that contains the VW model
        :param loss_function: loss function used in the loaded model
        :return: nothing
        """
        self.params['model'] = model_name
        if loss_function:
            self.params['loss_function'] = loss_function

    @classmethod
    def test_model(cls, model: str, predictions_file: str, test_file: str, probabilities: bool = True):
        """
        Test given model against a test file and return a performance metric
        :param model: Vowpal Wabbit model to test
        :param predictions_file: name of the file to output the resulting predictions/probabilities
        :param test_file: path to test file in Vowpal Wabbit format
        :param probabilities: whether the model has to return probabilities for each class or just prediction (NOTE:
        probability output needs loss_function=logistic. If the model was not trained with this parameter the behaviour
        of this option could be unexpected).
        :return: cross entropy score for probabilities=True or accuracy score for probabilities=False
        """
        if not os.path.exists(model):
            raise AttributeError('The specified model file does not exist.')

        # Set command
        command = [
            'vw',
            '--initial_regressor={}'.format(model),
            '--testonly',
            '--data={}'.format(test_file)
        ]
        if probabilities:
            command = command + [
                '--loss_function=logistic',
                '--probabilities'
            ]
        command = command + [
            '--predictions={}'.format(predictions_file),
            '--quiet'
        ]
        # Run command
        subprocess.run(command, check=True, stdout=subprocess.PIPE)

        # Compute metric from output
        y_true = cls.read_labels_from_vw_file(test_file)
        class_labels = np.unique(y_true)
        logger.debug('Detected classes: {}'.format(class_labels))
        if probabilities:
            y_pred = cls.read_vw_probabilities(filename=predictions_file, labels=class_labels)
            # logger.debug('Model predictions: \n{}'.format(y_pred))
            return log_loss(y_true=y_true, y_pred=y_pred, labels=class_labels)
        else:
            y_pred = cls.read_vw_predictions(filename=predictions_file)
            return accuracy_score(y_true=y_true, y_pred=y_pred)

    @staticmethod
    def read_labels_from_vw_file(filename: str) -> np.array:
        """
        Read labels from a test file
        :return: array of labels in file
        """
        with open(filename, 'r') as fd:
            labels = []
            for line in fd.readlines():
                labels.append(int(re.findall(pattern=r'^([0-9]*)|', string=line)[0]))
        return np.array(labels).reshape(-1, 1).astype(int)

    @staticmethod
    def read_vw_predictions(filename: str) -> np.array:
        """
        Read class predictions from result file (generated by test_model with probabilities=False)
        :return: array of predictions
        """
        with open(filename, 'r') as fd:
            predictions = [int(label) for label in fd.readlines()]
        return np.array(predictions).reshape(-1, 1).astype(int)

    @staticmethod
    def read_vw_probabilities(filename: str, labels) -> np.array:
        """
        Read probabilities from Vowpal Wabbit for N classes and create a DataFrame containing the values
        :param filename: name of the file to read predictions from
        :param labels: (array or list-like) with labels
        :returns: array of probabilities
        """
        with open(filename, 'r') as fd:
            rows = []
            for line in fd.readlines():
                probs = [float(x) for x in re.findall(r'\d+\.\d+', line)]
                rows.append(dict(zip(labels, probs)))
        # logger.debug('Returned values: \n{}'.format(pd.DataFrame(rows).values))
        return pd.DataFrame(rows).values

    def predict(self, nclasses: int, input_data: str = None, batch: bool = False):
        """
        Use the loaded model to detect the language of a string or to batch predict an input file
        :param nclasses: number of possible different classes expected in the prediction
        :param input_data: either a string (in Vowpal Wabbit format) for the example (i.e. a phrase in German,
        Italian or French) or a file name (for batch mode)
        :param batch: flag to indicate if we are doing single example detection or batch detection from file
        :return: prediction(s) for the input value(s)
        """
        if 'model' not in self.params.keys():
            raise AttributeError('{} object needs to have a loaded model to predict.'
                                 'Call load_model method'.format(self))

        model = self.params['model']
        logger.debug('Model is {}'.format(model))
        if batch:
            # Set output file path
            output_file = '/tmp/vw-language-model-output.vw'
            # Generate command
            command = [
                'vw',
                '--initial_regressor={}'.format(model),
                '--testonly',
                '--data={}'.format(input_data),
                '--loss_function=logistic',
                '--probabilities',
                '--predictions={}'.format(output_file),
                '--quiet'
            ]
            # Run command
            subprocess.run(command, check=True)
            # Read output of command
            probs_df = self.read_vw_probabilities(filename=output_file, labels=np.arange(nclasses))
            # Get prediction and probability from command output
            probability_df = pd.DataFrame(probs_df)
            predicted_language_idx = probability_df.idxmax(axis=1).values + 1
            predicted_language_prob = probability_df.max(axis=1).values
            return pd.DataFrame({'predicted_language': predicted_language_idx, 'probability': predicted_language_prob})
        else:
            # Create stdin process to act as input file
            tmp_input = subprocess.Popen(('echo', '{}'.format('| ' + remove_bad_chars(input_data))),
                                         stdout=subprocess.PIPE)
            # Generate command
            command = [
                'vw',
                '--initial_regressor={}'.format(model),
                '--testonly',
                '--data=/dev/stdin',
                '--loss_function=logistic',
                '--probabilities',
                '--predictions=/dev/stdout',
                '--quiet'
            ]
            # logger.debug('VW command: {}'.format(' '.join(command)))
            # Run command
            output = subprocess.run(command, check=True, stdin=tmp_input.stdout, stdout=subprocess.PIPE)
            # Read output of command
            line = output.stdout.decode('utf-8')
            # Get prediction and probability from command output
            probs = [float(x) for x in re.findall(r'\d+\.\d+', line)]
            predicted_language_prob = max(probs)
            predicted_language_idx = probs.index(predicted_language_prob) + 1
            return pd.DataFrame({'predicted_language': [predicted_language_idx],
                                 'probability': [predicted_language_prob]})
