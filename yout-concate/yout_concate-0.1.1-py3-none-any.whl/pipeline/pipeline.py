

class Pipeline:

    def __init__(self, steps):
        self.steps = steps

    def run(self, inputs, utils):
        data = None
        for step in self.steps:
            try:
                data = step.process(inputs, utils, data)
            except:
                print('Error happening in step process.')












