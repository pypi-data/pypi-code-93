import numpy as np
from sklearn import metrics
import torch
import logging

import torch.distributed as dist
from torch.distributed import ReduceOp


from medpy.metric.binary import (dc, jc, hd, asd, assd,
                                 precision, recall, ravd,
                                 sensitivity,
                                 specificity,
                                 true_positive_rate,
                                 true_negative_rate,
                                 positive_predictive_value)
from sklearn.metrics import (f1_score, precision_score, recall_score)

from .mIoU_and_SeK import mIoU, SeK
from .multilabel import emr, hamming
from .accuracy import Acc
from copy import deepcopy


metrics_map = {
    'dc': dc,
    'jc': jc,
    'hd': hd,
    'asd': asd,
    'assd': assd,
    'prec': precision,
    'recall': recall,
    'sensi': sensitivity,
    'speci': specificity,
    'ravd': ravd,
    'tpr': true_positive_rate,
    'tnr': true_negative_rate,
    'ppv': positive_predictive_value,
    'mc-prec': precision_score,
    'mc-recall': recall_score,
    'mc-f1-score': f1_score,
    'ml-prec': precision_score,
    'ml-recall': recall_score,
    'ml-emr': emr,
    'ml-hamming': hamming,
    'mIoU': mIoU,
    'SeK': SeK,
    'acc': Acc
}

metrics_argmax_required = [
    'dc',
    'jc',
    'hd',
    'asd',
    'assd',
    'prec',
    'recall',
    'sensi',
    'speci',
    'ravd',
    'tpr',
    'tnr',
    'ppv',
    'mc-prec',
    'mc-recall',
    'mc-f1-score',
    'ml-prec',
    'ml-recall',
    'ml-emr',
    'ml-hamming',
    'mIoU',
    'SeK',
    'acc'
]


def set_metric(key, metric, argmax_required=False):
    """Allows: 

    * Addition of a new metric to metrics map

    * Modification of existing metric definitions in metrics map

    Parameters
    ----------
    key : `str <https://docs.python.org/3/library/stdtypes.html#str>`_
        type of metric instance
    metric : `func <https://docs.python.org/3/tutorial/classes.html#method-objects>`_
        function returning metric output

    Examples
    --------
    Add an entry for a dummy metric to metrics map

    >>> def dummyMetric():
    ...    return 1.0
    >>> key = 'dummy'
    >>> set_metric(key,dummyMetric)

    Include this key in metrics_strings list to create metrics instance

    >>> met_str = ['dc','dummy']
    >>> metrics = Metrics(metrics_strings=met_str)

    Perform metrics computations

    >>> metrics.compute(torch.tensor([0, 0, 0]), torch.tensor([0, 0, 1]),
    ...                 torch.tensor(1))
    >>> metrics.metrics['dc'] 
    0.0
    >>> metrics.metrics['dummy']
    1.0
    
    Click `here <phobos.metrics.map.html>`_ to view details of metrics supported by phobos currently. 
    """
    logging.debug("Enter set_metrics routine")
    metrics_map[key] = metric
    if argmax_required:
        metrics_argmax_required.append(key)
    logging.debug("Exit set_metrics routine")


