import pytest
import os

from azureml.automl.dnn.nlp.ner.io.read.dataset_wrapper import DatasetWrapper
from azureml.automl.dnn.nlp.ner.utils import Split, InputFeatures


@pytest.mark.usefixtures('new_clean_dir')
class TestDatasetWrapper:
    def test_token_classification_dataset(self, get_tokenizer):
        tokenizer = get_tokenizer
        max_seq_length = 20
        mode = Split.test
        test_dataset = DatasetWrapper(
            data_dir='ner_data',
            dataset_file="sample_test.txt",
            tokenizer=get_tokenizer,
            labels=["O", "B-MISC", "I-MISC", "B-PER", "I-PER", "B-ORG", "I-ORG", "B-LOC", "I-LOC"],
            model_type="bert",
            max_seq_length=max_seq_length,
            mode=mode
        )
        assert len(test_dataset) == 3
        for test_example in test_dataset:
            assert type(test_example) == InputFeatures
            assert len(test_example.input_ids) == max_seq_length
            assert len(test_example.attention_mask) == max_seq_length
            assert len(test_example.token_type_ids) == max_seq_length
            assert len(test_example.label_ids) == max_seq_length
        assert os.path.exists(os.path.join('ner_data',
                                           "cached_{}_{}_{}".format(mode.value,
                                                                    tokenizer.__class__.__name__,
                                                                    str(max_seq_length))))
