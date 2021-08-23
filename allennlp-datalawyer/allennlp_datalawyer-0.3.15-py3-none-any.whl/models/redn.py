import math

import torch
import torch.nn.functional as F

from typing import Dict, List, Any

from allennlp.data import Vocabulary
from allennlp.models.model import Model
from allennlp.modules import TextFieldEmbedder
from allennlp.training.metrics import SpanBasedF1Measure, Metric


class RednLoss(torch.nn.Module):
    def __init__(self):
        super().__init__()

    def forward(self, score, adj: torch.Tensor, label: torch.Tensor):
        entity_mask = adj.unsqueeze(dim=1).repeat(1, score.shape[1], 1, 1).float()

        entity_sum = adj.sum(dim=(1, 2)).unsqueeze(dim=1).repeat(1, score.shape[1]).float()  # BS, NL

        pohl_mask = adj.sum(dim=(1, 2)) > 0

        pohl = adj.new_zeros(score.shape)
        s_index = label.unsqueeze(dim=1).unsqueeze(dim=2).unsqueeze(dim=3)
        s_index = s_index.repeat(1, 1, adj.shape[1], adj.shape[1])
        pohl = pohl.scatter(1, s_index, adj.unsqueeze(dim=1)).float()

        loss = ((F.binary_cross_entropy(score, pohl, reduction="none") * entity_mask).sum(dim=(2, 3))[pohl_mask] /
                entity_sum[pohl_mask]).mean()
        return loss


class MultiHeadAttentionScore(torch.nn.Module):
    def __init__(self, input_size, output_size, num_heads, output_attentions=False):
        super(MultiHeadAttentionScore, self).__init__()
        self.output_attentions = output_attentions
        self.num_heads = num_heads
        self.d_model_size = input_size

        self.depth = int(output_size / self.num_heads)

        self.Wq = torch.nn.Linear(input_size, output_size)
        self.Wk = torch.nn.Linear(input_size, output_size)

    def split_into_heads(self, x, batch_size):
        x = x.reshape(batch_size, -1, self.num_heads, self.depth)  # BS * SL * NH * H
        return x.permute([0, 2, 1, 3])  # BS * NH * SL * H

    def forward(self, k, q):  # BS * SL * HS
        batch_size = q.shape[0]

        q = self.Wq(q)  # BS * SL * OUT
        k = self.Wk(k)  # BS * SL * OUT

        q = self.split_into_heads(q, batch_size)  # BS * NH * SL * H
        k = self.split_into_heads(k, batch_size)  # BS * NH * SL * H

        attn_score = torch.matmul(q, k.permute(0, 1, 3, 2))
        attn_score = attn_score / math.sqrt(k.shape[-1])

        return attn_score


@Model.register("redn")
class Redn(Model):

    def __init__(self,
                 vocab: Vocabulary,
                 embedder: TextFieldEmbedder,
                 hidden_size: int = 768,
                 subject_1=True,
                 use_cls=True
                 ):
        super().__init__(vocab)
        self._embedder = embedder

        default_vocab_size = self._embedder.token_embedder_tokens.transformer_model.config.vocab_size
        self._embedder.token_embedder_tokens.transformer_model.resize_token_embeddings(default_vocab_size + 1)

        self.hidden_size = hidden_size
        self.loss_fn = RednLoss()

        self._f1 = SpanBasedF1Measure(vocab, 'labels')

        self.subject_1 = subject_1
        self.use_cls = use_cls

        self.num_rel_class = self.vocab.get_vocab_size("labels")
        self.attn_score = MultiHeadAttentionScore(input_size=self.hidden_size,
                                                  output_size=self.num_rel_class * self.hidden_size,
                                                  num_heads=self.num_rel_class)

    def forward(  # type: ignore
            self,
            context: Dict[str, Dict[str, torch.LongTensor]],
            head: torch.IntTensor,
            head_entity: torch.LongTensor,
            tail: torch.IntTensor,
            tail_entity: torch.LongTensor,
            relation_label: torch.LongTensor,
            metadata: List[Dict[str, Any]] = None
    ) -> Dict[str, torch.Tensor]:
        token_ids = context["tokens"]

        _, rep, hs = self._embedder(context)

        subject_output = hs[-1] if self.subject_1 else hs[-2]  # BS, SL, HS

        if self.use_cls:
            subject_output = subject_output + rep.view(-1, 1, rep.shape[-1])

        res = {}
        score = self.attn_score(hs[-1], subject_output).sigmoid()  # BS, NR, SL, SL
        res["logits"] = score

        adj = []
        seq_len = token_ids.shape[1]
        for i in range(len(token_ids)):
            h, t = token_ids.new_zeros((seq_len), dtype=torch.int8), token_ids.new_zeros((seq_len), dtype=torch.int8)
            h[tf[i][head_entity[0]]:tf[i][head_entity[1] + 1]] = 1
            t[tf[i][tail_entity[0]]:tf[i][tail_entity[1] + 1]] = 1
            h, t = h.unsqueeze(dim=0).repeat_interleave(seq_len, dim=0), t.unsqueeze(dim=0).repeat_interleave(seq_len,
                                                                                                              dim=0)
            adj.append((h + t.t() == 2))
        adj = torch.stack(adj, dim=0)

        pred = (score * adj.unsqueeze(dim=1).repeat(1, score.shape[1], 1, 1).float()).sum(dim=(2, 3)) / adj.sum(
            dim=(1, 2)).unsqueeze(dim=1).float()
        res["pred"] = pred
        if relation_label is not None:
            loss = self.loss_fn(score, adj, relation_label)
            self.f1(pred, relation_label)
            res["loss"] = loss
        return res

    def get_metrics(self, reset: bool = False) -> Dict[str, float]:
        metrics = self.f1.get_metric(reset)

        return metrics
