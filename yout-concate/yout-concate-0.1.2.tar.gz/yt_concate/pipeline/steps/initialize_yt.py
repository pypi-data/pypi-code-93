from .step import Step
from yt_concate.model.yt import Yt
import logging

class InitializeYt(Step):
    def process(self, inputs, utils, data):
        logger = logging.getLogger('record')
        logger.warning('creating YT objects')
        yts = [Yt(url) for url in data]
        return yts








