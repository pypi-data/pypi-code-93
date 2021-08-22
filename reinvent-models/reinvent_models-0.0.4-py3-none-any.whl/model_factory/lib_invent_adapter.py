from reinvent_models.lib_invent.models.model import DecoratorModel
from reinvent_models.model_factory.generative_model_base import GenerativeModelBase


class LibInventAdapter(GenerativeModelBase):

    def __init__(self, path_to_file: str, mode: str):
        self._link_invent_model = DecoratorModel.load_from_file(path_to_file, mode)
        self.vocabulary = self._link_invent_model.vocabulary
        self.max_sequence_length = self._link_invent_model.max_sequence_length
        self.network = self._link_invent_model.network

    def load_from_file(self, path, mode="train"):
        return self._link_invent_model.load_from_file(path, mode=mode)

    def save_to_file(self, path):
        self._link_invent_model.save_to_file(path)

    def likelihood(self, scaffold_seqs, scaffold_seq_lengths, decoration_seqs, decoration_seq_lengths):
        return self._link_invent_model.likelihood(scaffold_seqs, scaffold_seq_lengths, decoration_seqs, decoration_seq_lengths)

    def sample(self, scaffold_seqs, scaffold_seq_lengths):
        return self._link_invent_model.sample_decorations(scaffold_seqs, scaffold_seq_lengths)
