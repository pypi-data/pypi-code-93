import time
import concurrent.futures
import json
from youtube_transcript_api import YouTubeTranscriptApi
from .step import Step
import logging

class GetVideoCaption(Step):
    def process(self, inputs, utils, data):
        logger = logging.getLogger('record')
        start = time.perf_counter()
        caption_pool = []
        for yt in data:
            path = yt.get_caption_filepath()
            if utils.check_caption_file_exist(path):
                logger.warning('Caption file existed for '+yt.id)
                caption = self.read_file(path)
                caption_after = self.reformat(caption)
                yt.caption = caption_after
                continue
            caption_pool.append(yt)

        with concurrent.futures.ThreadPoolExecutor(max_workers=30) as executor:
            executor.map(self.get_single_caption, caption_pool)

        end = time.perf_counter()
        logger.info(f'Caption downloading elapsed time:{round(end-start,2)} secs.')

        return data


    def write_to_file(self, caption, yt):
        path = yt.get_caption_filepath()
        with open(path, 'w', encoding='utf-8') as fp:
            for line in caption:
                fp.write(json.dumps(line)+'\n')

    def read_file(self,path):
        caption = []
        with open(path, 'r') as fp:
            for line in fp:
                caption.append(json.loads(line.rstrip('\n')))
        return caption

    def get_single_caption(self, yt):
        logger = logging.getLogger('record')
        try:
            logger.info('Downloading captions: '+ yt.id)
            caption = YouTubeTranscriptApi.get_transcript(yt.id)
            self.write_to_file(caption, yt)
            caption_after = self.reformat(caption)
            yt.caption = caption_after
        except:
            logger.warning('Caption is disabled for'+ yt.id)

    def reformat(self, caption):
        caption_after = {}
        for line in caption:
            caption_after[line["text"]] = [line["start"], line["duration"]]
        return caption_after



















