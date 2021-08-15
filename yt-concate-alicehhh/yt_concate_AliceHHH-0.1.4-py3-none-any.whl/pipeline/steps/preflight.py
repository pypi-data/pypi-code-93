from yt_concate.pipeline.steps.step import Step


class Preflight(Step):
    def process(self, data, inputs, utils, log):
        log.info("=== in Preflight ===")
        utils.create_dirs()
