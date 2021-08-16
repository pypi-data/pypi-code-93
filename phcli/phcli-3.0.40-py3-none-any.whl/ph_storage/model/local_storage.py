# -*- coding: utf-8 -*-

import os


class PhLocalStorage:

    def remove(self, path):
        try:
            os.remove(path)
        except IOError:
            return False
        else:
            return True

    def createDir(self, path):
        try:
            if not os.path.exists(path):
                print("create path ", path)
                os.makedirs(path)
        except IOError:
            return ""
        else:
            return path
