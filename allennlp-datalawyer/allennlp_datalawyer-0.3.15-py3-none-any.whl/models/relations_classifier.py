from typing import Dict, Optional, List, Any

from overrides import overrides

import torch
from torch.nn.functional import softmax

from allennlp.data import Vocabulary, TextFieldTensors
from allennlp.modules import TextFieldEmbedder
from allennlp.models.model import Model
from allennlp.training.metrics import CategoricalAccuracy, FBetaMeasure


@Model.register('relations_classifier')
class RelationsModel(Model):

    def __init__(self,
                 vocab: Vocabulary,
                 embedder: TextFieldEmbedder,
                 dropout: Optional[float] = None,
                 bce_loss: bool = True) -> None:
        super().__init__(vocab)

        self._embedder = embedder

        self.relations_size = vocab.get_vocab_size('labels')

        self.rel_classifier = torch.nn.Linear(embedder.token_embedder_tokens.config.hidden_size * 2,
                                              self.relations_size)

        if dropout:
            self._dropout = torch.nn.Dropout(dropout)
        else:
            self._dropout = None

        self.bce_loss = bce_loss
        if bce_loss:
            self.loss = torch.nn.BCEWithLogitsLoss()
        else:
            self.loss = torch.nn.CrossEntropyLoss()

        labels = list(self.vocab.get_token_to_index_vocabulary('labels').values())

        self.metrics = {
            "accuracy": CategoricalAccuracy(),
            "fbeta-macro": FBetaMeasure(average='macro', labels=labels),
            "fbeta-micro": FBetaMeasure(average='micro', labels=labels),
            "fbeta-weighted": FBetaMeasure(average='weighted', labels=labels)
        }

    def forward(  # type: ignore
            self,
            context: TextFieldTensors,
            head: torch.IntTensor,
            tail: torch.IntTensor,
            labels: torch.LongTensor = None,
            metadata: List[Dict[str, Any]] = None,
    ) -> Dict[str, torch.Tensor]:

        embedded_text_input = self._embedder(context)

        indices = torch.arange(context['tokens']['token_ids'].size()[0])
        head_state = embedded_text_input[indices, head.squeeze(-1)]
        tail_state = embedded_text_input[indices, tail.squeeze(-1)]
        state = torch.cat((head_state, tail_state), 1)  # (batch_size, hidden_size*2)

        if self._dropout:
            state = self._dropout(state)

        logits = self.rel_classifier(state)
        if self.bce_loss:
            logits = logits.unsqueeze(1)

        class_probabilities = softmax(logits, dim=-1)

        output_dict = {"logits": logits,
                       "probabilities": class_probabilities}

        if "relation" in metadata[0]:
            output_dict["relation"] = [data["relation"] for data in metadata]
        if "data_item" in metadata[0]:
            output_dict["data_item"] = [data["data_item"] for data in metadata]

        if labels is not None:
            if self.bce_loss:
                relation_labels = torch.zeros([labels.shape[0], self.relations_size], dtype=torch.float32,
                                              device=labels.device)
                relation_labels.scatter_(1, labels.unsqueeze(1), 1)
                relation_labels = relation_labels.unsqueeze(1)
            else:
                relation_labels = labels

            loss = self.loss(logits, relation_labels)
            output_dict["loss"] = loss
            self.metrics['accuracy'](logits.view(logits.shape[0], -1), labels)
            self.metrics['fbeta-macro'](class_probabilities.view(logits.shape[0], -1), labels)
            self.metrics['fbeta-micro'](class_probabilities.view(logits.shape[0], -1), labels)
            self.metrics['fbeta-weighted'](class_probabilities.view(logits.shape[0], -1), labels)

        return output_dict

    @overrides
    def get_metrics(self, reset: bool = False) -> Dict[str, float]:
        metrics_to_return = {'accuracy': self.metrics['accuracy'].get_metric(reset)}
        for metric in ['fbeta-macro', 'fbeta-micro', 'fbeta-weighted']:
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
        if self.bce_loss:
            predictions_list = [predictions[i] for i in range(predictions.shape[0])]
        else:
            # deve ser diferente
            predictions_list = [predictions[i] for i in range(predictions.shape[0])]

        probabilities = []
        classes = []
        gold_labels = []
        for prediction in predictions_list:
            label_idx = prediction.argmax(dim=-1).item()
            probabilities.append(prediction.max(dim=-1)[0].item())
            classes.append(self.vocab.get_index_to_token_vocabulary('labels').get(label_idx, str(label_idx)))
        output_dict["labels"] = classes
        if "relation" in output_dict:
            for label, relation in zip(classes, output_dict['relation']):
                gold_labels.append(relation.relation_type)
                relation.set_relation_type(label)
        elif "data_item" in output_dict:
            for item in output_dict["data_item"]:
                gold_labels.append(item["relation"])
        output_dict["gold_labels"] = gold_labels
        output_dict["probabilities"] = probabilities
        return output_dict

    default_predictor = "cp_relations_predictor"
