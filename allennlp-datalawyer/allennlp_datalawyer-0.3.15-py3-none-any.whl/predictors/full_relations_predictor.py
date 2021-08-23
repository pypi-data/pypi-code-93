from overrides import overrides

from allennlp.common.util import JsonDict
from allennlp.data import DatasetReader, Instance
from allennlp.models import Model
from allennlp.predictors.predictor import Predictor


@Predictor.register('full_relations_predictor')
class RelationsPredictor(Predictor):
    """
        Predictor for any model that takes in a sentence and returns
        a single set of tags for it.  In particular, it can be used with
        the [`CrfTagger`](https://docs.allennlp.org/models/master/models/tagging/models/crf_tagger/)
        model and also the [`SimpleTagger`](../models/simple_tagger.md) model.

        Registered as a `Predictor` with name "sentence_tagger".
        """

    def __init__(
            self,
            model: Model,
            dataset_reader: DatasetReader
    ) -> None:
        super().__init__(model, dataset_reader)

    @overrides
    def _json_to_instance(self, json_dict: JsonDict) -> Instance:
        """
        Expects JSON that looks like `{"sentence": "..."}`.
        Runs the underlying model, and adds the `"words"` to the output.
        """
        sentence = self._dataset_reader._parse_sentence(json_dict)
        context = json_dict['tokens']
        tokenized_context = self._dataset_reader.tokenizer.tokenize(' '.join(context))
        return self._dataset_reader.text_to_instance(context=context,
                                                     tokenized_context=tokenized_context,
                                                     entities=sentence.entities,
                                                     relations=sentence.relations)
