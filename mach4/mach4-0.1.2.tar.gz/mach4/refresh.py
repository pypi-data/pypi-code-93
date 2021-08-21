# -*- coding: utf-8 -*-
"""
Created on Wed Jan 20 20:36:02 2021

Copyright 2021 Cyriaque Perier

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from threading import Thread


class Refresh(Thread):

    """

    Loop a function in a separate thread

    """

    def __init__(self):

        """

        Initialise object

        """

        super().__init__()

        self.keep_alive = True
        self.functions = []

    def interrupt(self):

        """

        Stop running loop

        """

        self.keep_alive = False

    def run(self):

        """

        Separate thread

        """

        while self.keep_alive:

            functions = self.functions.copy()

            for function in functions:

                function()

    def add_function(self, function):

        """

        Add a function to the run list

        """

        self.functions.append(function)
