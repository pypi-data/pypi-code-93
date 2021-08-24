# -*- coding=utf-8 -*-
"""GPT2 preprocess."""
from typing import Tuple
import numpy as np
import pandas as pd
import tensorflow as tf
from transformers import TFGPT2ForSequenceClassification, GPT2Tokenizer


gpt2_model = TFGPT2ForSequenceClassification.from_pretrained('gpt2')
wte = gpt2_model.transformer.wte.weight
wpe = gpt2_model.transformer.wpe


def embedding_and_mask_preprocessing(input_ids: tf.Tensor, attention_mask: tf.Tensor) -> Tuple[np.ndarray, np.ndarray]:
    """
    Doing all the necessary preprocessing of tokens and attention masks before passing them to encoders..

    Adding dimensions and replacing ones with zeros and zeros with -10000.
    Passing attention scores through the softmax will tell our model not to pay attention to padding tokens

    Parameters
    ----------
    input_ids
        tokenized text
    attention_mask
        indicator to padding tokens
    Returns
    -------
    array
        Preprocessed attention masks.
    array
        Preprocessed embeddings.
    """
    position_ids = tf.expand_dims(tf.range(0, np.shape(input_ids)[-1]), axis=0)
    position_embeddings = tf.gather(wpe, position_ids, axis=0)
    input_embeddings = tf.gather(wte, input_ids, axis=0)
    token_type_embeds = tf.constant(0.0)
    final_embeddings = position_embeddings + input_embeddings + token_type_embeds

    attention_mask_shape = np.shape(attention_mask)
    attention_mask = tf.reshape(attention_mask, (attention_mask_shape[0], 1, 1, attention_mask_shape[1]))
    one_cst = tf.constant(1.0)
    attention_mask = tf.cast(attention_mask, one_cst.dtype)
    attention_mask = tf.multiply(tf.subtract(one_cst, attention_mask), tf.constant(-10000.0))

    return np.asarray(final_embeddings), np.asarray(attention_mask)


def text_preprocessing(path_to_csv: str, calibration: bool) -> Tuple[tf.Tensor, tf.Tensor, np.ndarray]:
    """
    Doing all the necessary preprocessing of raw text.

    Tokenizing raw text, adding special tokens on both sides and convert each token to index.
    Then we perform padding of each tokenized text and based on that create attention masks.

    Parameters
    ----------
    path_to_csv
        path to the csv file, where is the desired raw texts
    calibration
        indicator of preprocessing usage
    Returns
    -------
    Tuple
        tokenized text and corresponding attention masks.
    """
    dataframe = pd.read_csv(path_to_csv)

    if calibration:
        dataframe = dataframe.sample(100)

    sentences = dataframe['text'].values
    labels = dataframe['sentiment'].values

    gpt2_tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
    gpt2_tokenizer.padding_side = "left"
    gpt2_tokenizer.pad_token = gpt2_tokenizer.eos_token

    max_len = 64
    final_embeddings = []
    final_extended_masks = []
    for sentence in sentences:
        input_ = gpt2_tokenizer(sentence, return_tensors="tf", max_length=max_len, padding='max_length')
        embeddings, extended_masks = embedding_and_mask_preprocessing(input_['input_ids'], input_['attention_mask'])
        final_embeddings.append(embeddings[0])
        final_extended_masks.append(extended_masks[0])
    final_embeddings = tf.convert_to_tensor(final_embeddings)
    final_extended_masks = tf.convert_to_tensor(final_extended_masks)

    return final_embeddings, final_extended_masks, labels
