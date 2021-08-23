from typing import Dict, Optional, List, Any

from overrides import overrides

import torch
from torch import nn as nn
from torch.nn.functional import softmax

from allennlp.data import Vocabulary, TextFieldTensors
from allennlp.models.heads import Head
from allennlp.training.metrics import CategoricalAccuracy, FBetaMeasure


def get_token(h: torch.tensor, x: torch.tensor, token: int):
    """ Get specific token embedding (e.g. [CLS]) """
    emb_size = h.shape[-1]

    token_h = h.view(-1, emb_size)
    flat = x.contiguous().view(-1)

    # get contextualized embedding of given token
    token_h = token_h[flat == token, :]

    return token_h


def batch_index(tensor, index):
    if tensor.shape[0] != index.shape[0]:
        raise Exception('tensor and index shapes are not the same: %s and %s' % (tensor.shape[0], index.shape[0]))

    return torch.stack([tensor[i][index[i]] for i in range(index.shape[0])])


def get_entities_features(embedded_text, entity_masks):
    """
    O shape do embedded_text é: [batch_size, sequence_length, embeddings_size]
    O shape do entity_masks é: [batch_size, 2, sequence_length], sendo o 2 correspondente a uma máscara para cada span
    de entidade que forma a relação.
    Este método faz o unsqueeze criando uma última dimensão para as máscaras. Este unsqueeze transforma cada vetor de
    tamanho sequence_length em sequence_length vetores de tamanho 1, que são booleanos. Em seguida, onde aos vetores que
    possuem valores falsos (posições de tokens que não fazem parte do span de alguma entidade) são atribuídos valores
    extremamente negativos.
    Em seguida, cada um dos embeddings do embedded_text é replicado para cada span das entidades, de forma que é criado
    um vetor de shape [batch_size, 2, sequence_length, embeddings_size].
    Este vetor de valores extremamente negativos a partir das máscaras é somado ao tensor redimensionado.
    O retorno é feito a partir de um max pooling dos embeddings de cada token da sequência pra cada span. Então, para
    cada sentença do batch, para cada span da sentença, agrega-se o valor máximo para cada token do span, retornando
    um tensor de shape [batch_size, 2, embeddings_size], sendo este embedding o resultado desta agregação.
    """
    # max pool entity candidate spans
    m = (entity_masks.unsqueeze(-1) == 0).float() * (-1e30)
    entity_spans_pool = m + embedded_text.unsqueeze(1).repeat(1, entity_masks.shape[1], 1, 1)
    return entity_spans_pool.max(dim=2)[0]


