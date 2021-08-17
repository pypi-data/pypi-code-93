#! /usr/bin/python
# -*- coding: utf-8 -*-

import tensorlayer as tl
from tensorlayer import logging
from tensorlayer.layers.core import Module

__all__ = [
    'MultiheadAttention',
    'Transformer',
    'TransformerEncoder',
    'TransformerDecoder',
    'TransformerEncoderLayer',
    'TransformerDecoderLayer',
]

class MultiheadAttention(Module):

    def __init__(self,
                 embed_dim,
                 num_heads,
                 dropout = 0.0,
                 kdim = None,
                 vdim = None,
                 bias = True,
                 batch_first = False,
                 need_weights = True,
                 name=None,):
        super(MultiheadAttention, self).__init__(name)

        self.embed_dim = embed_dim
        self.kdim = kdim if kdim is not None else embed_dim
        self.vdim = vdim if vdim is not None else embed_dim
        self.num_heads = num_heads
        self.dropout = dropout
        self.need_weights = need_weights
        self.head_dim = embed_dim // num_heads
        self.bias = bias
        self.batch_first = batch_first
        assert self.head_dim * num_heads == self.embed_dim, "embed_dim must be divisible by num_heads"

        self.build(None)
        logging.info(
            "MultiheadAttention %s: embed_dim: %d num_heads: %d kdim: %d vdim: %d dropout: %f" % (
                self.name, embed_dim, num_heads, self.kdim, self.vdim, dropout)
        )

    def __repr__(self):
        s = (
            '{classname}(embed_dim={embed_dim}, num_heads={num_heads}, dropout={dropout}'
            ', kdim={kdim}, vdim={vdim}, bias={bias}, batch_first={batch_first}, '
            'need_weights={need_weights}'
        )
        if self.name is not None:
            s+=', name = \'{name}\''
        s += ')'
        return s.format(classname=self.__class__.__name__, **self.__dict__)

    def build(self, inputs_shape):
        bias_init = tl.initializers.zeros()
        weight_init = tl.initializers.XavierNormal()
        self.q_proj_weight = self._get_weights(
            'q_weight', shape=(self.embed_dim, self.embed_dim), init=weight_init, order=True)
        self.k_proj_weight = self._get_weights(
            'k_weight', shape=(self.embed_dim, self.kdim), init=weight_init, order=True
        )
        self.v_proj_weight = self._get_weights(
            'v_weight', shape=(self.embed_dim, self.vdim), init=weight_init, order=True
        )
        self.out_proj_weight = self._get_weights(
            'out_weight', shape=(self.embed_dim, self.embed_dim), init=weight_init, order=True
        )
        self.q_bias = None
        self.k_bias = None
        self.v_bias = None
        self.out_bias = None
        if self.bias:
            self.q_bias = self._get_weights('q_bias', shape=(self.embed_dim,), init=bias_init, order=True)
            self.k_bias = self._get_weights('k_bias', shape=(self.embed_dim,), init=bias_init, order=True)
            self.v_bias = self._get_weights('v_bias', shape=(self.embed_dim,), init=bias_init, order=True)
            self.out_bias = self._get_weights('out_bias', shape=(self.embed_dim,), init=bias_init, order=True)

        self.multiheadattention = tl.ops.multiheadattention(
            embed_dim=self.embed_dim, num_heads=self.num_heads, dropout=self.dropout, batch_first=self.batch_first,
            need_weights=self.need_weights, q_weight=self.q_proj_weight, k_weight=self.k_proj_weight,
            v_weight=self.v_proj_weight, out_weight=self.out_proj_weight, q_bias=self.q_bias, k_bias=self.k_bias,
            v_bias = self.v_bias, out_bias=self.out_bias, train = self.is_train

        )

    # def forward(self, q, k=None, v=None, attn_mask = None, key_padding_mask = None):
    #
    #     attn_output,  attn_output_weights = self.multiheadattention(q, k, v, attn_mask, key_padding_mask)
    #
    #     return attn_mask, attn_output_weights




class Transformer(Module):

    pass

class TransformerEncoder(Module):
    pass

class TransformerDecoder(Module):
    pass

class TransformerEncoderLayer(Module):
    pass

class TransformerDecoderLayer(Module):
    pass

if __name__ == '__main__':
    l = MultiheadAttention(3,3)
    l.set_eval()
    print(l.is_train)