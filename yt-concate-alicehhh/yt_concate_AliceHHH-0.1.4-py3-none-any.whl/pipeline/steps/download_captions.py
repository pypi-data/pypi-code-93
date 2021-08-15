import time
from concurrent.futures import ThreadPoolExecutor
from pytube import YouTube

from .step import Step
from yt_concate.settings import CAPTIONS_DIR


class DownloadCaptions(Step):
    def process(self, data, inputs, utils, log):
        log.info("=== Downloading captions... ===")
        start = time.time()

        yt_ = []
        for yt in data:
            if inputs["fast"]:
                if utils.caption_file_exists(yt):
                    log.info(f"Found existing caption file: {yt.id}, skipping.")
                    continue
                else:
                    yt_.append(yt)
            else:
                yt_.append(yt)

        if len(yt_) > 0:
            log.info(f"{len(yt_)} captions to be downloaded.")
            with ThreadPoolExecutor(max_workers=inputs["thread"]) as executor:
                for yt in yt_:
                    executor.submit(self.download_captions, yt, log)

        end = time.time()

        captions_amount = utils.file_amount(CAPTIONS_DIR)
        log.info(f"Captions downloaded: Took {round(end-start, 2)} secs.")
        log.info(f"{captions_amount} caption files in folder: {CAPTIONS_DIR}.")
        return data

    @staticmethod
    def download_captions(yt, log):
        try:
            source = YouTube(yt.url)
            en_caption = source.captions['en']
            en_caption_convert_to_srt = en_caption.generate_srt_captions()

            text_file = open(yt.caption_filepath, "w", encoding="utf-8")
            text_file.write(en_caption_convert_to_srt)
            text_file.close()
            log.debug(f"Caption downloading done: {yt.id}")
        except (KeyError, AttributeError):
            log.error(f"Error when downloading caption: {yt.url}")
