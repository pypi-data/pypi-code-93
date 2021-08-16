from collections import deque
import logging
import sys
import threading
import time

from src.grip.metaclasses import (
    CallableStartMetaclass,
    ThreadSafeSingleton
)


# minimum representable positive normalized float
MIN_FLOAT = sys.float_info.min


class GRIP_Deque(deque):
    """
    The GRIP_Deque encapsulates a domain-specific deque and its behavior
    """
    def __init__(self, iterable=[], maxlen=None):
        """
        Params:
        * iterable (any iterable): Optionally provide the data to use to initialize this deque.
        * maxlen (int): Optionally indicate the maximum number of items that this instance's deque can hold
            at one time. If maxlen is None, this instance can hold an unbounded number of items to be processed.
            If this instance is bounded, then only maxlen number of items can be waiting to be processed, but
            this maxlen limit does not prevent more items from being added to the deque later; this can be
            useful if the items to be processed are resource intensive and you want to prevent out-of-memory
            issues or whatever because it will prevent too many things from being queued up and consuming
            resources while waiting to be processed.
        """
        super().__init__(iterable, maxlen)

    def get_next_item(self):
        """
        Returns the next item in the deque. Override this method to change from the default queue behavior
        to stack behavior by changing popleft() to pop().

        This will raise an IndexError if the deque is empty. Any exceptions should be handled by the code
        that calls this method, not inside this method.
        """
        return self.popleft()

    def append_item(self, item):
        """
        Append the item to the deque. Override this by changing append() to appendleft() if you require
        different behavior than the default queue-like FIFO.
        """
        self.append(item)


class GenericRateLimitedItemProcessor(threading.Thread, metaclass=ThreadSafeSingleton):
    """
    This thread-safe singleton processes items in a rate-limited manner once you call its start() method
    """
    def __init__(self,
                 iterable=[],
                 maxlen=None,
                 num_items=None,
                 num_seconds=None,
                 name=None,
                 daemon=None):
        """
        Params:
        * iterable (any iterable): Optionally provide the data to use to initialize this deque.
        * maxlen (int): Optionally indicate the maximum number of items that this instance's deque of items to
            process can hold at one time. If maxlen is None, this instance can hold an unbounded number of items.
            If this instance is bounded, then only maxlen number of items can be waiting to be processed, but
            this maxlen limit does not prevent more items from being added to the deque later.
        * num_items (int): Optionally indicate the number of items to process in num_seconds.
            If num_items is None, then the items are processed as fast as possible with no rate limiting.
            If num_items is a positive integer, then that number of items will be processed in num_seconds
            in an evenly distributed manner.
        * num_seconds (int or float): Optionally indicate the number of seconds in which to process num_items.
        * name (string): Optionally name this thread.
        * daemon (boolean): Optionally explicitly set whether this item processor is daemonic. If this is
            left as None, the thread inherits its daemonic property from the current thread.
        """
        super().__init__(name=name, daemon=daemon)
        self.items_to_process = GRIP_Deque(iterable=iterable, maxlen=maxlen)
        self.successfully_started = GRIP_Deque()
        self.unsuccessfully_started = GRIP_Deque()

        # default sleep time is 0 seconds, meaning items will be processed as quickly as possible
        self.sleep_time = 0
        # if num_items is a positive int and num_seconds is a positive int or float,
        # calculate the amount of time to sleep between processing items by dividing
        # num_seconds by num_items. For example, if you want to process 100 items in
        # 1 second, then the sleep time between items will be 0.01 seconds (100 / 1)
        if (num_items is not None and num_seconds is not None) \
           and isinstance(num_items, int) \
           and isinstance(num_seconds, (int, float)) \
           and num_items > 0 \
           and num_seconds > 0:
            self.sleep_time = num_seconds / num_items

    def run(self):
        """
        Because this is an instance of threading.Thread, we need to define a run() method so when start()
        is called to kick off the processing, something actually happens.
        """
        while True:
            try:
                item = self.items_to_process.get_next_item()

                try:
                    item.start()
                    self.successfully_started.append_item(item)
                except Exception:
                    logging.exception(f'The item {item} could not be processed and was moved '
                                      f'to the unsuccessfully_started deque for later examination.')
                    self.unsuccessfully_started.append_item(item)

                # this is how the rate limiting happens
                time.sleep(self.sleep_time)

            # If the items_to_process deque is empty when the next item
            # is requested, the deque will raise an IndexError so if
            # this happens, we return to cause the thread to finish running
            except IndexError:
                return


class GenericItem(metaclass=CallableStartMetaclass):
    """
    This class definition exists in order to have a non-abstract class that uses the CallableStartMetaclass

    No actual implementation is needed since the only thing we need this class for is to
    use it for type checking with a call to isinstance(thing, GenericItem) to ensure thing
    implements a start() method
    """
    pass
