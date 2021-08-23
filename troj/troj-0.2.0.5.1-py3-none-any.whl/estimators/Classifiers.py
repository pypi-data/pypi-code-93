from art import estimators
import numpy as np
import tensorflow as tf


"""


This class is our base class that child classes will inherit metadata collection (and other functions in the future) as well as inherits from
ART's base estimator class for instantiation and attack. 
We'll have a class for major frameworks that will inherit this class

"""


class TrojClassifier(estimators.BaseEstimator):
    """
    Collects and returns the model's metadata
    :return dict: returns a dictionary of metadata related to the classifier passed to the ART estimator class
    """

    def get_classifier_meta(self):
        return {
            "model": str(self._model),
            "model_name": str(self._model.__class__.__name__),
            "input_shape": str(self._input_shape),
            "num_classes": str(self.nb_classes),
            "loss_func": str(self._loss),
            "channels_first": str(self._channels_first),
        }


"""
Inherits from the troj base class and the ART tensorflow v1 classifier for tf1 support
Also implements our ComputeLoss function which will be called by each classifier, should implement as abstract method in base class
"""


class TrojTF1Classifier(estimators.classification.TensorFlowClassifier, TrojClassifier):
    from art.estimators.classification import TensorFlowClassifier

    """
    Compute loss computes the loss over a batch of target samples
    :param x: inputs
    :param y: labels, either true labels or original unperturbed model labels. y might need to be expanded along
    the first dimension because of art bug.
    :param return_preds: bool to return model predictions with loss
    :return: Loss values and optionally predictions
    """

    def ComputeLoss(self, x, y, return_preds=True):
        try:
            import tensorflow.compat.v1 as tf
        except:
            import tensorflow as tf
        from numpy import array

        # import tensorflow as tf
        # print("loss fn")
        shape = (y.size, 10)
        one_hot = np.zeros(shape)
        losses = np.array([])
        for sample in x:
            image = np.expand_dims(sample, axis=0)
            rows = np.arange(y.size)
            print(rows)
            one_hot[rows, y] = 1.0
            print(one_hot)
            label = np.expand_dims(one_hot[0], axis=0)
            loss_val = self.compute_loss(x, one_hot)
            losses = np.append(losses, loss_val)

        if return_preds:
            preds = self.predict(x)
            return losses, preds
        else:
            return loss_val.numpy()


"""
Inherits from the troj base class and the ART tensorflow v1 classifier for tf1 support
Also implements our ComputeLoss function which will be called by each classifier, should implement as abstract method in base class
"""


class TrojKerasClassifier(estimators.classification.KerasClassifier, TrojClassifier):
    import tensorflow as tf

    tf.compat.v1.disable_eager_execution()

    """
    Compute loss computes the loss over a batch of target samples

    :param x: inputs
    :param y: labels, either true labels or original unperturbed model labels. y might need to be expanded along
    the first dimension because of art bug.
    :param return_preds: bool to return model predictions with loss
    :param reduction: changes the reduction of the loss function to none 
    :return: Loss values and optionally predictions
    """

    def ComputeLoss(
        self, x, y, return_preds=True, reduction=tf.keras.losses.Reduction.NONE
    ):
        # import tensorflow.compat.v1 as tf
        import tensorflow as tf

        print("loss fn")
        print(self.model.loss)
        print(self)
        old_reduction = self.model.loss_functions[0]._get_reduction()
        self.model.loss_functions[0].reduction = reduction
        preds = self.predict(x)
        # hard_labels = np.argmax(preds, axis=1)
        # hard_labels_dtype = 'float32'
        # y = y.astype(hard_labels_dtype)
        loss_val = self.model.loss_functions[0](y, preds)
        self._loss.reduction = old_reduction
        # tf.compat.v1.enable_eager_execution()
        if return_preds:

            return loss_val.eval(session=tf.compat.v1.Session()), preds
        else:
            return loss_val.numpy()


"""
Inherits from the troj base class and the ART tensorflow v1 classifier for tf1 support
Also implements our ComputeLoss function which will be called by each classifier, should implement as abstract method in base class
"""


class TrojPytorchClassifier(
    estimators.classification.PyTorchClassifier, TrojClassifier
):
    """
    Compute loss computes the loss over a batch of target samples

    :param x: inputs
    :param y: labels, either true labels or original unperturbed model labels. y might need to be expanded along
    the first dimension because of art bug.
    :param return_preds: bool to return model predictions with loss
    :return: Loss values and optionally predictions
    """

    def ComputeLoss(self, x, y, return_preds=True, reduction="none"):
        import torch

        old_reduction = self._loss.reduction
        self._loss.reduction = reduction
        preds = torch.tensor(self.predict(x))
        y = torch.tensor(y)
        loss_val = self._loss(preds, y)
        self._loss.reduction = old_reduction
        if return_preds:
            return loss_val.numpy(), preds.numpy()
        else:
            return loss_val.numpy()
