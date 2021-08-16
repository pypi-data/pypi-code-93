import json
import logging
import os


class Manifest:
    __manifest = None

    def __init__(self):
        self.__load_manifest()

    def __load_manifest(self):
        logging.info("Load manifest - manifest.json")
        cwd = os.getcwd()
        with open(f"{cwd}/manifest.json") as file:
            self.__manifest = json.load(file)
            logging.info(self.__manifest)

    def get(self, key):
        return self.__manifest[key]

    def all(self, ):
        return self.__manifest


manifest = Manifest()
