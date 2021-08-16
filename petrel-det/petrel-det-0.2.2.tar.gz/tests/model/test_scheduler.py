import numpy as np

from petrel.model import load_edet, load_optimizer, load_scheduler

from unittest import TestCase


class MyTestCase(TestCase):
    def test_scheduler(self):
        model = load_edet("tf_efficientdet_d0", image_size=512)
        optimizer = load_optimizer("adam", model, learning_rate=1e-2)
        scheduler = load_scheduler("exponential", optimizer=optimizer)
        assert scheduler.gamma == 1.0
        assert scheduler.get_last_lr()[0] == 1e-2
        optimizer.step()
        scheduler.step()
        assert scheduler.get_last_lr()[0] == 1e-2

    def test_exponential(self):
        model = load_edet("tf_efficientdet_d0", image_size=512)
        optimizer = load_optimizer("adam", model, learning_rate=1e-2)
        scheduler = load_scheduler("exponential", optimizer=optimizer, gamma=0.9)
        assert scheduler.gamma == 0.9
        assert scheduler.get_last_lr()[0] == 1e-2
        optimizer.step()
        scheduler.step()
        assert np.round(scheduler.get_last_lr()[0], 3) == 9e-3
        optimizer.step()
        scheduler.step()
        assert np.round(scheduler.get_last_lr()[0], 4) == 8.1e-3

    def test_mult(self):
        model = load_edet("tf_efficientdet_d0", image_size=512)
        optimizer = load_optimizer("adam", model, learning_rate=1e-2)
        scheduler = load_scheduler("mult", optimizer=optimizer, lr_lambda=lambda epoch: 0.9)
        assert scheduler.get_last_lr()[0] == 1e-2
        optimizer.step()
        scheduler.step()
        assert np.round(scheduler.get_last_lr()[0], 3) == 9e-3
        optimizer.step()
        scheduler.step()
        assert np.round(scheduler.get_last_lr()[0], 4) == 8.1e-3

    def test_cosine(self):
        model = load_edet("tf_efficientdet_d0", image_size=512)
        optimizer = load_optimizer("adam", model, learning_rate=1e-2)
        scheduler = load_scheduler("cosine",
                                   optimizer=optimizer,
                                   T_max=100,
                                   eta_min=0)
        assert scheduler.get_last_lr()[0] == 1e-2
        optimizer.step()
        scheduler.step()
        assert scheduler.get_last_lr()[0] == 0.009997532801828659
        optimizer.step()
        scheduler.step()
        assert np.round(scheduler.get_last_lr()[0], 7) == 0.0099901