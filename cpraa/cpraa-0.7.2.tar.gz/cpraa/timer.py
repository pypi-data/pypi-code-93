import time


class Timer:

    all_timers = []
    enable_printing_default = True
    decimal_places_default = 3

    def __init__(self, start=True, output_string="Elapsed time:", enable_printing=None, decimal_places=None):
        self._start_time = None
        self._stop_time = None
        self.last_timing = None

        self.output_string = output_string

        if enable_printing is None:
            self.enable_printing = self.enable_printing_default
        else:
            self.enable_printing = enable_printing
        if decimal_places is None:
            decimal_places = self.decimal_places_default
        self.format_string = "{:." + str(decimal_places) + "f} seconds"

        self.all_timers.append(self)

        if start:
            self.start()

    def start(self):
        """Starts the timer"""
        self._start_time = time.perf_counter()

    def stop(self):
        """Stops the timer and returns the elapsed time in seconds"""
        self._stop_time = time.perf_counter()
        self.last_timing = self._stop_time - self._start_time
        if self.enable_printing:
            print(self.output_string, self.format_string.format(self.last_timing))
        return self.last_timing
