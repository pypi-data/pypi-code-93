from unittest import TestCase
from petrel.model import LossCounter


class TestLoss(TestCase):
    def test_counter(self):
        loss = LossCounter()
        loss.update({"loss": 5, "class_loss": 2, "box_loss": 1}, batch_size=1)
        loss.update({"loss": 10, "class_loss": 4, "box_loss": 2}, batch_size=2)
        assert loss.avg == 5.0
        assert loss.class_avg == 2.0
        assert loss.box_avg == 1.0
        loss.update({"loss": 19, "class_loss": 34, "box_loss": 16}, batch_size=2)
        assert loss.avg == 6.8
        assert loss.class_avg == 8.0
        assert loss.box_avg == 3.8

    def test_avg_counter(self):
        loss = LossCounter()
        loss.update_avg({"loss": 5, "class_loss": 2, "box_loss": 1}, batch_size=1)
        loss.update_avg({"loss": 5, "class_loss": 2, "box_loss": 1}, batch_size=2)
        assert loss.avg == 5.0
        assert loss.class_avg == 2.0
        assert loss.box_avg == 1.0
        loss.update_avg({"loss": 19, "class_loss": 34, "box_loss": 16}, batch_size=2)
        assert loss.avg == 10.6
        assert loss.class_avg == 14.8
        assert loss.box_avg == 7.0
