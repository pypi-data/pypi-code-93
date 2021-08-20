class KeyCounter:

    def __init__(self, counts=None):
        if isinstance(counts, dict) or counts is None:
            self.counts = {} if counts is None else counts
        else:
            raise ValueError("Keys to count must be either list of strings or string.")

    def _increase(self, key):
        if key not in self.counts:
            self.counts[key] = 0
        self.counts[key] += 1

    def count(self, key):
        if not isinstance(key, list) and not isinstance(key, str):
            raise ValueError("Keys to count must be either list of strings or string {} given".format(type(key)))

        if isinstance(key, list):
            for k in key:
                self._increase(k)
        else:
            self._increase(key)
