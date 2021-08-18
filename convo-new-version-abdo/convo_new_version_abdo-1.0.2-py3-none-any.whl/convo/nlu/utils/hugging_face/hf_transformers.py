import logging
from typing import Any, Dict, List, Text, Tuple, Optional

from convo.core.utils import get_dict_hash
from convo.nlu.model import Metadataset
from convo.nlu.tokenizers.whitespace_tokenizer import WhitespaceTokenizer
from convo.nlu.components import Element
from convo.nlu.config import ConvoNLUModelConfiguration
from convo.shared.nlu.training_data.training_data import TrainingDataSet
from convo.shared.nlu.training_data.message import Msg
from convo.nlu.tokenizers.tokenizer import Tkn
import convo.utils.train_utils as train_utils
import numpy as np

from convo.nlu.constants import (
    LANG_MODEL_DOCUMENTS,
    DENSE_FEATURE_ATTRS,
    TKN_IDS,
    TKNS,
    SENTENCE_FTRS,
    SEQUENTIAL_FEATURES,
    SUB_TOKENS_NUM,
    NO_LEN_RESTRICT,
)
from convo.shared.nlu.constants import TXT, ACT_TEXT

SEQ_MAX_LENGTH = {
    "bert": 512,
    "gpt": 512,
    "gpt2": 512,
    "xlnet": NO_LEN_RESTRICT,
    "distilbert": 512,
    "roberta": 512,
}

log = logging.getLogger(__name__)


