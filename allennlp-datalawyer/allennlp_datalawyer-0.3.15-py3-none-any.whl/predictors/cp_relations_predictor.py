from overrides import overrides

from allennlp.common.util import JsonDict
from allennlp_datalawyer.data.dataset_readers import BaseJsonReader
from allennlp_datalawyer.data.prepare_cp_data import convert_to_recorn_item
from allennlp.data import Instance
from allennlp.models import Model
from allennlp.predictors.predictor import Predictor


@Predictor.register('cp_relations_predictor')
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
            dataset_reader: BaseJsonReader
    ) -> None:
        super().__init__(model, dataset_reader)

    @overrides
    def _json_to_instance(self, json_dict: JsonDict) -> Instance:
        """
        Expects JSON that looks like `{"sentence": "..."}`.
        Runs the underlying model, and adds the `"words"` to the output.
        """
        assert 'relation' in json_dict
        cp_data_item = convert_to_recorn_item(json_dict, json_dict['relation'])
        cp_data_item['orig_id'] = json_dict['orig_id']
        cp_data_item['entities'] = json_dict['entities']
        return self._dataset_reader.text_to_instance(cp_data_item)
