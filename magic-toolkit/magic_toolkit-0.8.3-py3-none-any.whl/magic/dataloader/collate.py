r""""Contains definitions of the methods used by the _BaseDataLoaderIter workers to
collate samples fetched from dataset into Tensor(s).

These **needs** to be in global scope since Py2 doesn't support serializing
static methods.
"""

import re
import numpy as np
from torch._six import container_abcs, string_classes, int_classes

def default_collate(batch):
    r"""Puts each data field into a tensor with outer dimension batch size"""

    elem = batch[0]
    elem_type = type(elem)
    if elem_type.__module__ == 'numpy' and elem_type.__name__ != 'str_' and elem_type.__name__ != 'string_':
        elem = batch[0]
        if elem_type.__name__ == 'ndarray':
            # array of string classes and object
            np_str_obj_array_pattern = re.compile(r'[SaUO]')
            if np_str_obj_array_pattern.search(elem.dtype.str) is not None:
                default_collate_err_msg_format = (
                    "default_collate: batch must contain tensors, numpy arrays, numbers, "
                    "dicts or lists; found {}")
                raise TypeError(default_collate_err_msg_format.format(elem.dtype))

            # return default_collate([torch.as_tensor(b) for b in batch])
            return batch
        elif elem.shape == ():  # scalars
            # return torch.as_tensor(batch)
            return np.array(batch)
    elif isinstance(elem, float):
        # return torch.tensor(batch, dtype=torch.float64)
        return np.array(batch, dtype=np.float64)
    elif isinstance(elem, int_classes):
        # return torch.tensor(batch)
        return np.array(batch)
    elif isinstance(elem, string_classes):
        return batch
    elif isinstance(elem, container_abcs.Mapping):
        # return {key: default_collate([d[key] for d in batch]) for key in elem}
        return {key: [d[key] for d in batch] for key in elem}
    elif isinstance(elem, tuple) and hasattr(elem, '_fields'):  # namedtuple
        return elem_type(*(default_collate(samples) for samples in zip(*batch)))
    elif isinstance(elem, container_abcs.Sequence):
        transposed = zip(*batch)
        return [default_collate(samples) for samples in transposed]

    default_collate_err_msg_format = (
        "default_collate: batch must contain tensors, numpy arrays, numbers, "
        "dicts or lists; found {}")
    raise TypeError(default_collate_err_msg_format.format(elem_type))
