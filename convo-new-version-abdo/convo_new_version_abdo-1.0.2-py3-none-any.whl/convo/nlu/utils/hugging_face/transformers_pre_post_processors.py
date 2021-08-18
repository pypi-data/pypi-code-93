from typing import List, Tuple, Text
import numpy as np


def cleanup_tkns(
    tkn_id_str: List[Tuple[int, Text]], delimiter: Text
) -> Tuple[List[int], List[Text]]:
    """Utility method to apply delimiter based cleanup on list of tokens.

    Args:
        tkn_id_str: List of tuples with each tuple containing (token id, token string).
        delimiter: character/string to be cleaned from token strings.

    Returns:
        Token ids and Token strings unpacked.
    """

    tkn_id_str = [
        (id, string.replace(delimiter, "")) for id, string in tkn_id_str
    ]

    # remove empty strings
    tkn_id_str = [(id, string) for id, string in tkn_id_str if string]

    # return as individual token ids and token strings
    tkn_id, tkn_str = zip(*tkn_id_str)
    return tkn_id, tkn_str


def bert_tkns_pre_processor(token_ids: List[int]) -> List[int]:
    """Add BERT style special tokens(CLS and SEP).

    Args:
        token_ids: List of token ids without any special tokens.

    Returns:
        List of token ids augmented with special tokens.
    """
    CLS_ID_BERT = 101
    SEP_ID_BERT = 102

    process_tkns = token_ids

    process_tkns.insert(0, CLS_ID_BERT)
    process_tkns.append(SEP_ID_BERT)

    return process_tkns


def gpt_tkns_pre_processor(token_ids: List[int]) -> List[int]:
    """Add GPT style special tokens(None).

    Args:
        token_ids: List of token ids without any special tokens.

    Returns:
        List of token ids augmented with special tokens.
    """

    return token_ids


def xlnet_tkns_pre_processor(token_ids: List[int]) -> List[int]:
    """Add XLNET style special tokens.

    Args:
        token_ids: List of token ids without any special tokens.

    Returns:
        List of token ids augmented with special tokens.
    """
    CLS_ID_XLNET = 3
    SEP_ID_XLNET = 4

    token_ids.append(SEP_ID_XLNET)
    token_ids.append(CLS_ID_XLNET)

    return token_ids


def roberta_tkns_preprocessor(token_ids: List[int]) -> List[int]:
    """Add RoBERTa style special tokens.

    Args:
        token_ids: List of token ids without any special tokens.

    Returns:
        List of token ids augmented with special tokens.
    """
    BEG_ID_ROBERTA = 0
    END_ID_ROBERTA = 2

    token_ids.insert(0, BEG_ID_ROBERTA)
    token_ids.append(END_ID_ROBERTA)

    return token_ids


def xlm_tkns_preprocessor(token_ids: List[int]) -> List[int]:
    """Add XLM style special tokens.

    Args:
        token_ids: List of token ids without any special tokens.

    Returns:
        List of token ids augmented with special tokens.
    """
    SEP_ID_XLM = 1

    token_ids.insert(0, SEP_ID_XLM)
    token_ids.append(SEP_ID_XLM)

    return token_ids


def post_processor_bert_embedding(
    sequence_embeddings: np.ndarray,
) -> Tuple[np.ndarray, np.ndarray]:
    """Post-process embeddings from BERT.

    by removing CLS and SEP embeddings and returning CLS token embedding as
    sentence representation.

    Args:
        sequence_embeddings: Sequence of token level embeddings received as output from BERT.

    Returns:
        sentence level embedding and post-processed sequence level embedding.
    """
    embedding_sentence = sequence_embeddings[0]
    embedding_post_processed = sequence_embeddings[1:-1]

    return embedding_sentence, embedding_post_processed


def post_processor_gpt_embedding(
    sequence_embeddings: np.ndarray,
) -> Tuple[np.ndarray, np.ndarray]:
    """Post-process embeddings from GPT models.

    by taking a mean over sequence embeddings and returning that as sentence
    representation.

    Args:
        sequence_embeddings: Sequence of token level embeddings received as output from GPT.

    Returns:
        sentence level embedding and post-processed sequence level embedding.
    """
    embedding_sentence = np.mean(sequence_embeddings, axis=0)
    embedding_post_processed = sequence_embeddings

    return embedding_sentence, embedding_post_processed


