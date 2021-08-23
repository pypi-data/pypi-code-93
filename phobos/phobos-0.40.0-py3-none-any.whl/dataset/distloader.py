from torch.utils.data import DataLoader
from torch.utils.data.distributed import DistributedSampler

import torch.distributed as dist


def getDistLoaders(train_dataset,val_dataset,batch_size,num_workers,distributed=True, distributed_val=True):
    """
    
    Creates distributed dataloader:-
        For train_dataset: assigns distributed sampler,
        For val_dataset: assigns distributed sampler for distributed val step i.e. args.val_node=-1, else sampler=None

    Parameters
    ----------
    train_dataset : `torch.utils.data.Dataset <https://pytorch.org/docs/stable/data.html#torch.utils.data.Dataset>`_
        train_dataset
    val_dataset : `torch.utils.data.Dataset <https://pytorch.org/docs/stable/data.html#torch.utils.data.Dataset>`_
        val_dataset
    args : `dict <https://docs.python.org/3/tutorial/datastructures.html#dictionaries>`_
        args.train
            args.train['batch_size'] : `int <https://docs.python.org/3/library/functions.html#int>`_, 
            args.train['num_workers'] : `int <https://docs.python.org/3/library/functions.html#int>`_
        args.val
            args.val['batch_size'] : `int <https://docs.python.org/3/library/functions.html#int>`_, 
            args.val['num_workers'] : `int <https://docs.python.org/3/library/functions.html#int>`_
        args.distributed : `boolean <https://docs.python.org/3/library/functions.html#bool>`_
            distributed
        args.val_node : `int <https://docs.python.org/3/library/functions.html#int>`_
            val_node
    
    Examples
    --------
    Create distributed train and val loaders from DummyPreLoader instances

    >>> def get_train_val_metadata(args):
    ...     train_metadata = [1, 2]
    ...     val_metadata = [3, 4]
    ...     return train_metadata, val_metadata
    >>> 
    >>> class DummyPreloader(torch.utils.data.Dataset):
    ...     def __init__(self, metadata, args=None):
    ...         random.shuffle(metadata)
    ...         self.samples = metadata
    ...         self.args = args
    ...
    ...     def __getitem__(self, index):
    ...         return np.random.randn(1, 32, 32), np.zeros(32, 32)
    ...
    ...     def __len__(self):
    ...         return len(self.samples)
    >>>
    >>> train_samples, val_samples = get_train_val_metadata(args)
    >>> 
    >>> train_dataset = DummyPreloader(train_samples, args)
    >>> val_dataset = DummyPreloader(val_samples, args)
    >>>
    >>> train_loader, val_loader = getDistLoaders(
    ...                                 train_dataset,
    ...                                 val_dataset,
    ...                                 batch_size=args.batch_size,
    ...                                 num_workers=args.num_workers,
    ...                                 distributed=args.distributed,
    ...                                 distributed_val=args.distributed_val
    ...                                 )
    
    """

    train_sampler,val_sampler = None,None

    if distributed:
        rank, world_size = dist.get_rank(), dist.get_world_size()
        train_sampler = DistributedSampler(
            train_dataset,
            rank = rank,
            num_replicas = world_size
        )
        if distributed_val:
            val_sampler = DistributedSampler(
                val_dataset,
                rank = rank,
                num_replicas = world_size
            )
    # loaders
    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
        sampler=train_sampler,
        pin_memory=False
    )
    val_loader = DataLoader(
        val_dataset,
        batch_size=batch_size,
        num_workers=num_workers,
        sampler=val_sampler,
        pin_memory=False
    )
    return train_loader, val_loader
