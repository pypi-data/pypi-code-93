from collections import deque


class AutoSyncInputs:
    def __init__(self, max_queue_length, inputs_length):
        self.queue_list = [
            deque(maxlen=max_queue_length) for i in range(inputs_length)
        ]

    def stage(self, *args):
        for param_value in args:
            if param_value:
                index = args.index(param_value)
                self.queue_list[index].append(param_value)
        if all(self.queue_list):
            return tuple([q.popleft() for q in self.queue_list])
        else:
            return
