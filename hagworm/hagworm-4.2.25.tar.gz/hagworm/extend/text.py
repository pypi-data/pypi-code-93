# -*- coding: utf-8 -*-

import ahocorasick


class TextFinder:

    def __init__(self):

        self._automaton = ahocorasick.Automaton()

    def init_words(self, words):

        self._automaton.clear()

        for val in words:
            self._automaton.add_word(val, val)

        self._automaton.make_automaton()

    def find_all(self, content):

        return tuple(self._automaton.iter_long(content))

    def replace_all(self, content, _chars=r'*'):

        words = {item[1] for item in self.find_all(content)}

        for key in words:
            content = content.replace(key, _chars * len(key))

        return content
