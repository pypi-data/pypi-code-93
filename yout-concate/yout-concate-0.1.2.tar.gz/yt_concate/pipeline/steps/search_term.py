from .step import Step
from yt_concate.model.found import Found
import logging

class Search(Step):
    def process(self, inputs, utils, data):
        logger = logging.getLogger('record')
        logger.info('Search for corresponded search term...')
        search_term = inputs["search_term"]
        founds = []
        for yt in data:
            caption = yt.caption
            if caption:
                for caption_key in caption:
                    if search_term in caption_key:
                        founds.append(Found(yt, caption_key, caption[caption_key]))
        return founds







