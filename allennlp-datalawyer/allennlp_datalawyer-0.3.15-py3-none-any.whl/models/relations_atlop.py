from typing import Dict, Optional, List, Any

from overrides import overrides

from collections import defaultdict

from opt_einsum import contract

import numpy as np

import torch
from torch import nn as nn
from torch.nn.functional import softmax

from allennlp.common import cached_transformers
from allennlp.data import Vocabulary, TextFieldTensors
from allennlp.modules import Seq2SeqEncoder, Seq2VecEncoder, TextFieldEmbedder
from allennlp.models.model import Model
import allennlp.nn.util as util
from allennlp.nn.util import get_token_ids_from_text_field_tensors
from allennlp.training.metrics import CategoricalAccuracy, FBetaMeasure, F1Measure

from allennlp_datalawyer.models.atlop_loss import ATLoss
from allennlp_datalawyer.data.dataset_readers.relations import NO_RELATION_LABEL


@Model.register('relations_atlop')
class RelationsATLOPModel(Model):

    def __init__(self,
                 vocab: Vocabulary,
                 transformer_model_name: str = 'neuralmind/bert-base-portuguese-cased',
                 additional_tokens_added: int = 0,
                 dropout: Optional[float] = None,
                 block_size: int = 64,
                 num_labels=-1) -> None:
        super().__init__(vocab)

        self.transformer_model = cached_transformers.get(transformer_model_name, True)

        if additional_tokens_added > 0:
            self.transformer_model.resize_token_embeddings(
                self.transformer_model.get_input_embeddings().num_embeddings + additional_tokens_added
            )

        self.relations_size = vocab.get_vocab_size('labels')
        self.entities_size = vocab.get_vocab_size('entities_labels')

        if dropout and dropout > 0:
            self._dropout = torch.nn.Dropout(dropout)
        else:
            self._dropout = None

        self._loss = ATLoss()

        self.block_size = block_size
        self.num_labels = num_labels
        self.embedding_size = self.transformer_model.config.hidden_size

        self.head_extractor = nn.Linear(2 * self.embedding_size, self.embedding_size)
        self.tail_extractor = nn.Linear(2 * self.embedding_size, self.embedding_size)
        self.bilinear = nn.Linear(self.embedding_size * block_size, self.relations_size)

        labels = list(self.vocab.get_token_to_index_vocabulary('labels').values())[1:]

        self._label_f1_metrics: Dict[str, F1Measure] = {}
        for i in range(self.relations_size):
            self._label_f1_metrics[
                vocab.get_token_from_index(index=i, namespace="labels")
            ] = F1Measure(positive_label=i)

        self.metrics = {
            "accuracy": CategoricalAccuracy(),
            "fbeta-micro": FBetaMeasure(average='micro', labels=labels),
            "fbeta-weighted": FBetaMeasure(average='weighted', labels=labels)
        }

    def forward(  # type: ignore
            self,
            context: TextFieldTensors,
            entities_spans: torch.LongTensor,
            heads: torch.LongTensor,
            tails: torch.LongTensor,
            labels: torch.LongTensor = None,
            metadata: List[Dict[str, Any]] = None,
    ) -> Dict[str, torch.Tensor]:

        mask = context['tokens']['mask']

        transformer_output = self.transformer_model(input_ids=context['tokens']['token_ids'],
                                                    attention_mask=mask.float(),
                                                    output_attentions=True)
        embedded_text = transformer_output[0]
        attention = transformer_output[-1][-1]  # 12 cabeças de atenção da última camada

        entities_spans = entities_spans.cpu().numpy()
        heads = heads.cpu().numpy()
        tails = tails.cpu().numpy()

        def get_one_hot(targets, nb_classes):
            if type(targets) == list:
                targets = np.array(targets)
            res = np.eye(nb_classes)[np.array(targets).reshape(-1)]
            return res.reshape(list(targets.shape) + [nb_classes])

        if labels is not None:
            one_hot_labels = labels.cpu().numpy().tolist()
            trim_labels = lambda labels_list: [label for label in labels_list if label > -1]
            one_hot_labels = [get_one_hot(trim_labels(labels_list), self.relations_size) for labels_list in
                              one_hot_labels]
            one_hot_labels = [item for sublist in one_hot_labels for item in sublist]

        heads_embeddings, tails_embeddings, relations_embeddings = self.get_heads_relations_tails_embeddings(
            embedded_text, attention, entities_spans, heads, tails
        )

        if self._dropout:
            heads_embeddings = self._dropout(heads_embeddings)
            tails_embeddings = self._dropout(tails_embeddings)
            relations_embeddings = self._dropout(relations_embeddings)

        heads_embeddings = torch.tanh(self.head_extractor(torch.cat([heads_embeddings, relations_embeddings], dim=1)))
        tails_embeddings = torch.tanh(self.tail_extractor(torch.cat([tails_embeddings, relations_embeddings], dim=1)))
        b1 = heads_embeddings.view(-1, self.embedding_size // self.block_size, self.block_size)
        b2 = tails_embeddings.view(-1, self.embedding_size // self.block_size, self.block_size)
        bl = (b1.unsqueeze(3) * b2.unsqueeze(2)).view(-1, self.embedding_size * self.block_size)
        logits = self.bilinear(bl)

        predicted_labels = self._loss.get_label(logits, num_labels=self.num_labels)

        output_dict = {"logits": logits,
                       "probabilities": softmax(logits, dim=-1),
                       "predicted_labels": predicted_labels,
                       "relation": [relation for data in metadata for relation in data["relations"]]}

        if labels is not None:
            one_hot_labels = torch.tensor(one_hot_labels, dtype=torch.float32,
                                          device=labels.device)
            gold_labels = one_hot_labels.argmax(dim=1)
            loss = self._loss(logits.float(), one_hot_labels.float())
            output_dict["loss"] = loss

            for i in range(self.relations_size):
                metric = self._label_f1_metrics[self.vocab.get_token_from_index(index=i, namespace="labels")]
                metric(predicted_labels, gold_labels)

            self.metrics['accuracy'](predicted_labels, gold_labels)
            self.metrics['fbeta-weighted'](predicted_labels, gold_labels)

        return output_dict

    def get_heads_relations_tails_embeddings(self, embedded_text, attention, entities_spans, heads, tails):
        batch_size, attention_heads_size, _, sequence_length = attention.size()
        heads_embeddings, tails_embeddings, relations_embeddings = [], [], []
        for batch_idx, batch_spans in enumerate(entities_spans):
            embeddings_per_start_end_idx, attention_per_start_end_idx = dict(), dict()
            for entity_idx, entity_span in enumerate(batch_spans):
                start, end = entity_span
                if start > -1 and end > -1:
                    entity_embeddings = embedded_text[batch_idx, start:end]
                    entity_attention = attention[batch_idx, :, start:end]
                    if end - start > 1:
                        entity_embeddings = torch.logsumexp(entity_embeddings, dim=0)
                        entity_attention = entity_attention.transpose(1, 0).mean(0)
                    else:
                        entity_embeddings = entity_embeddings.squeeze(dim=0)
                        entity_attention = entity_attention.squeeze(dim=1)
                    embeddings_per_start_end_idx[(start, end)] = entity_embeddings
                    attention_per_start_end_idx[(start, end)] = entity_attention

            relations_heads = heads[batch_idx]
            relations_tails = tails[batch_idx]

            head_embeddings, tail_embeddings, head_attentions, tail_attentions, hts = [], [], [], [], []
            for relation_head, relation_tail in zip(relations_heads, relations_tails):
                relation_head = tuple(relation_head)
                relation_tail = tuple(relation_tail)
                if relation_head != (-1, -1) and relation_tail != (-1, -1):
                    head_embeddings.append(embeddings_per_start_end_idx[relation_head])
                    tail_embeddings.append(embeddings_per_start_end_idx[relation_tail])
                    head_attentions.append(attention_per_start_end_idx[relation_head])
                    tail_attentions.append(attention_per_start_end_idx[relation_tail])

            head_embeddings = torch.stack(head_embeddings, dim=0)
            tail_embeddings = torch.stack(tail_embeddings, dim=0)
            head_attentions = torch.stack(head_attentions, dim=0)
            tail_attentions = torch.stack(tail_attentions, dim=0)
            head_tail_attentions = (head_attentions * tail_attentions).mean(1)
            head_tail_attentions = head_tail_attentions / (head_tail_attentions.sum(1, keepdim=True) + 1e-5)
            relation_embeddings = contract("ld,rl->rd", embedded_text[batch_idx], head_tail_attentions)

            heads_embeddings.append(head_embeddings)
            tails_embeddings.append(tail_embeddings)
            relations_embeddings.append(relation_embeddings)

        heads_embeddings = torch.cat(heads_embeddings, dim=0)
        tails_embeddings = torch.cat(tails_embeddings, dim=0)
        relations_embeddings = torch.cat(relations_embeddings, dim=0)
        return heads_embeddings, relations_embeddings, tails_embeddings

    @overrides
    def get_metrics(self, reset: bool = False) -> Dict[str, float]:
        metrics_to_return = {'accuracy': self.metrics['accuracy'].get_metric(reset)}
        for name, value in self.metrics['fbeta-weighted'].get_metric(reset).items():
            metrics_to_return['fbeta-weighted' + '-' + name] = value
        sum_f1 = 0.0
        for name, metric in self._label_f1_metrics.items():
            for metric_name, metric_value in metric.get_metric(reset).items():
                metrics_to_return[name + '-' + metric_name] = metric_value
                if metric_name == 'f1' and name != NO_RELATION_LABEL:
                    sum_f1 += metric_value
        metrics_to_return['f1'] = sum_f1 / (self.relations_size - 1)
        return metrics_to_return

    @overrides
    def make_output_human_readable(
            self, output_dict: Dict[str, torch.Tensor]
    ) -> Dict[str, torch.Tensor]:
        """
        Does a simple argmax over the probabilities, converts index to string label, and
        add `"label"` key to the dictionary with the result.
        """
        predictions = output_dict["predicted_labels"]
        predicted_indices = [prediction.argmax(dim=-1).item() for prediction in predictions]

        classes = []
        gold_labels = []
        for label_idx in predicted_indices:
            label_str = self.vocab.get_index_to_token_vocabulary('labels').get(label_idx, str(label_idx))
            classes.append(label_str)
        output_dict["labels"] = classes
        for label, relation in zip(classes, output_dict['relation']):
            gold_labels.append(relation.relation_type)
            relation.set_relation_type(label)
        output_dict["gold_labels"] = gold_labels

        relations_per_sentence = defaultdict(list)

        for relation in output_dict['relation']:
            relations_per_sentence[relation.sentence_id].append(relation)

        output_dict["relations_per_sentence"] = [relations for relations in relations_per_sentence.values()]

        return output_dict
