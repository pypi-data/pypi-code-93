import typing as tp

from weak_postagger.logic import ListWeakModel, RuleBasedDisambiguation, PipelineWeakModels


class WeakPOSTagging:
    """
        This class utilizes weak modeling to give Part of Speech tag (POS Tag) to words in a sentence.
        
        It uses labeling steps and correction steps in order to arrive at more accurate labels.
        In order to use this class it is necessary to give it a set of files with lists of words for each POS Tag,
        as described in the ReadME.
        
        Methods:
        --------
        * label_sentence : Labels a sentence's words with its corresponding POS Tags.
        * clear_pipeline : Clears the labeling steps utilized on the pipeline.
        * add_pipeline_step : Adds a labeling step on the pipeline.
        
        Attributes:
        --------
        * pipeline: Labeling pipeline being used. It initializes with two default steps:
        The first step is the labeling module `ListWeakModel` created with the files input in the class.
        The second step is the label correction module `RuleBasedDisambiguation`.
    """
    def __init__(self, directory_path: str, use_preprocess: bool = True, pre_processing_options: tp.List[str] = []):
        """
            Initializes the class by reading the word list files and instantiating the pipeline and its steps.

            Possible pre processing options are EMAIL, URL, NUMBER and CODE.

        :param directory_path: Directory containing files to be read.
        :type directory_path: `str`
        :param use_preprocess: Flags whether text pre processing should be used. Defaults to true.
        :type use_preprocess: `bool`
        :param pre_processing_options: Optional pre processing options to be applied. Defaults to basic pre processing.
        :type pre_processing_options: `tp.List[str]`
        """
        self.__list_based_model = ListWeakModel(directory_path=directory_path,
                                                use_preprocess=use_preprocess,
                                                pre_processing_options=pre_processing_options)
        self.__rule_correction_model = RuleBasedDisambiguation()
        self.pipeline = self.__create_default_pipeline()
        
    def __create_default_pipeline(self) -> PipelineWeakModels:
        """ Creates the default pipeline with two steps.
        
        The first step is the labeling module `ListWeakModel` created with the files input in the class.
        The second step is the label correction module `RuleBasedDisambiguation`.
        
        :return: Weak labeling pipeline.
        :rtype: `PipelineWeakModels`
        """
        pipeline = PipelineWeakModels([ListWeakModel], [RuleBasedDisambiguation])
        pipeline.add_pipeline_step(self.__list_based_model)\
            .add_pipeline_step(self.__rule_correction_model)
        return pipeline
    
    def label_sentence(self, sentence: str) -> tp.Tuple[str, str]:
        """ Labels a sentence with its part of speech labels based on the labeling and correction steps of the pipeline.
        
        :param sentence: Sentence to be labeled.
        :type sentence: `str`
        :return: A tuple with the preprocessed sentence and the labels for the words on the sentence.
        :rtype: `tp.Tuple[str, str]`
        """
        return self.pipeline.predict_labels(sentence)

    def clear_pipeline(self):
        """ Clears the labeling steps utilized on the pipeline. """
        self.pipeline.clear_pipeline()
    
    def add_pipeline_step(self, labeling_step: tp.Any):
        """
            Adds a labeling step on the pipeline.

        :param labeling_step: Labeling step to be added to pipeline.
        :type labeling_step: `tp.Any`
        """
        self.pipeline.add_pipeline_step(labeling_step)
