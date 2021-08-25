import os

from PIL import Image

import numpy as np
import torch
import logging

from phobos.metrics import Metrics


class Logger():
    """Logger Class

    Parameters
    ----------
    gpu : `int <https://docs.python.org/3/library/functions.html#int>`_
        gpu id
    metrics : `str <https://docs.python.org/3/library/stdtypes.html#str>`_
        metrics string.
    input_shape : `list <https://docs.python.org/3/tutorial/introduction.html#lists>`_
        list containing input shape
    image_loader : `torch.utils.data.DataLoader <https://pytorch.org/docs/stable/data.html#torch.utils.data.DataLoader>`_
        dataloader object to load image
    batch_size : `int <https://docs.python.org/3/library/functions.html#int>`_
        batch size
    log_dir : `str <https://docs.python.org/3/library/stdtypes.html#str>`_
        path to log output location
    dataset_dir : `str <https://docs.python.org/3/library/stdtypes.html#str>`_
        path to dataset location
    images_to_be_logged : `list <https://docs.python.org/3/tutorial/introduction.html#lists>`_
        list of paths for images to be logged
    polyaxon_exp : `polyaxon.tracking.Run <https://polyaxon.com/docs/experimentation/tracking/client/>`_
        polyaxon experiment

    Attributes
    ----------
    gpu : `int <https://docs.python.org/3/library/functions.html#int>`_
        gpu id
    metrics : `str <https://docs.python.org/3/library/stdtypes.html#str>`_
        metrics string.
    input_shape : `list <https://docs.python.org/3/tutorial/introduction.html#lists>`_
        list containing input shape
    image_loader : `torch.utils.data.DataLoader <https://pytorch.org/docs/stable/data.html#torch.utils.data.DataLoader>`_
        dataloader object to load image
    batch_size : `int <https://docs.python.org/3/library/functions.html#int>`_
        batch size
    log_dir : `str <https://docs.python.org/3/library/stdtypes.html#str>`_
        path to log output location
    dataset_dir : `str <https://docs.python.org/3/library/stdtypes.html#str>`_
        path to dataset location
    images_to_be_logged : `list <https://docs.python.org/3/tutorial/introduction.html#lists>`_
        list of paths for images to be logged
    polyaxon_exp : `polyaxon.tracking.Run <https://polyaxon.com/docs/experimentation/tracking/client/>`_
        polyaxon experiment

    Examples
    --------
    1. Logger Instance Creation:

    * Create a default logger instance

    >>> params = {
    ...             'gpu': -1,
    ...             'input_shape': [1, 1, 32, 32],
    ...             'dataset_dir': '/tmp/datasets/',
    ...             'log_dir': '/tmp/logs/',
    ...             'images_to_be_logged': ['0.jpg'],
    ...             'batch_size': 32,
    ...             'metrics': []
    ... }
    >>> args = Namespace(**params)
    >>> logger = Logger(image_loader=image_loader,
    ...                 gpu=args.gpu,
    ...                 log_dir=args.log_dir,
    ...                 dataset_dir=args.dataset_dir,
    ...                 images_to_be_logged=args.images_to_be_logged,
    ...                 input_shape=args.input_shape,
    ...                 batch_size=args.batch_size,
    ...                 metrics=args.metrics,
    ...                 polyaxon_exp=None) 
    
    * Create a logger instance linked to polyaxon experiment

    >>> params = {
    ...             'gpu': -1,
    ...             'input_shape': [1, 1, 32, 32],
    ...             'dataset_dir': '/tmp/datasets/',
    ...             'log_dir': '/tmp/logs/',
    ...             'images_to_be_logged': ['0.jpg', '2.jpg'],
    ...             'batch_size': 32,
    ...             'metrics': []
    ... }
    >>> args = Namespace(**params)
    >>> experiment = Run()
    >>> logger = Logger(image_loader=image_loader,
    ...                 gpu=args.gpu,
    ...                 log_dir=args.log_dir,
    ...                 dataset_dir=args.dataset_dir,
    ...                 images_to_be_logged=args.images_to_be_logged,
    ...                 input_shape=args.input_shape,
    ...                 batch_size=args.batch_size,
    ...                 metrics=args.metrics,
    ...                 polyaxon_exp=experiment) 

    2. Logger functionalities:

    * patchify : generates patches and respective locations for image passed as argument

    >>> image = np.random.rand(1, 1, 1000, 1000)
    >>> patches, locs = logger._patchify(image)
    >>> type(patches)
    numpy.ndarray
    >>> type(locs)
    list
    >>> patches.shape[0]
    1024
    >>> len(locs)
    1024
    >>> patches[0].shape
    (1,1,32,32)

    * unpatchify : stitch patches to generate a complete image

    >>> image = np.random.rand(1, 1, 1000, 1000)
    >>> patches, locs = logger._patchify(image)
    >>>
    >>> shape = [image.shape[2], image.shape[3]]
    >>> gen_image = logger._unpatchify(patches, locs, shape)
    >>> type(gen_image)
    numpy.ndarray
    >>> image.shape
    (1000, 1000)
    >>> image.dtype
    numpy.uint8

    * predict_and_log : predicts and logs output images generated from a trained model for a set of input images

    >>> class Dummy(nn.Module):
    ...     def __init__(self, n_channels, n_classes):
    ...         super(Dummy, self).__init__()
    ...         self.linear = nn.Linear(n_channels, n_classes)
    ... 
    ...     def forward(self, x):
    ...         return x[:, 0, 0:1, :, :]
    >>> model = Dummy(1, 1)
    >>> logger.predict_and_log(model, epoch=0)  # generates output images in /tmp/logs
    >>> os.listdir('/tmp/logs/')
    ['epoch_0_0.jpg','epoch_0_2.jpg']  

    .. note:: default logger instance is used for these examples.

    """

    def __init__(self,
                 gpu,
                 metrics,
                 input_shape,
                 image_loader,
                 batch_size,
                 log_dir,
                 dataset_dir,
                 images_to_be_logged,
                 polyaxon_exp=None):
        self.gpu = gpu
        self.metrics = metrics
        self.input_shape = input_shape
        self.polyaxon_exp = polyaxon_exp
        self.image_loader = image_loader
        self.batch_size = batch_size
        self.log_dir = log_dir
        self.dataset_dir = dataset_dir
        self.metrics = Metrics(polyaxon_exp=polyaxon_exp,
                               phase='log',
                               metrics_strings=self.metrics)
        self.images_to_be_logged = images_to_be_logged

    def _patchify(self, image):
        """fragments image into patches.

        Parameters
        ----------
        image : `numpy.ndarray <https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html>`_
            image array to patchify.

        Returns
        -------
        `numpy.ndarray <https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html>`_, `list <https://docs.python.org/3/tutorial/introduction.html#lists>`_
            ndarray : array of patches
            list   : list of locations from where patches are taken

        """
        logging.debug("Enter _patchify routine")
        patches, locs = [], []
        w = self.input_shape[2]
        for i in range(0, image.shape[2], w):
            for j in range(0, image.shape[3], w):
                if i + w <= image.shape[2] and j + w <= image.shape[3]:
                    patches.append(image[:, :, i:i + w, j:j + w])
                    locs.append([i, j])
        logging.debug("Exit _patchify routine")
        return np.asarray(patches), locs

    def _unpatchify(self, patches, locs, shape):
        """generates image array from patches.

        Parameters
        ----------
        patches : `list <https://docs.python.org/3/tutorial/introduction.html#lists>`_
            list of patches.
        locs : `list <https://docs.python.org/3/tutorial/introduction.html#lists>`_
            list of patch locations.
        shape : `tuple <https://docs.python.org/3/tutorial/datastructures.html#tuples-and-sequences>`_
            dimensions of final image.

        Returns
        -------
        `numpy.ndarray <https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html>`_
            image array.

        """
        logging.debug("Enter _unpatchify routine")
        output = np.zeros((shape[0], shape[1]))
        w = self.input_shape[2]
        for i in range(len(locs)):
            x, y = locs[i]
            output[x:x + w, y:y + w] = patches[i]
        logging.debug("Exit _unpatchify routine")
        return (output * 255).astype(np.uint8)

    def predict_and_log(self, model, epoch):
        """Given a trained model, predicts and logs image output from input.

        This method does the following:

        for every image in image_dir:
            create patches from image_dir
            pass each patch through model
            stitch patch outputs to get final image output
            log image output

        Parameters
        ----------
        model : `torch.nn.module <https://pytorch.org/docs/stable/generated/torch.nn.Module.html>`_
            model type for trained model
        epoch : `int <https://docs.python.org/3/library/functions.html#int>`_
            trained model's epoch.

        """
        logging.debug("Enter predict_and_log routine")
        model.eval()
        for image_path in self.images_to_be_logged:
            image = self.image_loader(os.path.join(self.dataset_dir,
                                                   image_path))
            shape = [image.shape[2], image.shape[3]]
            patches, locs = self._patchify(image)

            result = []
            for i in range(0, len(patches), self.batch_size):
                batch = torch.tensor(patches[i:i + self.batch_size])
                if self.gpu > -1:
                    batch = batch.to(self.gpu)
                preds = model(batch)
                preds = self.metrics._argmax_or_thresholding(preds).cpu().numpy()
                result.append(preds.astype(np.uint8))

            result = np.concatenate(result)

            pred_mask = self._unpatchify(result, locs, shape)

            if self.polyaxon_exp:
                self.polyaxon_exp.log_image(data=pred_mask,
                                            name=image_path.replace('/', '_'),
                                            step=epoch)

            im = Image.fromarray(pred_mask)
            im.save(os.path.join(self.log_dir,
                    'epoch_' + str(epoch) + '_' + image_path.replace('/', '_')))

        logging.debug("Exit predict_and_log routine")
