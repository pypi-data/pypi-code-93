#    Virtual-IPM is a software for simulating IPMs and other related devices.
#    Copyright (C) 2021  The IPMSim collaboration <https://ipmsim.gitlab.io/>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

import itertools as it
from threading import Event, Thread
import time


class Spinner(Thread):
    """Show a console animation in a separate thread."""

    def __init__(self, *, frequency=5, title=''):
        super().__init__()
        self._symbols = it.cycle(r'-\|/')
        self._stop_event = Event()
        self._wait = 1 / frequency
        self._title = title

    def __enter__(self):
        self.start()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

    def run(self):
        print(self._title, end='', flush=True)
        while not self._stop_event.is_set():
            print(f'\r{self._title}{next(self._symbols)}', end='', flush=True)
            time.sleep(self._wait)
        print(end='\n')

    def stop(self):
        self._stop_event.set()
        self.join()
