import logging
from yt_concate.pipeline.steps.step import Step



class Preflight(Step):
    def process(self, inputs, utils, data):
        logger = logging.getLogger('record')
        logger.info('In preflight.')
        utils.create_downloads_dirs()
