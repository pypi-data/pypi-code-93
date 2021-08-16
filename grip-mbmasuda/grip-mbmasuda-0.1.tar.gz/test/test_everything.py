"""
pytest unit tests
"""
import random
import threading
import time

import pytest

from src.grip.grip import (
    GenericItem,
    GenericRateLimitedItemProcessor,
    GRIP_Deque
)


VALID = 'valid'
INVALID = 'invalid'
THREAD = 'thread'

# each tuple contains the num_items, num_seconds
RATE_LIMITING_TEST_DATA = [
    (100, 1),
    (3, 1.98324729923487),
    (2344, 0.3)
]


class ValidItem:
    def __init__(self, who_cares):
        self.data = who_cares

    def get_data(self):
        return self.data

    def start(self):
        pass


class InvalidItem:
    # this is an invalid item because it does not implement a callable start()
    def __init__(self, who_cares):
        self.data = who_cares

    def get_data(self):
        return self.data


class ThreadItem(threading.Thread):
    # this is not a subclass of GenericItem and does not implement its own
    # start() but it should be recognized as a generic item and work because
    # it is a subclass of threading.Thread and thus has a start() in its MRO
    def __init__(self, who_cares):
        super().__init__(daemon=True)
        self.data = who_cares

    def get_data(self):
        return self.data

    def run(self):
        start_time = time.time()
        time.sleep(random.random() * 5)
        stop_time = time.time()
        elapsed_time = stop_time - start_time
        return start_time, stop_time, elapsed_time


class SimplestPossibleItemThatCanBeProcessed:
    def start(self):
        pass


class NumberItem:
    def start(self):
        return 42


class SayHiItem:
    def start(self):
        return 'hi!'


class TestPorcelain:
    def test_make_new_instances(self):
        # make sure the CallableStartMetaclass implementation does not
        # have some fatal flaw that prevents an object from being created
        valid = ValidItem(VALID)
        invalid = InvalidItem(INVALID)
        assert valid.get_data() == VALID
        assert invalid.get_data() == INVALID

    def test_isinstance_works_correctly(self):
        # make sure the CallableStartMetaclass implementation of __instancecheck__
        # is working correctly
        valid = ValidItem(VALID)
        invalid = InvalidItem(INVALID)
        thread = ThreadItem(THREAD)
        assert isinstance(valid, GenericItem)
        assert isinstance(thread, GenericItem)
        assert not isinstance(invalid, GenericItem)

    def test_simplest_possible_item_that_can_be_processed(self):
        # this example is used in the README.md
        x = SimplestPossibleItemThatCanBeProcessed()
        grip = GenericRateLimitedItemProcessor(iterable=[x])
        grip.start()
        grip.join()
        assert 1 == len(grip.successfully_started)

    def test_mixed_and_matched_items(self):
        # this example is used in the README.md
        items = [NumberItem() for x in range(5)] + [SayHiItem() for x in range(5)]
        grip = GenericRateLimitedItemProcessor(iterable=items)
        grip.start()
        grip.join()
        assert 10 == len(grip.successfully_started)

    def test_valid_items_can_be_processed(self):
        valid_items = [ValidItem(i) for i in range(5)]
        thread_items = [ThreadItem(i) for i in range(5)]
        all_items = valid_items + thread_items
        grip = GenericRateLimitedItemProcessor(iterable=all_items)
        grip.start()

    @pytest.mark.parametrize("num_items, num_seconds", RATE_LIMITING_TEST_DATA)
    def test_rate_limiting_works(self, num_items, num_seconds):
        thread_items = [ThreadItem(i) for i in range(num_items)]
        grip = GenericRateLimitedItemProcessor(iterable=thread_items,
                                               num_items=num_items,
                                               num_seconds=num_seconds)
        grip.start()
        grip.join()
        # make sure start() was called on the expected number of items after
        # waiting for the grip thread to finish execution
        assert num_items == len(grip.successfully_started)


GRIP_DEQUE_TEST_DATA = [
    ([], None),  # no initial iterable, unbounded
    ([], 4),  # no initial iterable, bounded with maxlen of 4
    ([1, 2, 3], None),  # initial iterable, unbounded
    ([1, 2, 3, 4], 7),  # initial iterable is a list, bounded with maxlen of 7
    (('x', 'y', 'z'), 3),  # initial iterable is a tuple, bounded with maxlen of 3
    ('abcdefg', None)  # strings are iterables so check them as well, unbounded
]


class TestPlumbing:
    @pytest.mark.parametrize("iterable_data, maxlen", GRIP_DEQUE_TEST_DATA)
    def test_make_new_instance(self, iterable_data, maxlen):
        x = GRIP_Deque(iterable=iterable_data, maxlen=maxlen)
        assert x.maxlen == maxlen
        assert len(x) == len(iterable_data)

    @pytest.mark.parametrize("iterable_data, maxlen", GRIP_DEQUE_TEST_DATA)
    def test_get_next_item(self, iterable_data, maxlen):
        x = GRIP_Deque(iterable=iterable_data, maxlen=maxlen)
        counter = 0
        while True:
            try:
                actual = x.get_next_item()
                expected = iterable_data[counter]
                assert actual == expected
                counter += 1
            except IndexError:
                # make sure all items were obtained
                assert len(iterable_data) == counter
                return

    @pytest.mark.parametrize("iterable_data, maxlen", GRIP_DEQUE_TEST_DATA)
    def test_append_item(self, iterable_data, maxlen):
        # reuse GRIP_DEQUE_TEST_DATA because I am lazy but we do not
        # make use of the maxlen from the parametrized data in this test
        x = GRIP_Deque()
        for item in iterable_data:
            x.append_item(item)

        counter = 0
        while True:
            try:
                actual = x.get_next_item()
                expected = iterable_data[counter]
                assert actual == expected
                counter += 1
            except IndexError:
                # make sure all items were appended to x
                assert len(iterable_data) == counter
                return
