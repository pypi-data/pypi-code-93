import filecmp
import os
import pytest
import random

from azureml.automl.dnn.nlp.ner.ner_tasks import (
    convert_examples_to_features, read_examples_from_file, write_predictions_to_file
)
from azureml.automl.dnn.nlp.ner.utils import (
    Split,
    InputExample,
    InputFeatures
)


@pytest.mark.usefixtures('new_clean_dir')
class TestTokenClassificationTask:
    def test_read_examples_from_file(self):
        mode = Split.train.value
        examples = read_examples_from_file('ner_data/train.txt', mode)
        assert len(examples) == 3
        label_list = ['B-LOC', 'B-MISC', 'B-ORG', 'B-PER', 'I-LOC', 'I-MISC', 'I-ORG', 'I-PER', 'O']
        guid_index = 1
        for example in examples:
            assert type(example) == InputExample
            assert example.guid == "{}-{}".format(mode, guid_index)
            guid_index += 1
            for label in example.labels:
                assert label in label_list

    def test_write_predictions_to_file(self):
        preds_list = []
        preds_proba_list = []
        curr_predictions = []
        curr_predictions_proba = []
        label_list = ['B-LOC', 'B-MISC', 'B-ORG', 'B-PER', 'I-LOC', 'I-MISC', 'I-ORG', 'I-PER', 'O']
        expected_output_path = os.path.join('ner_data', 'expected_test_writer.txt')
        with open(expected_output_path, "w") as writer:
            with open(os.path.join('ner_data', "sample_test.txt"), "r") as test_input_reader:
                for line in test_input_reader:
                    if line == "" or line == "\n":
                        preds_list.append(curr_predictions)
                        preds_proba_list.append(curr_predictions_proba)
                        curr_predictions = []
                        curr_predictions_proba = []
                        writer.write(line)
                    else:
                        curr_label = random.choice(label_list)
                        curr_proba = random.random()
                        curr_predictions.append(curr_label)
                        curr_predictions_proba.append(curr_proba)
                        output_line = line.split()[0] + " " + curr_label + " " + str(curr_proba) + "\n"
                        writer.write(output_line)
                # process last line
                preds_list.append(curr_predictions)
                preds_proba_list.append(curr_predictions_proba)

        actual_output_path = os.path.join('ner_data', 'actual_test_writer.txt')
        with open(actual_output_path, "w") as test_writer:
            with open(os.path.join('ner_data', "sample_test.txt"), "r") as test_reader:
                write_predictions_to_file(
                    test_writer, test_reader, preds_list, preds_proba_list
                )

        assert filecmp.cmp(expected_output_path, actual_output_path)
        assert filecmp.cmp(expected_output_path, actual_output_path, shallow=False)

    def test_convert_examples_to_features(self, get_tokenizer):
        mode = Split.test.value
        examples = read_examples_from_file('ner_data/sample_test.txt', mode)
        labels = ["O", "B-MISC", "I-MISC", "B-PER", "I-PER", "B-ORG", "I-ORG", "B-LOC", "I-LOC"]
        max_seq_length = 20
        tokenizer = get_tokenizer
        features = convert_examples_to_features(
            examples,
            labels,
            max_seq_length,
            tokenizer,
            cls_token=tokenizer.cls_token,
            cls_token_segment_id=0,
            sep_token=tokenizer.sep_token,
            pad_on_left=bool(tokenizer.padding_side == "left"),
            pad_token=tokenizer.pad_token_id,
            pad_token_segment_id=tokenizer.pad_token_type_id
        )
        assert len(features) == len(examples)
        for feature in features:
            assert type(feature) == InputFeatures
            assert len(feature.input_ids) == max_seq_length
            assert len(feature.attention_mask) == max_seq_length
            assert len(feature.token_type_ids) == max_seq_length
            assert len(feature.label_ids) == max_seq_length
