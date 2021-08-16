from petrel.model import load_edet, load_optimizer
from torch.optim import Adam, AdamW, RMSprop, SGD

from unittest import TestCase


class TestOptimizer(TestCase):
    def test_adam(self):
        model = load_edet("tf_efficientdet_d0", image_size=512)
        optimizer = load_optimizer("adam", model, learning_rate=1e-2)
        assert optimizer.__class__ == Adam
        assert optimizer.param_groups[0]["lr"] == 1e-2
        assert optimizer.param_groups[0]["weight_decay"] == 0
        assert not optimizer.param_groups[0]["amsgrad"]

    def test_adamw(self):
        model = load_edet("tf_efficientdet_d0", image_size=512)
        optimizer = load_optimizer("adamw", model, learning_rate=1e-2)
        assert optimizer.__class__ == AdamW
        assert optimizer.param_groups[0]["lr"] == 1e-2
        assert optimizer.param_groups[0]["weight_decay"] == 4e-5
        assert not optimizer.param_groups[0]["amsgrad"]

    def test_rmsprop(self):
        model = load_edet("tf_efficientdet_d0", image_size=512)
        optimizer = load_optimizer("rmsprop", model, learning_rate=1e-2)
        assert optimizer.__class__ == RMSprop
        assert optimizer.param_groups[0]["lr"] == 1e-2
        assert optimizer.param_groups[0]['momentum'] == 0.9
        assert optimizer.param_groups[0]["weight_decay"] == 0

    def test_sgd(self):
        model = load_edet("tf_efficientdet_d0", image_size=512)
        optimizer = load_optimizer("sgd", model, learning_rate=1e-2)
        assert optimizer.__class__ == SGD
        assert optimizer.param_groups[0]["lr"] == 1e-2
        assert optimizer.param_groups[0]['momentum'] == 0.9
        assert optimizer.param_groups[0]["weight_decay"] == 0
