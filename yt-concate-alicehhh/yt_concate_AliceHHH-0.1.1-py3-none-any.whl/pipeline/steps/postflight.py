from yt_concate.pipeline.steps.step import Step
from yt_concate.settings import DOWNLOADS_DIR


class Postflight(Step):
    def process(self, data, inputs, utils, log):
        log.info("Output video done!")
        if inputs["cleanup"]:
            utils.delete_files(DOWNLOADS_DIR)
            log.info("Downloaded files been deleted.")

        log.info("=== in Postflight ===")
