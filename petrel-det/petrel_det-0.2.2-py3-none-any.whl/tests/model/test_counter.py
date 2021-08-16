from unittest import TestCase
from petrel.model import AvgCounter


class TestCounter(TestCase):
    def test_counter(self):
        avg_counter = AvgCounter()
        avg_counter.update(2, 1)
        avg_counter.update(3, 1)
        avg_counter.update(1, 1)
        assert avg_counter.avg == 2.0
        assert avg_counter.sum == 6.0
        assert avg_counter.count == 3
        avg_counter.update(2, 1)
        assert avg_counter.avg == 2.0
        assert avg_counter.sum == 8.0
        assert avg_counter.count == 4
        avg_counter.update(7, 1)
        assert avg_counter.avg == 3.0
        assert avg_counter.sum == 15.0
        assert avg_counter.count == 5
        avg_counter.reset()
        assert avg_counter.sum == 0.0
        assert avg_counter.count == 0

    def test_avg_counter(self):
        avg_counter = AvgCounter()
        avg_counter.update_avg(2, 2)
        assert avg_counter.avg == 2.0
        assert avg_counter.sum == 4.0
        assert avg_counter.count == 2
        avg_counter.update_avg(3, 3)
        assert avg_counter.avg == 2.6
        assert avg_counter.sum == 13.0
        assert avg_counter.count == 5
        avg_counter.update_avg(8, 1)
        assert avg_counter.avg == 3.5
        assert avg_counter.sum == 21.0
        assert avg_counter.count == 6

    def test_variable_count(self):
        avg_counter = AvgCounter()
        avg_counter.update(2, 2)
        assert avg_counter.avg == 1.0
        assert avg_counter.sum == 2.0
        assert avg_counter.count == 2
        avg_counter.update(3, 3)
        assert avg_counter.avg == 1.0
        assert avg_counter.sum == 5.0
        assert avg_counter.count == 5
        avg_counter.update(7, 1)
        assert avg_counter.avg == 2.0
        assert avg_counter.sum == 12.0
        assert avg_counter.count == 6
