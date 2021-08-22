from reinvent_models.model_factory.enums.model_mode_enum import ModelModeEnum
from reinvent_models.model_factory.generative_model_base import GenerativeModelBase
from reinvent_models.reinvent_core.models.model import Model


class ReinventCoreAdapter(GenerativeModelBase):

    def __init__(self, path_to_file: str, mode: str):
        self._reinvent_model = Model.load_from_file(path_to_file, mode)
        self.vocabulary =  self._reinvent_model.vocabulary
        self.tokenizer =  self._reinvent_model.tokenizer
        self.max_sequence_length =  self._reinvent_model.max_sequence_length
        self.network =  self._reinvent_model.network
        # self._nll_loss =  self._reinvent_model._nll_loss

    def load_from_file(self, path, mode=ModelModeEnum().TRAINING):
        model_mode = ModelModeEnum()
        mode = mode == model_mode.INFERENCE
        return self._reinvent_model.load_from_file(path, mode=mode)

    def save_to_file(self, path):
        self._reinvent_model.save(path)

    def likelihood(self, sequences):
        return self._reinvent_model.likelihood(sequences)

    def sample(self, num, batch_size):
        return self._reinvent_model.sample_smiles(num, batch_size)