class HF_Transformers_NLP(Element):
    """Utility Element for interfacing between Transformers library and Convo OS.

    The transformers(https://github.com/huggingface/transformers) library
    is used to load pre-trained language models like BERT, GPT-2, etc.
    The component also tokenizes and featurizes dense featurizable attributes of each
    message.
    """

    defaults = {
        # name of the language model to load.
        "model_name": "bert",
        # Pre-Trained weights to be loaded(string)
        "model_weights": None,
        # an optional path to a specific dir to download
        # and cache the pre-trained model weights.
        "cache_dir": None,
    }

    def __init__(
        self,
        component_config: Optional[Dict[Text, Any]] = None,
        skip_model_load: bool = False,
    ) -> None:
        super(HF_Transformers_NLP, self).__init__(component_config)

        self._load_meta_data_model()
        self._load_instance_model(skip_model_load)
        self.whitespace_tokenizer = WhitespaceTokenizer()

    def _load_meta_data_model(self) -> None:

        from convo.nlu.utils.hugging_face.registry import (
            model_class_dictionary,
            model_wt_defaults,
        )

        self.model_name = self.component_config["model_name"]

        if self.model_name not in model_class_dictionary:
            raise KeyError(
                f"'{self.model_name}' not a valid model name. Choose from "
                f"{str(list(model_class_dictionary.keys()))} or create"
                f"a new class inheriting from this class to support your model."
            )

        self.model_weights = self.component_config["model_weights"]
        self.cache_dir = self.component_config["cache_dir"]

        if not self.model_weights:
            log.info(
                f"Model weights not specified. Will choose default model weights: "
                f"{model_wt_defaults[self.model_name]}"
            )
            self.model_weights = model_wt_defaults[self.model_name]

        self.max_model_sequence_length = SEQ_MAX_LENGTH[self.model_name]

    def _load_instance_model(self, skip_model_load: bool) -> None:
        """Try loading the model instance

        Args:
            skip_model_load: Skip loading the model instances to save time. This should be True only for pytests
        """

        if skip_model_load:
            # This should be True only during pytests
            return

        from convo.nlu.utils.hugging_face.registry import (
            model_class_dictionary,
            model_tokenizer_dictionary,
        )

        log.debug(f"Loading Tokenizer and Model for {self.model_name}")

        self.tokenizer = model_tokenizer_dictionary[self.model_name].from_pretrained(
            self.model_weights, cache_dir=self.cache_dir
        )
        self.model = model_class_dictionary[self.model_name].from_pretrained(
            self.model_weights, cache_dir=self.cache_dir
        )

        # Use a universal pad token since all transformer architectures do not have a
        # consistent token. Instead of pad_token_id we use unk_token_id because
        # pad_token_id is not set for all architectures. We can't add a new token as
        # well since vocabulary resizing is not yet supported for TF classes.
        # Also, this does not hurt the model predictions since we use an attention mask
        # while feeding input.
        self.pad_token_id = self.tokenizer.unk_token_id

    @classmethod
    def cache_key(
        cls, component_meta: Dict[Text, Any], model_metadata: Metadataset
    ) -> Optional[Text]:

        weight = component_meta.get("model_weights") or {}

        return f"{cls.name}-{component_meta.get('model_name')}-{get_dict_hash(weight)}"

    @classmethod
    def req_packages(cls) -> List[Text]:
        return ["transformers"]

    def _lm_tokenizer(self, text: Text) -> Tuple[List[int], List[Text]]:
        """Pass the text through the tokenizer of the language model.

        Args:
            text: Text to be tokenized.

        Returns:
            List of token ids and token strings.

        """
        spliting_tkn_id = self.tokenizer.encode(text, add_special_tokens=False)

        spliting_tkn_str = self.tokenizer.convert_ids_to_tokens(spliting_tkn_id)

        return spliting_tkn_id, spliting_tkn_str

    def _add_lm_special_specific_tkns(
        self, token_ids: List[List[int]]
    ) -> List[List[int]]:
        """Add language model specific special tokens which were used during their training.

        Args:
            token_ids: List of token ids for each example in the batch.

        Returns:
            Augmented list of token ids for each example in the batch.
        """
        from convo.nlu.utils.hugging_face.registry import (
            model_special_tkns_pre_processors,
        )

        token_augmented = [
            model_special_tkns_pre_processors[self.model_name](example_token_ids)
            for example_token_ids in token_ids
        ]
        return token_augmented

    def _lm_specific_cleanup_tkn(
        self, split_token_ids: List[int], token_strings: List[Text]
    ) -> Tuple[List[int], List[Text]]:
        """Clean up special chars added by tokenizers of language models.

        Many language models add a special char in front/back of (some) words. We clean
        up those chars as they are not
        needed once the features are already computed.

        Args:
            split_token_ids: List of token ids received as output from the language
            model specific tokenizer.
            token_strings: List of token strings received as output from the language
            model specific tokenizer.

        Returns:
            Cleaned up token ids and token strings.
        """
        from convo.nlu.utils.hugging_face.registry import model_tkns_cleaner

        return model_tkns_cleaner[self.model_name](split_token_ids, token_strings)

    def _post_process_seq_embed(
        self, sequence_embeddings: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Compute sentence level representations and sequence level representations
        for relevant tokens.

        Args:
            sequence_embeddings: Sequence level dense features received as output from
            language model.

        Returns:
            Sentence and sequence level representations.
        """

        from convo.nlu.utils.hugging_face.registry import (
            model_embeded_postprocessors,
        )

        embed_sentence = []
        post_process_seq_embeded = []

        for example_embedding in sequence_embeddings:
            (
                example_sentence_embedding,
                example_post_processed_embedding,
            ) = model_embeded_postprocessors[self.model_name](example_embedding)

            embed_sentence.append(example_sentence_embedding)
            post_process_seq_embeded.append(example_post_processed_embedding)

        return (
            np.array(embed_sentence),
            np.array(post_process_seq_embeded),
        )

    def _tokenizer_exp(
        self, message: Msg, attribute: Text
    ) -> Tuple[List[Tkn], List[int]]:
        """Tokenize a single message example.

        Many language models add a special char in front of (some) words and split
        words into sub-words. To ensure the entity start and end values matches the
        token values, tokenize the text first using the whitespace tokenizer. If
        individual tokens are split up into multiple tokens, we add this information
        to the respected token.

        Args:
            message: Single message object to be processed.
            attribute: Property of message to be processed, one of ``TXT`` or
            ``RETURN_RESPONSE``.

        Returns:
            List of token strings and token ids for the corresponding attribute of the
            message.
        """

        in_tkn = self.whitespace_tokenizer.tokenizer(message, attribute)

        outer_token = []

        outer_id_token = []

        for token in in_tkn:
            # use lm specific tokenizer to further tokenize the text
            split_token_ids, split_token_strings = self._lm_tokenizer(token.text)

            split_token_ids, split_token_strings = self._lm_specific_cleanup_tkn(
                split_token_ids, split_token_strings
            )

            outer_id_token += split_token_ids

            token.put(SUB_TOKENS_NUM, len(split_token_strings))

            outer_token.append(token)

        return outer_token, outer_id_token

    def _get_tkn_ids_for_group(
        self, batch_examples: List[Msg], attribute: Text
    ) -> Tuple[List[List[Tkn]], List[List[int]]]:
        """Compute token ids and token strings for each example in batch.

        A token id is the id of that token in the vocabulary of the language model.
        Args:
            batch_examples: Batch of message objects for which tokens need to be
            computed.
            attribute: Property of message to be processed, one of ``TXT`` or
            ``RETURN_RESPONSE``.

        Returns:
            List of token strings and token ids for each example in the batch.
        """

        group_token_id = []
        group_token = []
        for example in batch_examples:

            example_tokens, example_token_ids = self._tokenizer_exp(
                example, attribute
            )
            group_token.append(example_tokens)
            group_token_id.append(example_token_ids)

        return group_token, group_token_id

    @staticmethod
    def _compute_mask_attention(
        actual_sequence_lengths: List[int], max_input_sequence_length: int
    ) -> np.ndarray:
        """Compute a mask for padding tokens.

        This mask will be used by the language model so that it does not attend to
        padding tokens.

        Args:
            actual_sequence_lengths: List of length of each example without any padding.
            max_input_sequence_length: Maximum length of a sequence that will be present in the input batch. This is
            after taking into consideration the maximum input sequence the model can handle. Hence it can never be
            greater than self.max_model_sequence_length in case the model applies length restriction.

        Returns:
            Computed attention mask, 0 for padding and 1 for non-padding tokens.
        """

        mask_attention = []

        for actual_sequence_length in actual_sequence_lengths:
            # add 1s for present tokens, fill up the remaining space up to max
            # sequence length with 0s (non-existing tokens)
            padded_seq = [1] * min(
                actual_sequence_length, max_input_sequence_length
            ) + [0] * (
                max_input_sequence_length
                - min(actual_sequence_length, max_input_sequence_length)
            )
            mask_attention.append(padded_seq)

        mask_attention = np.array(mask_attention).astype(np.float32)
        return mask_attention

    def _extract_seq_len(
        self, batch_token_ids: List[List[int]]
    ) -> Tuple[List[int], int]:

        # Compute max length across examples
        max_input_seq_len = 0
        actual_seq_len = []

        for example_token_ids in batch_token_ids:
            sequence_length = len(example_token_ids)
            actual_seq_len.append(sequence_length)
            max_input_seq_len = max(
                max_input_seq_len, len(example_token_ids)
            )

        # Take into account the maximum sequence length the model can handle
        max_input_seq_len = (
            max_input_seq_len
            if self.max_model_sequence_length == NO_LEN_RESTRICT
            else min(max_input_seq_len, self.max_model_sequence_length)
        )

        return actual_seq_len, max_input_seq_len

    def _add_padding_to_group(
        self, batch_token_ids: List[List[int]], max_sequence_length_model: int
    ) -> List[List[int]]:
        """Add padding so that all examples in the batch are of the same length.

        Args:
            batch_token_ids: Batch of examples where each example is a non-padded list
            of token ids.
            max_sequence_length_model: Maximum length of any input sequence in the batch
            to be fed to the model.

        Returns:
            Padded batch with all examples of the same length.
        """
        tkn_padded_id = []

        # Add padding according to max_sequence_length
        # Some models don't contain pad token, we use unknown token as padding token.
        # This doesn't affect the computation since we compute an attention mask
        # anyways.
        for example_token_ids in batch_token_ids:

            # Truncate any longer sequences so that they can be fed to the model
            if len(example_token_ids) > max_sequence_length_model:
                example_token_ids = example_token_ids[:max_sequence_length_model]

            tkn_padded_id.append(
                example_token_ids
                + [self.pad_token_id]
                * (max_sequence_length_model - len(example_token_ids))
            )
        return tkn_padded_id

    @staticmethod
    def _extract_non_padded_embed(
        embeddings: np.ndarray, actual_sequence_lengths: List[int]
    ) -> np.ndarray:
        """Use pre-computed non-padded lengths of each example to extract embeddings
        for non-padding tokens.

        Args:
            embeddings: sequence level representations for each example of the batch.
            actual_sequence_lengths: non-padded lengths of each example of the batch.

        Returns:
            Sequence level embeddings for only non-padding tokens of the batch.
        """
        non_padded_seq_embeded = []
        for index, embedding in enumerate(embeddings):
            unmasked_embedding = embedding[: actual_sequence_lengths[index]]
            non_padded_seq_embeded.append(unmasked_embedding)

        return np.array(non_padded_seq_embeded)

    def _compute_group_seq_feature(
        self, batch_attention_mask: np.ndarray, padded_token_ids: List[List[int]]
    ) -> np.ndarray:
        """Feed the padded batch to the language model.

        Args:
            batch_attention_mask: Mask of 0s and 1s which indicate whether the token
            is a padding token or not.
            padded_token_ids: Batch of token ids for each example. The batch is padded
            and hence can be fed at once.

        Returns:
            Sequence level representations from the language model.
        """
        model_outcome = self.model(
            np.array(padded_token_ids), attention_mask=np.array(batch_attention_mask)
        )

        # sequence hidden states is always the first output from all models
        seq_hide_state = model_outcome[0]

        seq_hide_state = seq_hide_state.numpy()
        return seq_hide_state

    def _validate_seq_len(
        self,
        actual_sequence_lengths: List[int],
        batch_examples: List[Msg],
        attribute: Text,
        inference_mode: bool = False,
    ) -> None:
        """Validate if sequence lengths of all inputs are less the max sequence length the model can handle

        This method should throw an error during training, whereas log a debug message during inference if
        any of the input examples have a length greater than maximum sequence length allowed.

        Args:
            actual_sequence_lengths: original sequence length of all inputs
            batch_examples: all message instances in the batch
            attribute: attribute of message object to be processed
            inference_mode: Whether this is during training or during inferencing
        """
        if self.max_model_sequence_length == NO_LEN_RESTRICT:
            # There is no restriction on sequence length from the model
            return

        for sequence_length, example in zip(actual_sequence_lengths, batch_examples):
            if sequence_length > self.max_model_sequence_length:
                if not inference_mode:
                    raise RuntimeError(
                        f"The sequence length of '{example.get(attribute)[:20]}...' "
                        f"is too long({sequence_length} tokens) for the "
                        f"model chosen {self.model_name} which has a maximum "
                        f"sequence length of {self.max_model_sequence_length} tokens. Either "
                        f"shorten the message or use a model which has no "
                        f"restriction on input sequence length like XLNet."
                    )
                else:
                    log.debug(
                        f"The sequence length of '{example.get(attribute)[:20]}...' "
                        f"is too long({sequence_length} tokens) for the "
                        f"model chosen {self.model_name} which has a maximum "
                        f"sequence length of {self.max_model_sequence_length} tokens. "
                        f"Downstream model predictions may be affected because of this."
                    )

    def _adding_extra_padding(
        self, sequence_embeddings: np.ndarray, actual_sequence_lengths: List[int]
    ) -> np.ndarray:
        """
        Add extra zero padding to match the original sequence length.

        This is only done if the input was truncated during the batch preparation of input for the model.
        Args:
            sequence_embeddings: Embeddings returned from the model
            actual_sequence_lengths: original sequence length of all inputs

        Returns:
            Modified sequence embeddings with padding if necessary
        """

        if self.max_model_sequence_length == NO_LEN_RESTRICT:
            # No extra padding needed because there wouldn't have been any truncation in the first place
            return sequence_embeddings

        reshaped_seq_embeded = []
        for index, embedding in enumerate(sequence_embeddings):
            embeded_size = embedding.shape[-1]
            if actual_sequence_lengths[index] > self.max_model_sequence_length:
                embedding = np.concatenate(
                    [
                        embedding,
                        np.zeros(
                            (
                                actual_sequence_lengths[index]
                                - self.max_model_sequence_length,
                                embeded_size,
                            ),
                            dtype=np.float32,
                        ),
                    ]
                )
            reshaped_seq_embeded.append(embedding)

        return np.array(reshaped_seq_embeded)

    def _fetch_model_feature_for_group(
        self,
        batch_token_ids: List[List[int]],
        batch_tokens: List[List[Tkn]],
        batch_examples: List[Msg],
        attribute: Text,
        inference_mode: bool = False,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Compute dense features of each example in the batch.

        We first add the special tokens corresponding to each language model. Next, we
        add appropriate padding and compute a mask for that padding so that it doesn't
        affect the feature computation. The padded batch is next fed to the language
        model and token level embeddings are computed. Using the pre-computed mask,
        embeddings for non-padding tokens are extracted and subsequently sentence
        level embeddings are computed.

        Args:
            batch_token_ids: List of token ids of each example in the batch.
            batch_tokens: List of token objects for each example in the batch.
            batch_examples: List of examples in the batch.
            attribute: attribute of the Msg object to be processed.
            inference_mode: Whether the call is during training or during inference.

        Returns:
            Sentence and token level dense representations.
        """
        # Let's first add tokenizer specific special tokens to all examples
        group_tkn_id_augmented = self._add_lm_special_specific_tkns(
            batch_token_ids
        )

        # Compute sequence lengths for all examples
        (
            actual_sequence_lengths,
            max_input_sequence_length,
        ) = self._extract_seq_len(group_tkn_id_augmented)

        # Validate that all sequences can be processed based on their sequence lengths and
        # the maximum sequence length the model can handle
        self._validate_seq_len(
            actual_sequence_lengths, batch_examples, attribute, inference_mode
        )

        # Add padding so that whole batch can be fed to the model
        padded_tkn_id = self._add_padding_to_group(
            group_tkn_id_augmented, max_input_sequence_length
        )

        # Compute attention mask based on actual_sequence_length
        group_attention_mask = self._compute_mask_attention(
            actual_sequence_lengths, max_input_sequence_length
        )

        # Get token level features from the model
        seq_hidden_state = self._compute_group_seq_feature(
            group_attention_mask, padded_tkn_id
        )

        # Extract features for only non-padding tokens
        seq_non_padded_embedding = self._extract_non_padded_embed(
            seq_hidden_state, actual_sequence_lengths
        )

        # Extract sentence level and post-processed features
        (
            sentence_embeddings,
            seq_embedding,
        ) = self._post_process_seq_embed(seq_non_padded_embedding)

        # Pad zeros for examples which were truncated in inference mode.
        # This is intentionally done after sentence embeddings have been extracted so that they are not affected
        seq_embedding = self._adding_extra_padding(
            seq_embedding, actual_sequence_lengths
        )

        # shape of matrix for all sequence embeddings
        group_dim = len(seq_embedding)
        sequence_dim = max(e.shape[0] for e in seq_embedding)
        feature_dimension = seq_embedding[0].shape[1]
        shapes = (group_dim, sequence_dim, feature_dimension)


        # align features with tokens so that we have just one vector per token
        # (don't include sub-tokens)
        seq_embedding = train_utils.aligning_token_features(
            batch_tokens, seq_embedding, shapes
        )

        # seq_embedding is a padded numpy array
        # remove the padding, keep just the non-zero vectors
        seq_final_embedding = []
        for embeddings, tokens in zip(seq_embedding, batch_tokens):
            seq_final_embedding.append(embeddings[: len(tokens)])
        seq_final_embedding = np.array(seq_final_embedding)

        return sentence_embeddings, seq_final_embedding

    def _fetch_docs_for_group(
        self,
        batch_examples: List[Msg],
        attribute: Text,
        inference_mode: bool = False,
    ) -> List[Dict[Text, Any]]:
        """Compute language model docs for all examples in the batch.

        Args:
            batch_examples: Batch of message objects for which language model docs
            need to be computed.
            attribute: Property of message to be processed, one of ``TXT`` or
            ``RETURN_RESPONSE``.
            inference_mode: Whether the call is during inference or during training.


        Returns:
            List of language model docs for each message in batch.
        """

        group_token, group_token_id = self._get_tkn_ids_for_group(
            batch_examples, attribute
        )

        (
            batch_sentence_features,
            batch_sequence_features,
        ) = self._fetch_model_feature_for_group(
            group_token_id, group_token, batch_examples, attribute, inference_mode
        )

        # A doc consists of
        # {'token_ids': ..., 'tokens': ..., 'sequence_features': ...,
        # 'sentence_features': ...}
        group_document = []
        for index in range(len(batch_examples)):
            doc = {
                TKN_IDS: group_token_id[index],
                TKNS: group_token[index],
                SEQUENTIAL_FEATURES: batch_sequence_features[index],
                SENTENCE_FTRS: np.reshape(batch_sentence_features[index], (1, -1)),
            }
            group_document.append(doc)

        return group_document

    def training(
        self,
        training_data: TrainingDataSet,
        config: Optional[ConvoNLUModelConfiguration] = None,
        **kwargs: Any,
    ) -> None:
        """Compute tokens and dense features for each message in training data.

        Args:
            training_data: NLU training data to be tokenized and featurized
            config: NLU pipeline config consisting of all components.

        """

        group_size = 64

        for attribute in DENSE_FEATURE_ATTRS:

            non_empty_exp = list(
                filter(lambda x: x.get(attribute), training_data.training_examples)
            )

            group_begin_index = 0

            while group_begin_index < len(non_empty_exp):

                group_end_index = min(
                    group_begin_index + group_size, len(non_empty_exp)
                )
                # Collect batch examples
                group_msg = non_empty_exp[group_begin_index:group_end_index]

                # Construct a doc with relevant features
                # extracted(tokens, dense_features)
                group_document = self._fetch_docs_for_group(group_msg, attribute)

                for index, ex in enumerate(group_msg):

                    ex.put(LANG_MODEL_DOCUMENTS[attribute], group_document[index])

                group_begin_index += group_size

    def process(self, message: Msg, **kwargs: Any) -> None:
        """Process an incoming message by computing its tokens and dense features.

        Args:
            message: Incoming message object
        """

        # process of all featurizers operates only on TXT and ACT_TEXT attributes,
        # because all others attributes are labels which are featurized during training
        # and their features are stored by the model itself.
        for attribute in {TXT, ACT_TEXT}:
            if message.get(attribute):
                message.put(
                    LANG_MODEL_DOCUMENTS[attribute],
                    self._fetch_docs_for_group(
                        [message], attribute=attribute, inference_mode=True
                    )[0],
                )
