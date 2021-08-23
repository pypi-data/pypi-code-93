from .scheduler import get_scheduler
from .optimizer import get_optimizer
from torch.autograd import Variable
from torch.utils.data.distributed import DistributedSampler
from phobos.loss import get_loss
from phobos.metrics.metrics import Metrics
from torch.utils.tensorboard import SummaryWriter

import torch
import logging
import os
import torch.distributed as dist
import tqdm
import math


class Runner():
    """Runner class.

    Parameters
    ----------
    model : `torch.nn.module <https://pytorch.org/docs/stable/generated/torch.nn.Module.html>`_
        model to train or validate.
    device : `torch.device <https://pytorch.org/docs/stable/tensor_attributes.html#torch.torch.device>`_
        device to move tensors to.
    criterion : `str <https://docs.python.org/3/library/stdtypes.html#str>`_ / `torch.nn.module <https://pytorch.org/docs/stable/generated/torch.nn.Module.html>`_
        criterion/loss for model. Details of phobos supported criteria `here <phobos.loss.html>`_
    train_loader : `torch.utils.data.DataLoader <https://pytorch.org/docs/stable/data.html#torch.utils.data.DataLoader>`_
        dataloader to load training dataset.
    val_loader : `torch.utils.data.DataLoader <https://pytorch.org/docs/stable/data.html#torch.utils.data.DataLoader>`_
        dataloader to load validation dataset.
    distributed : `boolean <https://docs.python.org/3/library/functions.html#bool>`_
        flag to create runner in distributed mode
    val_node : `int <https://docs.python.org/3/library/functions.html#int>`_
        validation step node if args.distributed=True, -1 for distributed val step
    metrics : `list <https://docs.python.org/3/tutorial/introduction.html#lists>`_ / `phobos.metrics.Metrics <https://phobos.granular.ai/phobos.metrics.html#phobos.metrics.Metrics>`_
        metrics string. Details of phobos supported metrics `here <phobos.metrics.map.html>`_
    optimizer : `str <https://docs.python.org/3/library/stdtypes.html#str>`_ / `torch.optim <https://pytorch.org/docs/stable/optim.html>`_
        optimizer string / instance. Details of phobos supported optimizers `here <phobos.runner.optimizers.map.html>`_
    num_classes : `int <https://docs.python.org/3/library/functions.html#int>`_
        number of classes
    loss_args : `dict <https://docs.python.org/3/tutorial/datastructures.html#dictionaries>`_
        dictionary of loss arguments
    scheduler : `str <https://docs.python.org/3/library/stdtypes.html#str>`_ / `torch.optim.lr_scheduler <https://pytorch.org/docs/stable/optim.html#how-to-adjust-learning-rate>`_
        scheduler string / instance. Details of phobos supported schedulers `here <phobos.runner.schedulers.map.html>`_
    optimizer_args : `dict <https://docs.python.org/3/tutorial/datastructures.html#dictionaries>`_
        dictionary of optimizer arguments
    scheduler_args : `dict <https://docs.python.org/3/tutorial/datastructures.html#dictionaries>`_
        dictionary of scheduler arguments
    polyaxon_exp : `polyaxon.tracking.Run <https://polyaxon.com/docs/experimentation/tracking/client/>`_
        polyaxon experiment.

    Attributes
    ----------
    device : `torch.device <https://pytorch.org/docs/stable/tensor_attributes.html#torch.torch.device>`_
        device to move tensors to.
    model : `torch.nn.module <https://pytorch.org/docs/stable/generated/torch.nn.Module.html>`_
        model to train or validate.
    criterion : `torch.nn.module <https://pytorch.org/docs/stable/generated/torch.nn.Module.html>`_
        criterion to measure loss for model.
    train_loader : `torch.utils.data.DataLoader <https://pytorch.org/docs/stable/data.html#torch.utils.data.DataLoader>`_
        dataloader to load training dataset.
    val_loader : `torch.utils.data.DataLoader <https://pytorch.org/docs/stable/data.html#torch.utils.data.DataLoader>`_
        dataloader to load validation dataset.
    optimizer : `torch.optim <https://pytorch.org/docs/stable/optim.html>`_
        optimizer instance
    scheduler : `torch.optim.lr_scheduler <https://pytorch.org/docs/stable/optim.html#how-to-adjust-learning-rate>`_
        scheduler instance
    distributed : `boolean <https://docs.python.org/3/library/functions.html#bool>`_
        flag to create runner in distributed mode
    distributed_val : `boolean <https://docs.python.org/3/library/functions.html#bool>`_
        DDP: distributed validation step if True, val_step on master node otherwise.
    train_metrics : `phobos.metrics.Metrics <https://phobos.granular.ai/phobos.metrics.html#phobos.metrics.Metrics>`_
        training metrics instance
    val_metrics : `phobos.metrics.Metrics <https://phobos.granular.ai/phobos.metrics.html#phobos.metrics.Metrics>`_
        validation metrics instance
    polyaxon_exp : `polyaxon.tracking.Run <https://polyaxon.com/docs/experimentation/tracking/client/>`_
        polyaxon experiment.
    iteration : `int <https://docs.python.org/3/library/functions.html#int>`_
        current iteration

    Examples
    --------
    Create Namespace object from a parameters dictionary

    >>> params = {
    ...     'loss': 'dice_spline',
    ...     'metrics': ['dc'],
    ...     'gpu': 0,
    ...     'input_shape': [1, 1, 32, 32],
    ...     'num_classes': 2,
    ...     'loss_args': {'alpha': 0.5, 'patch_size': 32},
    ...     'optimizer': 'sgd',
    ...     'optimizer_args': {'lr': 0.1},
    ...     'scheduler': 'step',
    ...     'scheduler_args': {'step_size': 30, 'gamma': 0.1},
    ...     'distributed': False,
    ...     'mode': 'epoch',
    ...     'max_iters': 2
    ... }
    >>> args = Namespace(**params)

    Create and load dummy model 

    >>> class Dummy(nn.Module):
    ...     def __init__(self, n_channels, n_classes):
    ...         super(Dummy, self).__init__()
    ...         self.linear = nn.Linear(n_channels, n_classes)
    ...
    ...     def forward(self, x):
    ...         x = self.linear(x).permute(0, 3, 1, 2)
    ...         return x
    >>>
    >>> device = torch.device('cuda',args.gpu)
    >>> model = Dummy(args.input_shape[1], 1).to(device=device)

    and dummy train and val loaders

    >>> class DummyPreloader(data.Dataset):
    ...     def __init__(self, patch_size, n_channels, n_classes, n_samples):
    ...         self.patch_size = patch_size
    ...         self.n_channels = n_channels
    ...         self.n_classes = n_classes
    ...         self.samples = n_samples
    ... 
    ...     def __getitem__(self, index):
    ...         return (np.random.rand(self.patch_size, self.patch_size, self.n_channels),
    ...                 np.ones((self.patch_size, self.patch_size)))
    ...
    ...         def __len__(self):
    ...             return self.samples
    >>>
    >>> train_set = DummyPreloader(patch_size=args.input_shape[2],
    ...                            n_channels=args.input_shape[1],
    ...                            n_classes=1,
    ...                            n_samples=5)
    >>> val_set = DummyPreloader(patch_size=args.input_shape[2],
    ...                          n_channels=args.input_shape[1],
    ...                          n_classes=16,
    ...                          n_samples=2)
    >>> train_loader = data.DataLoader(train_set,
    ...                                batch_size=2,
    ...                                shuffle=True,
    ...                                num_workers=2)
    >>> val_loader = data.DataLoader(val_set,
    ...                              batch_size=2,
    ...                              shuffle=False,
    ...                              num_workers=2)

    1. Create Runner instance using arguments from Namespace object

    >>> runner = Runner(model=model,
    ...                 device=device,
    ...                 criterion=args.loss,
    ...                 loss_args=args.loss_args,
    ...                 train_loader=train_loader,
    ...                 val_loader=val_loader,
    ...                 distributed=args.distributed,
    ...                 metrics=args.metrics,
    ...                 num_classes=args.num_classes,
    ...                 optimizer=args.optimizer,
    ...                 optimizer_args=args.optimizer_args,
    ...                 scheduler=args.scheduler,
    ...                 scheduler_args=args,scheduler_args,
    ...                 mode=args.mode,
    ...                 max_iters = args.max_iters
    ...                 )

    2. Create criterion instance using :attr:`loss` and :attr:`loss_args` to be passed for Runner instance creation

    >>> criterion = get_loss(loss_str=args.loss, loss_args=args.loss_args)
    >>> runner = Runner(model=model,
    ...                 device=device,
    ...                 criterion=criterion,
    ...                 train_loader=train_loader,
    ...                 val_loader=val_loader,
    ...                 distributed=args.distributed,
    ...                 metrics=args.metrics,
    ...                 num_classes=args.num_classes,
    ...                 optimizer=args.optimizer,
    ...                 optimizer_args=args.optimizer_args,
    ...                 mode=args.mode,
    ...                 max_iters = args.max_iters
    ...                 )


    Details of criteria/losses currently supported by phobos can be viewed `here <phobos.loss.html>`_.

    Apart from this, custom criterion (derived from :attr:`torch.nn.Module`) can also be used for Runner instance creation.

    3. Create optimizer and scheduler instances to be passed for Runner instance creation

    >>> optimizer = get_optimizer(key=args.optimizer, args=args.optimizer_args, model=model)
    >>> scheduler = get_scheduler(key=args.scheduler, args=args.scheduler_args, optimizer=optimizer)
    >>> runner = Runner(model=model,
    ...                 device=device,
    ...                 criterion=criterion,
    ...                 train_loader=train_loader,
    ...                 val_loader=val_loader,
    ...                 distributed=args.distributed,
    ...                 metrics=args.metrics,
    ...                 num_classes=args.num_classes,
    ...                 optimizer=optimizer,
    ...                 scheduler=scheduler,
    ...                 mode=args.mode,
    ...                 max_iters=args.max_iters
    ...                 )

    Details of optimizers and schedulers supported by phobos currently can be viewed `here <phobos.runner.optimizers.map.html>`_ and `here <phobos.runner.schedulers.map.html>`_ 
    
    Apart from this, custom optimizer (derived from :attr:`torch.optim`) and custom scheduler (derived from :attr:`torch.optim.lr_scheduler`) can also be passed for Runner instance creation.

    4. Create a metrics dictionary to be passed for Runner instance creation

    >>> train_metrics = Metrics(polyaxon_exp=None,
    ...                         phase='train',
    ...                         metrics_strings=args.metrics,
    ...                         num_classes=args.num_classes,
    ...                         distributed=args.distributed
    ...                         )
    >>> val_metrics   = Metrics(polyaxon_exp=None,
    ...                         phase='val',
    ...                         metrics_strings=args.metrics,
    ...                         num_classes=args.num_classes,
    ...                         distributed=args.distributed
    ...                         )
    >>> metrics = { 
    ...             'train_metrics': train_metrics,
    ...             'val_metrics': val_metrics
    ... }
    >>> runner = Runner(model=model,
    ...                 device=device,
    ...                 criterion=criterion,
    ...                 train_loader=train_loader,
    ...                 val_loader=val_loader,
    ...                 distributed=args.distributed,
    ...                 metrics=metrics,
    ...                 optimizer=optimizer,
    ...                 scheduler=scheduler,
    ...                 mode=args.mode,
    ...                 max_iters=args.max_iters
    ...                 )

    Details of metrics currently supported by phobos can be viewed `here <phobos.metrics.map.html>`_

    Apart from this, metrics instances created may also contain user defined (custom) metrics. 

    Custom metric definitions need to be added to metrics map for metrics instance creation. Click `here <phobos.metrics.html#phobos.metrics.metrics.set_metric>`_ for more details.

    Runner instance created thus is used for model training and evaluation

    >>> for step, train_metrics, eval_metrics in runner.trainer():
    ...     print(train_metrics)
    ...     print(eval_metrics)
    ...     if (not args.distributed or local_testing) or (args.distributed and dist.get_rank() == 0):
    ...         if eval_metrics['val_dc'] > best_dc:
    ...             cpt_path = os.path.join(args.weight_dir,'checkpoint_epoch_' + str(step) + '.pt')
    ...             model_dict = None
    ...             if args.distributed and not local_testing:
    ...                 model_dict = model.module.state_dict()
    ...             else:
    ...                 model_dict = model.state_dict()
    ...         
    ...             torch.save(model_dict, cpt_path)
    ...             best_dc = eval_metrics['val_dc']
    ... 
    ...             best_metrics = {**train_metrics, **eval_metrics}
    ...             if not local_testing():
    ...                 experiment.log_outputs(**best_metrics)

    """

    def __init__(self,
                 model,
                 device,
                 criterion,
                 train_loader,
                 val_loader,
                 metrics,
                 optimizer,
                 distributed=False,
                 max_iters:int = 0,
                 distributed_val=True,
                 mode = 'epoch',
                 val_frequency: int = -1,
                 tensorboard_logging:bool = True,
                 num_classes=None,
                 loss_args=None,
                 scheduler=None,
                 optimizer_args=None,
                 scheduler_args=None,
                 polyaxon_exp=None):
                 
        self.polyaxon_exp = polyaxon_exp
        self.model = model
        self.device = device

        self.train_loader = train_loader
        self.val_loader = val_loader

        self.mode = mode
        self.max_iters = max_iters

        assert mode == 'epoch' or mode == 'batch', 'Enter the correct mode epoch/batch'

        self.criterion = self.get_runner_criterion(criterion, loss_args)
        self.optimizer = self.get_runner_optimizer(optimizer, optimizer_args, model)        
        self.scheduler = self.get_runner_scheduler(scheduler, scheduler_args, self.optimizer)

        self.distributed = False
        if distributed:
            self.set_distributed_params(distributed_val=distributed_val)

        self.train_metrics, self.val_metrics = self.get_runner_metrics(metrics, num_classes)

        if self.distributed and distributed_val is False:
            assert type(self.val_loader.sampler) !=  DistributedSampler, "For single node val_step, val_loader should not have distributed sampler"
            self.val_metrics.distributed = False
        
        self.val_frequency = val_frequency
        self.tboard = None
        
        if tensorboard_logging:
            self.tensorboard_logging = True
            if polyaxon_exp:
                tensorboard_path = os.path.join(polyaxon_exp.get_artifacts_path(),'outputs/tensorboard')
            else:
                tensorboard_path = os.path.join(os.curdir,'outputs/tensorboard')
            if not os.path.exists(tensorboard_path):
                os.makedirs(tensorboard_path)
            self.tboard = SummaryWriter(log_dir=tensorboard_path)
            self.train_metrics.tboard = self.tboard
            self.val_metrics.tboard = self.tboard

    @staticmethod
    def distributed():
        """Initialize process group, default is nccl backend.

        """
        dist.init_process_group(backend='nccl')

    def set_distributed_params(self, distributed_val):
        """Set up distributed params: world size, rank, and distributed or not.

        """
        self.world_size = dist.get_world_size()
        self.rank = dist.get_rank()
        logging.info(f"{self.rank} / {self.world_size}")
        self.distributed = True
        self.distributed_val = distributed_val

    def get_runner_metrics(self, metrics, num_classes=None):
        if type(metrics) == list:
            train_metrics = Metrics(polyaxon_exp=self.polyaxon_exp,
                                    phase='train',
                                    metrics_strings=metrics,
                                    num_classes=num_classes,
                                    distributed=self.distributed
                                    )
            val_metrics   = Metrics(polyaxon_exp=self.polyaxon_exp,
                                    phase='val',
                                    metrics_strings=metrics,
                                    num_classes=num_classes,
                                    distributed=self.distributed
                                    )
            return train_metrics, val_metrics
        else:
            return metrics["train_metrics"], metrics["val_metrics"]           

    def get_runner_criterion(self, criterion, loss_args=None):
        if type(criterion) == str:
            return get_loss(loss_str=criterion, loss_args=loss_args)
        else:
            return criterion

    def get_runner_optimizer(self, optimizer, optimizer_args=None, model=None):
        if type(optimizer) == str:
            return get_optimizer(key=optimizer, args=optimizer_args, model=model)
        else:
            return optimizer

    def get_runner_scheduler(self, scheduler, scheduler_args=None, optimizer=None):
        if scheduler is not None and scheduler_args is not None:
            if type(scheduler) == str:
                return get_scheduler(key=scheduler, args=scheduler_args, optimizer=optimizer)
            else:
                return scheduler
        else:
            return None

    def tensorize_batch(self, input_tensor, label_tensor):
        """
        Tensorize batch of input images and labels, and move them to gpu.

        Parameters
        ----------
        input_tensor : `numpy.ndarray <https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html>`_
            batch of input images.
        label_tensor : `numpy.ndarray <https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html>`_
            batch of input labels.

        Returns
        -------
        input_tensor : `torch.Tensor <https://pytorch.org/docs/stable/tensors.html#torch.Tensor>`_
            input tensor loaded in gpu
        label_tensor : `torch.Tensor <https://pytorch.org/docs/stable/tensors.html#torch.Tensor>`_
            label tensor loaded in gpu

        """
        logging.debug("Enter tensorize_batch routine")
        input_tensor = Variable(input_tensor)
        label_tensor = Variable(label_tensor)

        input_tensor=input_tensor.to(device=self.device).float()
        label_tensor=label_tensor.to(device=self.device)

        logging.debug("Exit tensorize_batch routine")

        return input_tensor, label_tensor

    def train_forward_backward(self, input_tensor, label_tensor):
        """Performs forward propagation, loss evaluation
        and backward propagation while training model.

        Parameters
        ----------
        input_tensor : `torch.Tensor <https://pytorch.org/docs/stable/tensors.html#torch.Tensor>`_
            tensorised batch of input images.
        label_tensor : `torch.Tensor <https://pytorch.org/docs/stable/tensors.html#torch.Tensor>`_
            tensorised batch of input labels.

        Returns
        -------
        prediction_tensor : `torch.Tensor <https://pytorch.org/docs/stable/tensors.html#torch.Tensor>`_
            output/prediction tensor from model.
        loss : `torch.nn.module <https://pytorch.org/docs/stable/generated/torch.nn.Module.html>`_
            forward propagation loss

        """
        # Zero the gradient
        logging.debug("Enter train_forward_backward routine")
        self.optimizer.zero_grad()

        # Get model predictions, calculate loss, backprop
        prediction_tensor = self.model(input_tensor)
        loss = self.criterion(prediction_tensor, label_tensor)
        loss.backward()
        self.optimizer.step()
        logging.debug("Exit train_forward_backward routine")

        return prediction_tensor, loss

    def eval_forward(self, input_tensor, label_tensor):
        """Performs forward propagation while evaluating model.

        Parameters
        ----------
        input_tensor : `torch.Tensor <https://pytorch.org/docs/stable/tensors.html#torch.Tensor>`_
            tensorised batch of input images.
        label_tensor : `torch.Tensor <https://pytorch.org/docs/stable/tensors.html#torch.Tensor>`_
            tensorised batch of input labels.

        Returns
        -------
        prediction_tensor : `torch.Tensor <https://pytorch.org/docs/stable/tensors.html#torch.Tensor>`_
            output/prediction tensor from model.
        loss : `torch.nn.module <https://pytorch.org/docs/stable/generated/torch.nn.Module.html>`_
            forward propagation loss

        """
        # Get predictions and calculate loss
        logging.debug("Enter eval_forward routine")
        if self.distributed and not self.distributed_val:
            prediction_tensor = self.model.module(input_tensor)
        else:
            prediction_tensor = self.model(input_tensor)
        loss = self.criterion(prediction_tensor, label_tensor)
        logging.debug("Exit eval_forward routine")

        return prediction_tensor, loss

    def eval_model(self,step):
        """Evaluates model.

        Parameters
        ----------
        step : `int <https://docs.python.org/3/library/functions.html#int>`_
            training step.

        Returns
        -------
        `dict <https://docs.python.org/3/tutorial/datastructures.html#dictionaries>`_
            dictionary of evaluation metrics.

        """
        self.model.eval()
        
        if self.distributed and not self.distributed_val and dist.get_rank() != 0:
            return {}

        logging.debug("Enter eval_model routine")
        with torch.no_grad():
            for (input_tensor, label_tensor) in self.val_loader:
                input_tensor, label_tensor = self.tensorize_batch(input_tensor, label_tensor)

                prediction_tensor, loss = self.eval_forward(
                    input_tensor, label_tensor)

                self.val_metrics.compute(prediction_tensor, label_tensor, loss)

                # clear batch variables from memory
                del input_tensor, label_tensor

        metrics = self.val_metrics.crunch_it(step)

        if self.scheduler:
            self.scheduler.step(metrics['val_loss'])
        logging.debug("Exit eval_model routine")

        return metrics

    def getContextIterationValue(self,x):
        val = x//self.train_loader.batch_size
        if self.train_loader.drop_last:
            val += math.ceil(x/self.train_loader.batch_size - x//self.train_loader.batch_size)
        return val

    def logResults(self,step):
        val_metrics = None
        if self.distributed:
            val_metrics = self.eval_model(step)
            self.val_metrics.reset()
            dist.barrier()
        else:
            val_metrics = self.eval_model(step)
            self.val_metrics.reset()
        return val_metrics
        
    def condRun(self,iteration,epoch):
        if self.mode == 'epoch' and epoch < self.max_iters:
            return True
        elif self.mode == 'batch' and iteration < self.max_iters:
            return True
        return False

    def trainer(self):
        """Trains model.

        Returns
        -------
        `dict <https://docs.python.org/3/tutorial/datastructures.html#dictionaries>`_
            dictionary of training metrics.

        """
        logging.debug("Enter train_model generator")

        train_metrics, val_metrics = None,None
        iteration,epoch = 0,0

        while  self.condRun(iteration,epoch):
            epoch += 1
            for input_tensor, label_tensor in self.train_loader:
                iteration += 1
                # batch train
                self.model.train()

                input_tensor, label_tensor = self.tensorize_batch(
                    input_tensor, label_tensor)

                prediction_tensor, loss = self.train_forward_backward(
                    input_tensor, label_tensor)
                self.train_metrics.compute(prediction_tensor, label_tensor, loss)

                del input_tensor, label_tensor
                
                if self.mode == 'batch':
                    train_metrics = self.train_metrics.crunch_it(iteration)
                    self.train_metrics.reset()
                    if self.distributed:
                        dist.barrier()
                    # end batch train
                    logging.info(f"{iteration}/{self.max_iters} completed!")
                    if self.val_frequency != -1 and iteration % self.val_frequency == 0:
                        val_metrics = self.logResults(iteration)
                        yield iteration,train_metrics,val_metrics

                if self.mode == "batch" and not self.condRun(iteration,epoch):
                    break
                    
            if self.mode == 'epoch':
                train_metrics = self.train_metrics.crunch_it(epoch)
                self.train_metrics.reset()
                logging.info(f"{epoch}/{self.max_iters} completed!")
                if self.distributed:
                    dist.barrier()
                val_metrics = self.logResults(epoch)
                yield epoch, train_metrics, val_metrics
            elif self.mode == 'batch' and self.val_frequency == -1:
                val_metrics = self.logResults(iteration)
                yield epoch,train_metrics,val_metrics
                
        logging.debug("Exit train_model routine")