@Head.register('relations_head')
class RelationsHead(Head):

    def __init__(self,
                 vocab: Vocabulary,
                 embedding_dim: int,
                 dropout: Optional[float] = None,
                 label_namespace: str = "relations-labels",
                 entities_label_namespace: str = "ner-labels") -> None:
        super().__init__(vocab)

        self.label_namespace = label_namespace
        self.relations_size = self.vocab.get_vocab_size(label_namespace)
        self.entities_size = self.vocab.get_vocab_size(entities_label_namespace)

        self.rel_classifier = nn.Linear(embedding_dim * 3, self.relations_size)

        if dropout:
            self._dropout = torch.nn.Dropout(dropout)
        else:
            self._dropout = None

        self._loss = torch.nn.BCEWithLogitsLoss()

        labels = list(self.vocab.get_token_to_index_vocabulary(label_namespace).values())[1:]

        self.metrics = {
            "accuracy": CategoricalAccuracy(),
            "fbeta-micro": FBetaMeasure(average='micro', labels=labels),
            "fbeta-weighted": FBetaMeasure(average='weighted', labels=labels)
        }

    def forward(  # type: ignore
            self,
            encoded_text: torch.Tensor,
            encoded_text_mask: torch.Tensor,
            head: torch.IntTensor,
            tail: torch.IntTensor,
            labels: torch.LongTensor = None,
            metadata: List[Dict[str, Any]] = None,
    ) -> Dict[str, torch.Tensor]:

        context_size = encoded_text_mask.shape[1]

        def create_entity_mask(start, end, context_size):
            mask = torch.zeros(context_size, dtype=torch.bool, device=head.device)
            mask[start:end] = 1
            return mask

        # Create a mask for the text to mask out tokens that are not entities.
        # shape: (batch_size, sequence_length)
        entities_masks = []
        relations_masks = torch.zeros_like(encoded_text_mask, dtype=torch.bool)
        for i, entity_mask in enumerate(relations_masks):
            entities_mask = []
            head_span = head[i]
            tail_span = tail[i]
            entity_mask[head_span[0]:head_span[1]] = 1
            entity_mask[tail_span[0]:tail_span[1]] = 1
            entities_mask.append(create_entity_mask(head_span[0], head_span[1], context_size))
            entities_mask.append(create_entity_mask(tail_span[0], tail_span[1], context_size))
            entities_masks.append(torch.stack(entities_mask))

        entities_masks = torch.stack(entities_masks)
        relations_masks = relations_masks.unsqueeze(1)

        logits = self._forward_relations_classifier(embedded_context=encoded_text,
                                                    entities_masks=entities_masks,
                                                    relations_masks=relations_masks)

        class_probabilities = softmax(logits, dim=-1)

        output_dict = {"logits": logits,
                       "probabilities": class_probabilities,
                       "relation": [data["relation"] for data in metadata]}

        if labels is not None:
            relation_labels = torch.zeros([labels.shape[0], self.relations_size], dtype=torch.float32,
                                          device=labels.device)
            relation_labels.scatter_(1, labels.unsqueeze(1), 1)
            # relation_labels = relation_labels[:, 1:]  # all zeros for 'none' relation
            relation_labels = relation_labels.unsqueeze(1)

            # loss = self._loss(logits, relation_label_onehot.long().view(-1))
            loss = self._loss(logits, relation_labels)
            output_dict["loss"] = loss
            self.metrics['accuracy'](logits.view(logits.shape[0], -1), labels)
            # self.metrics['fbeta-micro'](class_probabilities.view(logits.shape[0], -1), relation_label)
            self.metrics['fbeta-weighted'](class_probabilities.view(logits.shape[0], -1), labels)

        return output_dict

    def _forward_relations_classifier(self,
                                      embedded_context: torch.tensor,
                                      entities_masks: torch.tensor,
                                      relations_masks: torch.tensor):
        # get contextualized token embeddings from last transformer layer
        # batch_size = entities_masks.shape[0]

        # classify entities
        entity_spans_pool = get_entities_features(embedded_context, entities_masks)

        # classify relations
        h_large = embedded_context.unsqueeze(1).repeat(1, relations_masks.shape[1], 1, 1)

        # obtain relation logits
        # classify relation candidates
        rel_clf_logits = self._classify_relations(entity_spans_pool, relations_masks, h_large)

        return rel_clf_logits

    def _classify_relations(self, entity_spans, relations_masks, h):
        """
        O shape de entity_spans é [batch_size, 2, embeddings_size], sendo o 2 correspondente a um embedding para cada
        span de entidade que forma a relação.
        O shape de relations_masks é [batch_size, 1, sequence_length]
        O shape de h é [batch_size, 1, sequence_length, embeddings_size], sendo o 1 correspondente a uma representação
        para a relação.
        Primeiro, este método reorganiza o entity_spans para produzir uma representação de shape [batch_size, 1,
        embeddings_size * 2], colocando em um vetor só as representações de cada span.
        Em seguida, faz-se o unsqueeze criando uma última dimensão para as máscaras. Este unsqueeze transforma cada
        vetor de tamanho sequence_length em sequence_length vetores de tamanho 1, que são booleanos. Em seguida aos
        vetores que possuem valores falsos (posições de tokens que não fazem parte do span de alguma entidade) são
        atribuídos valores extremamente negativos.
        Este vetor de valores extremamente negativos a partir das máscaras é somado ao tensor h, criando uma nova
        representação reforçada a partir da máscara.
        Nesta nova representação é feito um max pooling dos embeddings de cada token da sequência da relação. Então,
        para cada sentença do batch, para a relação em questão da sentença, agrega-se o valor máximo para cada token dos
        spans, resultando em um tensor de shape [batch_size, 1, embeddings_size], sendo este embedding o resultado desta
        agregação.
        Em seguida, é feita uma concatenação entre as representações por pares de entidades (entity_pairs) e as
        relações, resultando em um embedding de shape [batch_size, 1, embeddings_size * 3], no qual é aplicado dropout.
        Esta última representação é aplicada em um classificador e os logits são retornados.
        """
        batch_size = relations_masks.shape[0]
        # get pairs of entity candidate representations
        entity_pairs = entity_spans.view(batch_size, relations_masks.shape[1], -1)

        # relation context (context between entity candidate pair)
        # mask non entity candidate tokens
        m = ((relations_masks == 0).float() * (-1e30)).unsqueeze(-1)
        rel_ctx = m + h
        # max pooling
        rel_ctx = rel_ctx.max(dim=2)[0]
        # set the context vector of neighboring or adjacent entity candidates to zero
        # Zera os embeddings de qualquer relação que não tenha nenhum span, de acordo com a máscara
        rel_ctx[relations_masks.to(torch.uint8).any(-1) == 0] = 0

        # create relation candidate representations including context, max pooled entity candidate pairs
        # and corresponding size embeddings
        rel_repr = torch.cat([rel_ctx, entity_pairs], dim=2)
        if self._dropout:
            rel_repr = self._dropout(rel_repr)

        # classify relation candidates
        chunk_rel_logits = self.rel_classifier(rel_repr)
        return chunk_rel_logits

    @overrides
    def get_metrics(self, reset: bool = False) -> Dict[str, float]:
        metrics_to_return = {'accuracy': self.metrics['accuracy'].get_metric(reset)}
        for metric in ['fbeta-weighted']:
            for name, value in self.metrics[metric].get_metric(reset).items():
                metrics_to_return[metric + '-' + name] = value
        return metrics_to_return

    @overrides
    def make_output_human_readable(
            self, output_dict: Dict[str, torch.Tensor]
    ) -> Dict[str, torch.Tensor]:
        """
        Does a simple argmax over the probabilities, converts index to string label, and
        add `"label"` key to the dictionary with the result.
        """
        predictions = output_dict["probabilities"]
        predictions_list = [predictions[i][0] for i in range(predictions.shape[0])]

        classes = []
        gold_labels = []
        for prediction in predictions_list:
            label_idx = prediction.argmax(dim=-1).item()
            label_str = self.vocab.get_index_to_token_vocabulary('labels').get(label_idx, str(label_idx))
            classes.append(label_str)
        output_dict["labels"] = classes
        for label, relation in zip(classes, output_dict['relation']):
            gold_labels.append(relation.relation_type)
            relation.set_relation_type(label)
        output_dict["gold_labels"] = gold_labels
        return output_dict
