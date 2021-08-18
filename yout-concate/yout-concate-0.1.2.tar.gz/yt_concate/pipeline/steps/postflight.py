import os
import shutil
from .step import Step
from yt_concate.settings import CAPTION_DIR
from yt_concate.settings import VIDEO_DIR
import logging


class Postflight(Step):
    def process(self, inputs, utils, data):
        logger = logging.getLogger('record')
        if inputs['cleanup']:
            logger.info('In postflight')
            os.remove(utils.get_video_list_path(inputs["channel_id"]))
            shutil.rmtree(CAPTION_DIR)
            shutil.rmtree(VIDEO_DIR)
            logger.warning('All related downloading file has been removed.')
