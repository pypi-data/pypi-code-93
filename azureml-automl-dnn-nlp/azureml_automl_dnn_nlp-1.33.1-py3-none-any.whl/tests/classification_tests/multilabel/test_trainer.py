import pytest
import unittest

from azureml.automl.dnn.nlp.classification.multilabel.trainer import PytorchTrainer
from azureml.automl.dnn.nlp.classification.common.constants import MultiLabelParameters
from azureml.automl.dnn.nlp.common.constants import Split


try:
    import torch
    has_torch = True
    from torch.utils.data import RandomSampler
except ImportError:
    has_torch = False


class MockBertClass(torch.nn.Module):
    def __init__(self, num_labels):
        super(MockBertClass, self).__init__()
        self.num_labels = num_labels
        self.l1 = torch.nn.Linear(num_labels, num_labels)
        # number of times forward was called
        self.forward_called = 0
        self.train_called = False
        self.eval_called = False
        return

    def forward(self, ids, attention_mask, token_type_ids):
        self.forward_called = self.forward_called + 1
        return self.l1(torch.randn(ids.shape[0], self.num_labels))

    def train(self, mode=True):
        self.train_called = True
        super().train(mode)

    def eval(self):
        self.eval_called = True
        super().eval()


class MockTextDataset(torch.utils.data.Dataset):
    def __init__(self, size, num_labels):
        # Inputs created using BertTokenizer('this is a sentence')
        self.inputs = {'input_ids': [101, 2023, 2003, 1037, 6251, 102],
                       'token_type_ids': [0, 0, 0, 0, 0, 0],
                       'attention_mask': [1, 1, 1, 1, 1, 1]}
        self.dataset_size = size
        self.num_labels = num_labels

    def __len__(self):
        return self.dataset_size

    def __getitem__(self, index):
        return {
            'ids': torch.tensor(self.inputs['input_ids'], dtype=torch.long),
            'mask': torch.tensor(self.inputs['attention_mask'], dtype=torch.long),
            'token_type_ids': torch.tensor(self.inputs['token_type_ids'], dtype=torch.long),
            'targets': torch.randint(self.num_labels, (2,)).float()
        }


@unittest.skipIf(not has_torch, "torch not installed")
def test_initialization_variables():
    PytorchTrainer(MockBertClass, 2)


@unittest.skipIf(not has_torch, "torch not installed")
@pytest.mark.parametrize('dataset_size',
                         [pytest.param(10),
                          pytest.param(10000),
                          pytest.param(MultiLabelParameters.TRAIN_BATCH_SIZE // 2),
                          pytest.param(MultiLabelParameters.TRAIN_BATCH_SIZE + 3),
                          pytest.param(MultiLabelParameters.TRAIN_BATCH_SIZE * 3)]
                         )
def test_train(dataset_size):
    num_labels = 2
    trainer = PytorchTrainer(MockBertClass, num_labels)
    model_parameters = next(trainer.model.l1.parameters()).data.clone()
    dataset = MockTextDataset(dataset_size, num_labels)
    model = trainer.train(dataset)

    # Assert training ran through entire data
    batch_size = MultiLabelParameters.TRAIN_BATCH_SIZE
    expected_steps = ((dataset_size // batch_size) + ((dataset_size % batch_size) > 0)) * MultiLabelParameters.EPOCHS
    assert trainer.model.forward_called == expected_steps, "Expected steps to run through entire dataset wasn't met"

    # Assert model parameters were updated
    assert not torch.equal(model_parameters, next(model.l1.parameters()).data), \
        "Train completed without updating any model parameters"

    assert trainer.model.train_called is True, "model.train should be called before training"


@unittest.skipIf(not has_torch, "torch not installed")
@pytest.mark.parametrize('dataset_size',
                         [pytest.param(10),
                          pytest.param(10000),
                          pytest.param(MultiLabelParameters.VALID_BATCH_SIZE // 2),
                          pytest.param(MultiLabelParameters.VALID_BATCH_SIZE + 3),
                          pytest.param(MultiLabelParameters.VALID_BATCH_SIZE * 3)]
                         )
def test_validation(dataset_size):
    num_labels = 2
    trainer = PytorchTrainer(MockBertClass, num_labels)
    model_parameters = next(trainer.model.l1.parameters()).data.clone()
    dataset = MockTextDataset(dataset_size, num_labels)
    outputs, _ = trainer.validate(dataset)

    # Assert training ran through entire data
    batch_size = MultiLabelParameters.VALID_BATCH_SIZE
    expected_steps = (dataset_size // batch_size) + ((dataset_size % batch_size) > 0)
    assert trainer.model.forward_called == expected_steps, "Expected steps to run through entire dataset wasn't met"

    # Assert model parameters were updated
    assert torch.equal(model_parameters, next(trainer.model.l1.parameters()).data), \
        "Validation updated model parameters, which is not expected"

    assert trainer.model.eval_called is True, "model.eval should be called before validation"
    assert len(outputs) == dataset_size
    assert len(outputs[0]) == 2


@unittest.skipIf(not has_torch, "torch not installed")
@pytest.mark.parametrize('dataset_size',
                         [pytest.param(10),
                          pytest.param(10000),
                          pytest.param(MultiLabelParameters.VALID_BATCH_SIZE // 2),
                          pytest.param(MultiLabelParameters.VALID_BATCH_SIZE + 3),
                          pytest.param(MultiLabelParameters.VALID_BATCH_SIZE * 3)]
                         )
def test_compute_metrics(dataset_size):
    num_labels = 2
    trainer = PytorchTrainer(MockBertClass, num_labels)
    dataset = MockTextDataset(dataset_size, num_labels)
    accuracy, f1_micro, f1_macro = trainer.compute_metrics(dataset)
    assert trainer.model.eval_called is True, "compute metrics should also run data validation in current flow"
    assert accuracy is not None
    assert f1_micro is not None
    assert f1_macro is not None


@unittest.skipIf(not has_torch, "torch not installed")
@pytest.mark.parametrize('mode',
                         [Split.train,
                          Split.test])
def test_sampler(mode):
    trainer = PytorchTrainer(MockBertClass, 2)
    sampler = trainer._data_sampler("some_dataset", mode)
    assert type(sampler) is RandomSampler
