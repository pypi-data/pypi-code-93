# -*- coding=utf-8 -*-
"""BERT-large-uncased preprocess."""
from typing import Tuple
import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras.preprocessing.sequence import pad_sequences
from transformers import TFBertForSequenceClassification, BertTokenizer


# Loading fine-tuned BERT-large and extracting pre-trained embeddings
pre_trained_bert = TFBertForSequenceClassification.from_pretrained('bert-large-uncased', num_labels=2)
pre_trained_embeddings = pre_trained_bert.bert.get_input_embeddings().weight
pre_trained_token_type_embeddings = pre_trained_bert.bert.get_input_embeddings().token_type_embeddings
pre_trained_position_embeddings = pre_trained_bert.bert.get_input_embeddings().position_embeddings
pre_trained_layer_norm = pre_trained_bert.bert.get_input_embeddings().LayerNorm


def preprocessing_word_embeddings(input_ids: np.ndarray) -> tf.Tensor:
    """
    Extract word embeddings from the BERT's pre-trained weights.

    Parameters
    ----------
    input_ids
        indexes of tokens in the sentence
    Returns
    -------
    tensor
        Preprocessed word embeddings.
    """
    indices = tf.constant(input_ids)
    inputs_embeds = tf.gather(params=pre_trained_embeddings, indices=indices, axis=0)
    input_shape = np.shape(inputs_embeds)[:-1]
    token_type_ids = tf.fill(dims=input_shape, value=0)
    position_ids = tf.expand_dims(tf.range(start=0, limit=input_shape[-1]), axis=0)
    position_embeds = tf.gather(params=pre_trained_position_embeddings, indices=position_ids, axis=0)
    position_embeds = tf.tile(input=position_embeds, multiples=(input_shape[0], 1, 1))
    token_type_embeds = tf.gather(params=pre_trained_token_type_embeddings, indices=token_type_ids, axis=0)

    embeddings_sum = tf.keras.layers.Add()
    final_embeddings = embeddings_sum(inputs=[inputs_embeds, position_embeds, token_type_embeds])

    final_embeddings = pre_trained_layer_norm(inputs=final_embeddings)

    return final_embeddings


def preprocessing_attention_masks(attention_masks: np.ndarray) -> tf.Tensor:
    """
    Doing all the necessary preprocessing of attention masks for future pass into the stack of encoders.

    Adding dimensions and replacing ones with zeros and zeros with -10000.
    Passing attention scores through the softmax will tell our model not to pay attention to padding tokens

    Parameters
    ----------
    attention_masks
        ones for paying attention and zeros otherwise
    Returns
    -------
    tensor
        Preprocessed attention masks.
    """
    input_shape = np.shape(attention_masks)
    extended_attention_mask = tf.reshape(attention_masks, (input_shape[0], 1, 1, input_shape[1]))
    extended_attention_mask = tf.cast(extended_attention_mask, tf.float32)
    one_cst = tf.constant(1.0, dtype=tf.float32)
    ten_thousand_cst = tf.constant(-10000.0, dtype=tf.float32)
    extended_attention_mask = tf.multiply(tf.subtract(one_cst, extended_attention_mask), ten_thousand_cst)

    return extended_attention_mask


def text_preprocessing(path_to_csv: str, calibration: bool) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Doing all the necessary preprocessing of raw text.

    Tokenizing raw text, adding special tokens on both sides and convert each token to index.
    Then we perform padding of each tokenized text and based on that create attention masks.

    Parameters
    ----------
    path_to_csv
        path to the csv file, where is the desired raw texts
    calibration
        indicate preprocessing for calibration tensors or for test
    Returns
    -------
    Tuple
        tokenized text and corresponding attention masks.
    """
    dataframe = pd.read_csv(path_to_csv)
    if calibration:
        dataframe = dataframe.sample(100)
        sentences = dataframe.text.values
        labels = dataframe.sentiment.values
    else:
        sentences = dataframe.text.values
        labels = dataframe.sentiment.values

    input_ids = []
    max_len = 55
    bert_tokenizer = BertTokenizer.from_pretrained('bert-large-uncased')
    for sentence in sentences:
        encoded_sentence = bert_tokenizer.encode(sentence, add_special_tokens=True)
        input_ids.append(encoded_sentence)
    input_ids = pad_sequences(input_ids, value=0, padding='post', maxlen=max_len)

    attention_masks = []
    for encoded_sentence in input_ids:
        attention_mask = [int(token > 0) for token in encoded_sentence]
        attention_masks.append(attention_mask)

    return np.asarray(input_ids), np.asarray(attention_masks), np.asarray(labels)
