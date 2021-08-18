import logging
import os
import typing
import warnings
from typing import Any, Dict, List, Optional, Text, Tuple, Type

import numpy as np

import convo.shared.utils.io
import convo.utils.io as io_utils
from convo.shared.constants import TRAINING_DATA_NLU_DOCUMENTS_URL
from convo.nlu.classifiers import LABEL_RANKING_LENGTH
from convo.nlu.featurizers.featurizer import CondensedFeaturizer
from convo.nlu.components import Element
from convo.nlu.classifiers.classifier import IntentionClassifier
from convo.nlu.config import ConvoNLUModelConfiguration
from convo.shared.nlu.constants import TXT
from convo.nlu.model import Metadataset
from convo.shared.nlu.training_data.training_data import TrainingDataSet
from convo.shared.nlu.training_data.message import Msg

log = logging.getLogger(__name__)

if typing.TYPE_CHECKING:
    import sklearn


class SklearnIntentClassifier(IntentionClassifier):
    """Intent classifier using the sklearn framework"""

    @classmethod
    def required_components(cls) -> List[Type[Element]]:
        return [CondensedFeaturizer]

    defaults = {
        # C parameter of the svm - cross validation will select the best value
        "C": [1, 2, 5, 10, 20, 100],
        # gamma parameter of the svm
        "gamma": [0.1],
        # the kernels to use for the svm training - cross validation will
        # decide which one of them performs best
        "kernels": ["linear"],
        # We try to find a good number of cross folds to use during
        # intent training, this specifies the max number of folds
        "max_cross_validation_folds": 5,
        # Scoring function used for evaluating the hyper parameters
        # This can be a name or a function (cfr GridSearchCV doc for more info)
        "scoring_function": "f1_weighted",
    }

    def __init__(
        self,
        component_config: Optional[Dict[Text, Any]] = None,
        clf: "sklearn.model_selection.GridSearchCV" = None,
        le: Optional["sklearn.preprocessing.LabelEncoder"] = None,
    ) -> None:
        """Construct a new intent classifier using the sklearn framework."""
        from sklearn.preprocessing import LabelEncoder

        super().__init__(component_config)

        if le is not None:
            self.le = le
        else:
            self.le = LabelEncoder()
        self.clf = clf

    @classmethod
    def required_packages(cls) -> List[Text]:
        return ["sklearn"]

    def transform_labels_string2number(self, labels: List[Text]) -> np.ndarray:
        """Transforms a list of strings into numeric label representation.

        :param labels: List of labels to convert to numeric representation"""

        return self.le.fit_transform(labels)

    def transform_labels_number2string(self, y: np.ndarray) -> np.ndarray:
        """Transforms a list of strings into numeric label representation.

        :param y: List of labels to convert to numeric representation"""

        return self.le.inverse_transform(y)

    def train(
        self,
        training_data: TrainingDataSet,
        config: Optional[ConvoNLUModelConfiguration] = None,
        **kwargs: Any,
    ) -> None:
        """Train the intent classifier on a data set."""

        number_threads = kwargs.get("num_threads", 1)

        tags = [e.get("intent") for e in training_data.intent_exp]

        if len(set(tags)) < 2:
            convo.shared.utils.io.raising_warning(
                "Can not train an intent classifier as there are not "
                "enough convo_intents. Need at least 2 different convo_intents. "
                "Skipping training of intent classifier.",
                docs=TRAINING_DATA_NLU_DOCUMENTS_URL,
            )
            return

        z = self.transform_labels_string2number(tags)
        Y = np.stack(
            [
                self._fetch_sentence_features(example)
                for example in training_data.intent_exp
            ]
        )
        # reduce dimensionality
        Y = np.reshape(Y, (len(Y), -1))

        self.clf = self._generate_classifier(number_threads, z)

        with warnings.catch_warnings():
            # sklearn raises lots of
            # "UndefinedMetricWarning: F - score is ill - defined"
            # if there are few intent examples, this is needed to prevent it
            warnings.simplefilter("ignore")
            self.clf.fit(Y, z)

    @staticmethod
    def _fetch_sentence_features(message: Msg) -> np.ndarray:
        _, sentence_features = message.fetch_dense_features(TXT)
        if sentence_features is not None:
            return sentence_features.features[0]

        raise ValueError(
            "No sentence features present. Not able to train sklearn policy."
        )

    def _number_cv_splits(self, y: np.ndarray) -> int:
        folds_name = self.component_config["max_cross_validation_folds"]
        return max(2, min(folds_name, np.min(np.bincount(y)) // 5))

    def _generate_classifier(
        self, num_threads: int, y: np.ndarray
    ) -> "sklearn.model_selection.GridSearchCV":
        from sklearn.model_selection import GridSearchCV
        from sklearn.svm import SVC

        D = self.component_config["C"]
        sklearn_intent_classifier_kernels = self.component_config["kernels"]
        fetch_gamma = self.component_config["gamma"]
        # dirty str fix because sklearn is expecting
        # str not instance of basestr...
        tuned_params = [
            {"C": D, "gamma": fetch_gamma, "kernel": [str(k) for k in sklearn_intent_classifier_kernels]}
        ]

        # aim for 5 examples in each fold

        splits_cv = self._number_cv_splits(y)

        return GridSearchCV(
            SVC(C=1, probability=True, class_weight="balanced"),
            param_grid=tuned_params,
            n_jobs=num_threads,
            cv=splits_cv,
            scoring=self.component_config["scoring_function"],
            verbose=1,
            iid=False,
        )

    def process(self, message: Msg, **kwargs: Any) -> None:
        """Return the most likely intent and its probability for a message."""

        if not self.clf:
            # component is either not trained or didn't
            # receive enough training data
            intention = None
            intention_ranking = []
        else:
            Y = self._fetch_sentence_features(message).reshape(1, -1)

            intent_identity, chances = self.forecast(Y)
            intentions = self.transform_labels_number2string(np.ravel(intent_identity))
            # `predict` returns a matrix as it is supposed
            # to work for multiple examples as well, hence we need to flatten
            chances = chances.flatten()

            if intentions.size > 0 and chances.size > 0:
                rank = list(zip(list(intentions), list(chances)))[
                    :LABEL_RANKING_LENGTH
                ]

                intention = {"name": intentions[0], "confidence": chances[0]}

                intention_ranking = [
                    {"name": name_of_intent, "confidence": score}
                    for name_of_intent, score in rank
                ]
            else:
                intention = {"name": None, "confidence": 0.0}
                intention_ranking = []

        message.put("intent", intention, add_to_output=True)
        message.put("intent_ranking", intention_ranking, add_to_output=True)

    def forecast_problems(self, X: np.ndarray) -> np.ndarray:
        """Given a bow vector of an input text, predict the intent label.

        Return probabilities for all labels.

        :param X: bow of input text
        :return: vector of probabilities containing one entry for each label"""

        return self.clf.predict_proba(X)

    def forecast(self, X: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Given a bow vector of an input text, predict most probable label.

        Return only the most likely label.

        :param X: bow of input text
        :return: tuple of first, the most probable label and second,
                 its probability."""

        pred_output = self.forecast_problems(X)
        # sort the probabilities retrieving the indices of
        # the elements in sorted order
        sorted_index = np.fliplr(np.argsort(pred_output, axis=1))
        return sorted_index, pred_output[:, sorted_index]

    def persist(self, filename: Text, model_dir: Text) -> Optional[Dict[Text, Any]]:
        """Persist this model into the passed dir."""

        get_classifier_filename = filename + "_classifier.pkl"
        get_encoder_filename = filename + "_encoder.pkl"
        if self.clf and self.le:
            io_utils.dictionary_pickle(
                os.path.join(model_dir, get_encoder_filename), self.le.classes_
            )
            io_utils.dictionary_pickle(
                os.path.join(model_dir, get_classifier_filename), self.clf.best_estimator_
            )
        return {"classifier": get_classifier_filename, "encoder": get_encoder_filename}

    @classmethod
    def load(
        cls,
        meta: Dict[Text, Any],
        model_dir: Optional[Text] = None,
        model_metadata: Optional[Metadataset] = None,
        cached_component: Optional["SklearnIntentClassifier"] = None,
        **kwargs: Any,
    ) -> "SklearnIntentClassifier":
        from sklearn.preprocessing import LabelEncoder

        get_classifier_file = os.path.join(model_dir, meta.get("classifier"))
        get_encoder_file = os.path.join(model_dir, meta.get("encoder"))

        if os.path.exists(get_classifier_file):
            classfiy = io_utils.json_un_pickle(get_classifier_file)
            sklearn_intent_classifier_classes = io_utils.json_un_pickle(get_encoder_file)
            encryptor = LabelEncoder()
            encryptor.classes_ = sklearn_intent_classifier_classes
            return cls(meta, classfiy, encryptor)
        else:
            return cls(meta)