def post_processor_xlnet_embedding(
    sequence_embeddings: np.ndarray,
) -> Tuple[np.ndarray, np.ndarray]:
    """Post-process embeddings from XLNet models.

    by taking a mean over sequence embeddings and returning that as sentence
    representation. Remove last two time steps corresponding
    to special tokens from the sequence embeddings.

    Args:
        sequence_embeddings: Sequence of token level embeddings received as output from XLNet.

    Returns:
        sentence level embedding and post-processed sequence level embedding.
    """
    embedding_post_processed = sequence_embeddings[:-2]
    embedding_sentence = np.mean(embedding_post_processed, axis=0)

    return embedding_sentence, embedding_post_processed


def post_processor_roberta_embedding(
    sequence_embeddings: np.ndarray,
) -> Tuple[np.ndarray, np.ndarray]:
    """Post process embeddings from Roberta models.

    by taking a mean over sequence embeddings and returning that as sentence
    representation. Remove first and last time steps
    corresponding to special tokens from the sequence embeddings.

    Args:
        sequence_embeddings: Sequence of token level embeddings received as output from Roberta

    Returns:
        sentence level embedding and post-processed sequence level embedding
    """

    embedding_post_processed = sequence_embeddings[1:-1]
    embedding_sentence = np.mean(embedding_post_processed, axis=0)

    return embedding_sentence, embedding_post_processed


def post_processor_xlm_embedding(
    sequence_embeddings: np.ndarray,
) -> Tuple[np.ndarray, np.ndarray]:
    """Post process embeddings from XLM models

    by taking a mean over sequence embeddings and returning that as sentence
    representation. Remove first and last time steps
    corresponding to special tokens from the sequence embeddings.

    Args:
        sequence_embeddings: Sequence of token level embeddings received as output from XLM

    Returns:
        sentence level embedding and post-processed sequence level embedding
    """
    embedding_post_processed = sequence_embeddings[1:-1]
    embedding_sentence = np.mean(embedding_post_processed, axis=0)

    return embedding_sentence, embedding_post_processed


def bert_tkns_cleaner(
    token_ids: List[int], token_strings: List[Text]
) -> Tuple[List[int], List[Text]]:
    """Token cleanup method for BERT.

    Clean up tokens with the extra delimiters(##) BERT adds while breaking a token into sub-tokens.

    Args:
        token_ids: List of token ids received as output from BERT Tokenizer.
        token_strings: List of token strings received as output from BERT Tokenizer.

    Returns:
        Cleaned token ids and token strings.
    """
    return cleanup_tkns(list(zip(token_ids, token_strings)), "##")


def openaigpt_tkns_cleaner(
    token_ids: List[int], token_strings: List[Text]
) -> Tuple[List[int], List[Text]]:
    """Token cleanup method for GPT.

    Clean up tokens with the extra delimiters(</w>) OpenAIGPT adds while breaking a token into sub-tokens.

    Args:
        token_ids: List of token ids received as output from GPT Tokenizer.
        token_strings: List of token strings received as output from GPT Tokenizer.

    Returns:
        Cleaned token ids and token strings.
    """
    return cleanup_tkns(list(zip(token_ids, token_strings)), "</w>")


def gpt2_tkns_cleaner(
    token_ids: List[int], token_strings: List[Text]
) -> Tuple[List[int], List[Text]]:
    """Token cleanup method for GPT2.

    Clean up tokens with the extra delimiters(Ġ) GPT2 adds while breaking a token into sub-tokens.

    Args:
        token_ids: List of token ids received as output from GPT Tokenizer.
        token_strings: List of token strings received as output from GPT Tokenizer.

    Returns:
        Cleaned token ids and token strings.
    """
    return cleanup_tkns(list(zip(token_ids, token_strings)), "Ġ")


def xlnet_tkns_cleaner(
    token_ids: List[int], token_strings: List[Text]
) -> Tuple[List[int], List[Text]]:
    """Token cleanup method for XLNet.

    Clean up tokens with the extra delimiters(▁) XLNet adds while breaking a token into sub-tokens.

    Args:
        token_ids: List of token ids received as output from GPT Tokenizer.
        token_strings: List of token strings received as output from GPT Tokenizer.

    Returns:
        Cleaned token ids and token strings.
    """
    return cleanup_tkns(list(zip(token_ids, token_strings)), "▁")
