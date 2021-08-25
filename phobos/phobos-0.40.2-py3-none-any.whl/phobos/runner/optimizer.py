from torch.optim import (Adadelta, Adagrad, Adam, AdamW,
                         SparseAdam, Adamax, ASGD, LBFGS,
                         RMSprop, Rprop, SGD)
import logging

optimizer_map = {
    'adadelta': Adadelta,
    'adagrad': Adagrad,
    'adam': Adam,
    'adamw': AdamW,
    'sparseadam': SparseAdam,
    'adamax': Adamax,
    'asgd': ASGD,
    'lbfgs': LBFGS,
    'rmsprop': RMSprop,
    'rprop': Rprop,
    'sgd': SGD
}


def get_optimizer(key, args, model):
    """Creates and returns a optimizer based on optimizer type and arguments. 

    Parameters
    ----------
    key : `str <https://docs.python.org/3/library/stdtypes.html#str>`_
        type of optimizer instance
    args : `dict <https://docs.python.org/3/tutorial/datastructures.html#dictionaries>`_
        dictionary of optimizer parameters.
    model : `torch.nn.module <https://pytorch.org/docs/stable/generated/torch.nn.Module.html>`_
        model to train or validate.

    Returns
    -------
    `torch.optim <https://pytorch.org/docs/stable/optim.html>`_
        optimizer instance.

    Examples
    --------
    Create an optimizer instance using a dummy model and SGD parameters

    >>> class Dummy(nn.Module):
    ...     def __init__(self, n_channels, n_classes):
    ...         super(Dummy, self).__init__()
    ...         self.linear = nn.Linear(n_channels, n_classes)
    ...
    ...     def forward(self, x):
    ...         x = self.linear(x).permute(0, 3, 1, 2)
    ...         return x
    >>> model = Dummy(1, 1)
    >>> optim_key = 'sgd'
    >>> optim_args = {'lr': 0.1}
    >>> optimizer = get_optimizer(key=optim_key, args=optim_args, model=model)
    >>> optimizer
    SGD (
    Parameter Group 0
        dampening: 0
        lr: 0.1
        momentum: 0
        nesterov: False
        weight_decay: 0
    )

    This optimizer instance can be passed to runner for training.

    Click `here <phobos.runner.optimizers.map.html>`_ to view details of optimizers supported by phobos currently. 
    """
    logging.debug("Enter get_optimizer routine")
    optimizer = optimizer_map[key]
    args['params'] = model.parameters()
    logging.debug("Exit get_optimizer routine")
    return optimizer(**args)


def set_optimizer(key, optimizer):
    """Allows: 

    * Addition of a new optimizer to optimizer map
    
    * Modification of existing optimizer definitions in optimizer map

    Parameters
    ----------
    key : `str <https://docs.python.org/3/library/stdtypes.html#str>`_
        type of optimizer instance
    optimizer : `torch.optim <https://pytorch.org/docs/stable/optim.html>`_
        optimizer class

    Examples
    --------
    Add a dummy optimizer to optimizer map 

    >>> class DummyOptimizer(torch.optim.SGD):
    ...     def __init__(self, args):
    ...         super().__init__(**args)
    >>> key = 'dummy_sgd'
    >>> set_optimizer(key,DummyOptimizer)

    This optimizer key can be passed to runner for training.

    Click `here <phobos.runner.optimizers.map.html>`_ to view details of optimizers supported by phobos currently.
    """
    logging.debug("Enter set_optimizer routine")
    optimizer_map[key] = optimizer
    logging.debug("Exit set_optimizer routine")
