import typing as tp


class PipelineWeakModels:
    """
        Class responsible for constructing a labeling pipeline utilizing the weak labeling systems.
        It uses the list based labeling followed by the disambiguation rules to correct ambiguous labels.

        Methods:
        --------
        * add_pipeline_step : Adds a labeling step on the pipeline.
        * predict_labels : Applies the pipeline steps to label a sentence.
        * clear_pipeline : Clears the labeling steps utilized on the pipeline.
        
        Attributes:
        --------
        * pipeline: List of steps to be applied in the pipeline.

    """
    
    def __init__(self, valid_labeling_steps: tp.List[tp.Any], valid_correction_steps: tp.List[tp.Any]):
        """
            Initializes the class informing what are the valid pipeline steps for labeling and correction.
            
        :param valid_labeling_steps: Valid labeling systems to use on the pipeline.
        :type valid_labeling_steps: `tp.List[tp.Any]`
        :param valid_correction_steps: Valid labeling correction systems to use on the pipeline.
        :type valid_correction_steps: `tp.List[tp.Any]`
        """
        self.pipeline = []
        self.__valid_labeling_steps = tuple(valid_labeling_steps)
        self.__valid_correction_steps = tuple(valid_correction_steps)
        self.__valid_steps = self.__valid_labeling_steps + self.__valid_correction_steps

    def add_pipeline_step(self, labeling_step: tp.Any):
        """
            Adds a labeling step on the pipeline.

        :param labeling_step: Labeling step to be added to pipeline.
        :type labeling_step: `tp.Any`
        """
        if not isinstance(labeling_step, self.__valid_steps):
            raise Exception(f'{labeling_step} is not a valid labeling step.')
    
        if len(self.pipeline) == 0:
            self.__add_first_step(labeling_step)
        else:
            self.pipeline.append(labeling_step)
        return self

    def predict_labels(self, sentence: str) -> tp.Tuple[str, str]:
        """
            Labels a sentence with its part of speech labels based on the labeling and correction steps of the pipeline.
            
        :param sentence: Sentence to be labeled.
        :type sentence: `str`
        :return: A tuple with the preprocessed sentence and the labels for the words on the sentence.
        :rtype: `tp.Tuple[str, str]`
        """
        labels = ''
        for step in self.pipeline:
            if isinstance(step, self.__valid_labeling_steps):
                sentence, labels = step.label_message(sentence)
            elif isinstance(step, self.__valid_correction_steps):
                sentence, labels = step.label_disambiguation(sentence, labels)
        return sentence, labels

    def clear_pipeline(self):
        """ Clears the labeling steps utilized on the pipeline. """
        self.pipeline = []

    def __add_first_step(self, labeling_system: tp.Any):
        """
            Adds first step to the pipeline while checking if it is a labeling step.
            
        :param labeling_system: Labeling systems to use on the pipeline.
        :type labeling_system: `tp.Any`
        """
        if isinstance(labeling_system, self.__valid_labeling_steps):
            self.pipeline.append(labeling_system)
        else:
            raise Exception(f'First step should be a labeling one, but received a step of type {type(labeling_system)}')
