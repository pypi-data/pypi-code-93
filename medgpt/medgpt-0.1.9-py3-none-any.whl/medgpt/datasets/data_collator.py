from typing import Any, Callable, Dict, List, NewType, Optional, Tuple, Union
import torch

InputDataClass = NewType("InputDataClass", Any)

class CollataAndPad(object):
    r''' Arrange the data into the right format + add padding or trim where necessary.

    Args:
        max_len (`int`, `optional`, defaults to -1):
            Upper bound for sequence length. If it is -1 means that it will be
            calculated for each bach and set to the max length without upper limits.
        pad_id (`int`, `optional`, defaults to 0):
            What ID will be used to pad the inputs to max_len
        shift_labels:
            If True labels = input_ids[1:] + [pad_id], else labels = input_ids, this will also
                remove the last element from each sample in input_ids.
        remap_names:
            If a dictionary the stanard output names (input_ids, labels, attention_mask) will be maped
            to whatever is in the dict.
        mlm (`float`, `optional`, defaults to None):
            Number [0, 1] - Marks the mlm probability, if it is not None tokens will be masked
        mlm_mask_id:
            ID of the token that will be used as a mask
    '''
    def __init__(self, max_len=-1, pad_id=0, shift_labels=False, remap_names=None, mlm=None, mlm_mask_id=None):
        self.max_len = max_len
        self.pad_id = pad_id
        self.shift_labels = shift_labels
        self.remap_names = remap_names
        self.mlm = mlm
        self.mlm_mask_id = mlm_mask_id


    def __call__(self, features: List[InputDataClass]) -> Dict[str, torch.Tensor]:
        batch = {}
        if self.max_len == -1:
            max_len = max([len(f['input_ids']) for f in features])
        else:
            max_len = min(self.max_len, max([len(f['input_ids']) for f in features]))

        if self.shift_labels and not 'labels' in features[0]:
            # Recalculate max_len
            max_len = min(max_len, max([len(f['input_ids'][0:-1]) for f in features]))

            # Labels do not exist and we should shift
            batch['labels'] = torch.tensor([f['input_ids'][1:max_len+1] + [-100] * max(0, max_len - len(f['input_ids']) + 1)
                                          for f in features], dtype=torch.long)

            for f in features:
                f['input_ids'] = f['input_ids'][0:-1]

        elif 'labels' in features[0]:
            # Labels already exist, just pad them with -100
            batch['labels'] = torch.tensor([f['labels'] for f in features], dtype=torch.long)


        batch['input_ids'] = torch.tensor([f['input_ids'][0:max_len] + [self.pad_id] * max(0, max_len - len(f['input_ids']))
                                          for f in features], dtype=torch.long)
        batch['attention_mask'] = batch['input_ids'] != self.pad_id

        if not self.shift_labels and not 'labels' in batch:
            # If we did not shift labels just clone
            batch['labels'] = batch['input_ids'].clone()
            batch['labels'][batch['labels'] == self.pad_id] = -100

        # If we want Masked Langauge Modeling - mask some tokens
        if self.mlm is not None:
            pass

        if self.remap_names is not None:
            batch = {self.remap_names.get(k, k):v for k,v in batch.items()}

        return batch


    def mask_tokens(self, input_ids):
        probability_matrix = torch.full(input_ids.shape, self.mlm_probability)

