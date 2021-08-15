import unittest
import numpy as np
import pandas as pd
from sklearn.metrics import balanced_accuracy_score

from jaison.api.types import ProblemDefinition
from jaison.api.high_level import predictor_from_problem
np.random.seed(42)


class TestBasic(unittest.TestCase):
    def setup_predictor(self, df, target):
        mask = np.random.rand(len(df)) < 0.8
        train = df[mask]
        test = df[~mask]

        predictor = predictor_from_problem(df, ProblemDefinition.from_dict({'target': target, 'time_aim': 20}))
        predictor.learn(train)

        if hasattr(predictor, 'ensemble'):
            for i, model in enumerate(predictor.ensemble.models):

                predictor.ensemble.best_index = i
                predictions = predictor.predict(test)
                assert 'truth' in predictions.columns
                assert 'prediction' in predictions.columns
                assert 'confidence' in predictions.columns

                predictions = predictor.predict_proba(test)

                for label in df[target].unique():
                    assert f'__mdb_proba_{label}' in predictions.columns
        return predictor

    def test_0_binary(self):
        df = pd.read_csv('tests/data/adult.csv')[:300]
        target = 'income'
        predictor = self.setup_predictor(df, target)
        predictions = predictor.predict(df)

        self.assertTrue(balanced_accuracy_score(df[target], predictions['prediction']) > 0.7)
        self.assertTrue(all([0 <= p <= 1 for p in predictions['confidence']]))

    def test_1_categorical(self):
        df = pd.read_csv('tests/data/hdi.csv')
        target = 'Development Index'
        predictor = self.setup_predictor(df, target)
        predictions = predictor.predict(df)

        self.assertTrue(balanced_accuracy_score(df[target].astype(int), predictions['prediction'].astype(int)) > 0.9)
        self.assertTrue(all([0 <= p <= 1 for p in predictions['confidence']]))
