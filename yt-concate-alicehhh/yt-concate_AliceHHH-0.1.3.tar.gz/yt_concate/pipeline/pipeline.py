from .steps.step import StepException


class Pipeline:
    def __init__(self, steps):
        self.steps = steps

    def run(self, inputs, utils, log):
        data = None
        for step in self.steps:
            try:
                data = step.process(data, inputs, utils, log)
            except StepException as e:
                print("Exception happened:", e)
