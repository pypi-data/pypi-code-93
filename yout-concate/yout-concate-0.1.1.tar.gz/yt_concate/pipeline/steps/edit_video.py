import os
from moviepy.editor import VideoFileClip
from moviepy.editor import concatenate_videoclips
from .step import Step
from yt_concate.settings import OUTPUT_DIR
import logging


class EditVideo(Step):
    def process(self, inputs, utils, data):
        logger = logging.getLogger('record')
        logger.warning('Editing final video...')
        clips = []
        if inputs['limit'] > len(data):
            limit = len(data)
        else:
            limit = inputs['limit']
        for found in data[:limit]:
            s, e = self.parse_clip_time(found)
            try:
                clips.append(VideoFileClip(found.yt.get_video_filepath()).subclip(s, e))
            except:
                logger.error('Error happened while clip video:'+ found.yt.id)
        final_clip = concatenate_videoclips(clips)
        final_clip.write_videofile(os.path.join(OUTPUT_DIR, inputs["channel_id"]+'.mp4'))
        return


    def parse_clip_time(self,found):
        start = found.caption_time[0]
        end = found.caption_time[0] + found.caption_time[1]
        return start, end
