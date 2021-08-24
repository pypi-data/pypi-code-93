"""Utils for BERT-large-uncased."""
import os
import numpy as np
from iva_applications.bert_large.preprocess import preprocessing_word_embeddings,\
    preprocessing_attention_masks, text_preprocessing


def save_calibration_tensors(save_dir: str, path_to_csv: str) -> None:
    """
    Doing all the steps to produce calibration tensors..

    Tokenizing our 100 sentences and creating corresponding attention masks.
    Then we convert our tokens into word embeddings and extend our attention masks.
    Last step is the saving calibration tensors

    Parameters
    ----------
    save_dir
        directory for saving tensors
    path_to_csv
        path to csv file with raw text
    Returns
    -------
    None

    """
    input_ids, attention_masks, _ = text_preprocessing(path_to_csv, calibration=True)
    word_embeddings = preprocessing_word_embeddings(input_ids)
    extended_attention_masks = preprocessing_attention_masks(attention_masks)
    word_embeddings = np.asarray(word_embeddings, dtype=np.float32)
    extended_attention_masks = np.asarray(extended_attention_masks, dtype=np.float32)
    np.save(os.path.join(save_dir, 'calibration_tensor_bert_large_embeddings'), word_embeddings)
    np.save(os.path.join(save_dir, 'calibration_tensor_bert_large_masks'), extended_attention_masks)