class Metrics():
    """Metrics class.

    Parameters
    ----------
    polyaxon_exp : `polyaxon.tracking.Run <https://polyaxon.com/docs/experimentation/tracking/client/>`_
        polyaxon experiment.
    phase : `str <https://docs.python.org/3/library/stdtypes.html#str>`_
        model training phase. can be `train` or `val`
    metrics_strings : `list <https://docs.python.org/3/tutorial/introduction.html#lists>`_
        list of metrics strings to evaluate
        during model training or evaluation.
    *args : `list <https://docs.python.org/3/tutorial/introduction.html#lists>`_
        list of non keyworded arguments.
    **kwargs : `list <https://docs.python.org/3/tutorial/introduction.html#lists>`_
        list of keyworded arguments.

    Attributes
    ----------
    metrics_strings : `list <https://docs.python.org/3/tutorial/introduction.html#lists>`_
        list of metrics strings to evaluate
        during model training or evaluation.
    metric_funcs : `list <https://docs.python.org/3/tutorial/introduction.html#lists>`_
        list of functions for every metric
        in metric_strings.
    metrics : `dict <https://docs.python.org/3/tutorial/datastructures.html#dictionaries>`_
        map of evaluated metrics where
        key   : string from metrics_strings
        value : evaluated metrics.
    initialize_metrics : `func <https://docs.python.org/3/tutorial/classes.html#method-objects>`_
        method to initialise metrics map.

    Examples
    --------
    1. Metrics class computes and stores loss as well as list of metrics passed as `metrics_strings` during initializaztion:
    
    >>> metrics = Metrics(metrics_strings=['dc'])
    >>> metrics.compute(torch.tensor([0, 0, 0]), torch.tensor([0, 0, 1]),
    ...                 torch.tensor(1))
    >>> metrics.metrics['dc'] 
    0.0
    >>> metrics.metrics['loss']
    1.0

    2. If an empty list is passed during initialization, only loss is computed:

    >>> metrics = Metrics(metrics_strings=[])
    >>> metrics.compute(torch.tensor([0, 0, 0]), torch.tensor([0, 0, 1]),
    ...                 torch.tensor(1))
    >>> metrics.metrics['loss']
    1.0

    3. Computation of multiclass metrics:

    >>> metrics = Metrics(metrics_strings=['mc-prec',
    ...                                    'mc-recall',
    ...                                    'mc-f1-score'])
    >>> metrics.compute(torch.tensor([0, 1, 2, 3]), torch.tensor([0, 1, 2, 3]),
    ...                torch.tensor(1))
    >>> metrics.metrics['mc-prec'] 
    1.0
    >>> metrics.metrics['mc-recall']
    1.0
    >>> metrics.metrics['mc-f1-score'] 
    1.0
    >>> metrics.metrics['loss'] 
    1.0

    4. Computation of multilabel metrics:

    >>> metrics = Metrics(metrics_strings=['ml-prec',
    ...                                    'ml-recall',
    ...                                    'ml-emr',
    ...                                    'ml-hamming'])
    >>> metrics.compute(torch.tensor([[0, 1, 0], [0, 1, 1]]),
    ...                torch.tensor([[0, 1, 0], [0, 0, 1]]),
    ...                torch.tensor(1))
    >>> metrics.metrics['ml-prec'] 
    1.0
    >>> metrics.metrics['ml-recall'] 
    0.75
    >>> metrics.metrics['ml-emr'] 
    0.5
    >>> metrics.metrics['ml-hamming'] 
    0.16666666666666666
    >>> metrics.metrics['loss']
    1.0

    5. Metrics instance can be used for multiple metrics computations, and subsequent results are stored in the instance. 
    
    These results can be crunched to retrieve metrics statistics:

    >>> metrics = Metrics(metrics_strings=['dc'])
    >>> metrics.compute(torch.tensor([0, 0, 0]), torch.tensor([0, 0, 1]),
    ...                 torch.tensor(1))
    >>> metrics.compute(torch.tensor([0, 0, 1]), torch.tensor([0, 0, 1]),
    ...                 torch.tensor(0))
    >>> metrics_means = metrics.crunch_it(step=0)
    >>> metrics_means 
    {'dc': 0.5, 'loss': 0.5}

    6. Metrics instance state can be reset after multiple computations:

    >>> metrics = Metrics(metrics_strings=['dc'])
    >>> metrics.compute(torch.tensor([0, 0, 0]), torch.tensor([0, 0, 1]),
    ...                 torch.tensor(1))
    >>> metrics.compute(torch.tensor([0, 0, 1]), torch.tensor([0, 0, 1]),
                        torch.tensor(0))
    >>> metrics_means = metrics.crunch_it(step=0)
    >>> metrics.reset()
    >>> metrics.metrics['dc']
    []
    >>> metrics.metrics['loss']
    []
    >>> metrics_means['dc']
    0.5

    Click `here <phobos.metrics.map.html>`_ to view details of metrics supported by phobos currently. 

    Most commonly used metrics have been benchmarked, whose results can be viewed `here <phobos.metrics.benchmark.html>`_
    """

    def __init__(self,
                 polyaxon_exp=None,
                 phase='',
                 metrics_strings=['prec'],
                 num_classes=2,
                 distributed=False,
                 *args, **kwargs):
        super(Metrics, self).__init__(*args, **kwargs)
        self.polyaxon_exp = polyaxon_exp
        self.phase = phase
        self.metric_strings = metrics_strings
        self.metric_funcs = {}
        self.metrics = {}
        self.distributed = distributed
        self.multilabel = False
        self.num_classes = num_classes

        self.initialize_metrics()

    def initialize_metrics(self):
        """Initialize metrics map based on metrics in metric_strings
        
        """
        logging.debug("Initializing metrics")
        self.metrics['loss'] = []

        for metstr in self.metric_strings:
            if metstr.startswith('ml'):
                self.multilabel = True

            self.metric_funcs[metstr] = metrics_map[metstr]
            self.metrics[metstr] = []

        self.tboard = None
    
    def reset(self):
        """Reset metrics map.

        """
        logging.debug("Reset Metrics")
        for k in self.metrics.keys():
            self.metrics[k] = []

    def _transform_tensor(self, tensor):
        """Transform tensor into numpy array.

        Parameters
        ----------
        tensor : `torch.Tensor <https://pytorch.org/docs/stable/tensors.html#torch.Tensor>`_
            tensor to transform.

        Returns
        -------
        `numpy.ndarray <https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html>`_
            numpy array transformed from tensor.

        """
        logging.debug("Inside _transform_tensor routine")
        if isinstance(tensor, int):
            return tensor
        elif isinstance(tensor, torch.Tensor):
            if tensor.is_cuda:
                return tensor.data.cpu().numpy()
            else:
                return tensor.data.numpy()
        elif isinstance(tensor, np.ndarray):
            return tensor
        elif isinstance(tensor, list):
            return np.asarray(tensor)
        else:
            return tensor

    def _argmax_or_thresholding(self, tensor):
        """Performs argmax or thresholding on input tensor.

        Parameters
        ----------
        tensor : `torch.Tensor <https://pytorch.org/docs/stable/tensors.html#torch.Tensor>`_
            input tensor.

        Returns
        -------
        `torch.Tensor <https://pytorch.org/docs/stable/tensors.html#torch.Tensor>`_
            final tensor after applying transforms.

        """
        logging.debug("Enter _argmax_or_thresholding routine")
        if type(tensor) != torch.Tensor:
            raise TypeError("Input should be a torch tensor! but got "+str(type(tensor)))

        if len(tensor.size()) >= 4:
            if tensor.size(1) == 1:
                tensor = torch.squeeze(tensor, dim=1)
                tensor[tensor < 0.5] = 0
                tensor[tensor >= 0.5] = 1
            else:
                tensor = torch.argmax(tensor, dim=1)
        if len(tensor.size()) == 3:
            tensor[tensor < 0.5] = 0
            tensor[tensor >= 0.5] = 1
        if len(tensor.size()) == 2:
            if not self.multilabel:
                tensor = torch.argmax(tensor, dim=1)
            else:
                tensor[tensor < 0.5] = 0
                tensor[tensor >= 0.5] = 1

        logging.debug("Exit _argmax_or_thresholding routine")
        return tensor

    def computeMetricsOut(self,k,predicted_,target_):
        metrics_out = None

        if 'mc' in k:
            metrics_out = self.metric_funcs[k](predicted_.flatten(),
                                                        target_.flatten(),
                                                        average='micro')
        elif 'ml' in k:
            metrics_out = self.metric_funcs[k](predicted_,
                                                        target_,
                                                        average='samples')
        elif 'mIoU' in k or 'SeK' in k:
            metrics_out = self.metric_funcs[k](predicted_,
                                                        target_,
                                                        num_classes=self.num_classes)
        else:
            metrics_out = self.metric_funcs[k](predicted_,
                                                        target_)
        return metrics_out

    def compute(self, predicted, target, loss):
        """Compute loss between target and predicted tensors.

        Parameters
        ----------
        predicted : `torch.Tensor <https://pytorch.org/docs/stable/tensors.html#torch.Tensor>`_
            predicted/output tensor.
        target : `torch.Tensor <https://pytorch.org/docs/stable/tensors.html#torch.Tensor>`_
            target tensor.
        loss : `torch.Tensor <https://pytorch.org/docs/stable/tensors.html#torch.Tensor>`_
            loss tensor.

        """
        predicted = predicted.detach().cpu()
        target = target.detach().cpu()

        self.metrics['loss'].append(self._transform_tensor(loss))

        if len(self.metric_strings) > 0:

            for k in self.metric_funcs.keys():
                predicted_,target_ = deepcopy(predicted), deepcopy(target)
                if k in metrics_argmax_required:
                    predicted_ = self._argmax_or_thresholding(predicted_)
                
                try:
                    metrics_out = self.computeMetricsOut(k,predicted_,target_)
                except Exception:
                    predicted_ = self._transform_tensor(predicted_)
                    target_ = self._transform_tensor(target_)
                    metrics_out = self.computeMetricsOut(k,predicted_,target_)

                del predicted_,target_
                metrics_out = self._transform_tensor(metrics_out)
                self.metrics[k].append(metrics_out)
                logging.info("{}={}".format(k, self.metrics[k][-1]))

    def plotTensorboard(self,mean_metrics,step):
        for key in mean_metrics.keys():
            self.tboard.add_scalar(f"{self.phase}/{key}",mean_metrics[key],step)

    def crunch_it(self, step):
        """Crunch metrics to obtain mean_metrics map.

        Parameters
        ----------
        step : `int <https://docs.python.org/3/library/functions.html#int>`_
            training step.

        Returns
        -------
        `dict <https://docs.python.org/3/tutorial/datastructures.html#dictionaries>`_
            mean_metrics map.

        """
        mean_metrics = {}
        mean_metrics_rank = {}

        # compute
        for k in self.metrics.keys():
            if self.phase:
                out_key = self.phase + '_' + k
            else:
                out_key = k

            mean_metrics[out_key] = np.mean(self.metrics[k])
            if self.distributed:
                mean_metrics_rank[
                    out_key + '_' + str(dist.get_rank())
                ] = np.mean(self.metrics[k])

        # all_reduce if phase != train
        if self.distributed:
            dist.barrier()
            for k in mean_metrics.keys():
                _ = torch.tensor(mean_metrics[k]).cuda()
                dist.all_reduce(_,
                                op=ReduceOp.SUM)
                mean_metrics[k] = _.cpu().item()/ float(dist.get_world_size())
            dist.barrier()

        # logging
        for k in mean_metrics_rank.keys():
            logging.info(f"rank_{k} = {mean_metrics_rank[k]}")
        for k in mean_metrics.keys():
            logging.info(f"mean_{k} = {mean_metrics[k]}")

        if self.polyaxon_exp:
            if self.distributed:
                if dist.get_rank() == 0:
                    self.polyaxon_exp.log_metrics(step=step, **mean_metrics)
                    if self.tboard:
                        self.plotTensorboard(mean_metrics=mean_metrics,step=step)
                dist.barrier()
            else:
                self.polyaxon_exp.log_metrics(step=step, **mean_metrics)
                if self.tboard:
                    self.plotTensorboard(mean_metrics=mean_metrics,step=step)
        else:
            if self.tboard:
                self.plotTensorboard(mean_metrics=mean_metrics,step=step)
        return mean_metrics
