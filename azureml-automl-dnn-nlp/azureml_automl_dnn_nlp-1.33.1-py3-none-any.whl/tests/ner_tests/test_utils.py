import pytest
import unittest

from azureml.automl.dnn.nlp.ner.utils import get_labels


@pytest.mark.usefixtures('new_clean_dir')
class UtilsTest(unittest.TestCase):
    """Tests for NER trainer."""
    def __init__(self, *args, **kwargs):
        super(UtilsTest, self).__init__(*args, **kwargs)

    def test_get_labels(self):
        labels = get_labels('ner_data/labels_misc.txt')
        self.assertEqual(set(labels), set(["O", "Aditya", "Anup", "Arjun", "Harsh"]))
        labels = get_labels(None)
        self.assertEqual(
            set(labels), set(["O", "B-MISC", "I-MISC", "B-PER", "I-PER", "B-ORG", "I-ORG", "B-LOC", "I-LOC"])
        )
