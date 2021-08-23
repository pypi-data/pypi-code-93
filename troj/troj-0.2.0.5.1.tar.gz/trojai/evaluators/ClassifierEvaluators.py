from ..attacks.ClassifierAttacks import LpAttack, TrojEpsAttack
from ..metrics.metric_utils import compute_Lp_distance
import numpy as np


class GenericRobustnessEvaluator:
    def __init__(
        self, classifier, attack, attack_name, attkwargs, use_model_preds=False
    ):
        """
        The simple robustness evaluator class. Should be used to form a baseline.

        :param classifier: TrojClassifier/ART Classifier instance
        :param attack: undecalred ART evasion class
        :param attack_name: Name for logging
        :param **attkwargs: keyword arguments for attack.
        """
        self.atk_meta = attkwargs
        self.classifier = classifier
        self.attacker = LpAttack(self.classifier, attack, use_model_preds, **attkwargs)
        self.atk_meta["name"] = attack_name

    def attack(self, data, target, index, device=None):
        """
        Runs the attack.

        :param data: Input data
        :param target: Target labels
        :param index: Index of samples in dataframe
        :param device: If using Pytorch, one can specify the device.
        :return: A dictionary containing the minimum perturbation, the loss, adversarial loss, prediction, and adversarial
        prediction for each sample, along with a list of indices for the logging function.
        """

        # send data and target to cpu, convert to numpy
        data = np.ascontiguousarray(data.astype(np.float32))
        test_loss, preds = self.classifier.ComputeLoss(data, target)
        preds = np.argmax(preds, axis=1)
        adv_x, adv_preds, adv_loss = self.attacker.generate(data, target)
        # adv_loss, adv_preds = self.classifier.ComputeLoss(adv_x, target)
        perturbation = compute_Lp_distance(data, adv_x)
        adv_pred = np.argmax(adv_preds, axis=1)
        # generate the adversarial image using the data numpy array and label numpy array
        out_dict = {
            "Linf_perts": perturbation,
            "Loss": test_loss,
            "Adversarial_Loss": adv_loss,
            "prediction": preds,
            "Adversarial_prediction": adv_pred,
        }
        return (out_dict, index)


class BasicRobustnessEvaluator:
    def __init__(
        self,
        classifier,
        eps_steps=0.01,
        batch_size=128,
        norm=np.inf,
        use_model_preds=False,
    ):
        """
        The simple robustness evaluator class. Should be used to form a baseline.

        :param classifier: TrojClassifier/ART Classifier instance
        :param eps_steps: Epsilon step size for the attack. Smaller values are more precise but slower.
        :param batch_size: Number of images in a batch.
        :param norm: The p norm (can be int or np.inf)
        :param use_model_preds: Whether or not to use true labels or model predictions
        """
        self.atk_meta = {
            "attack_name": "fgsm",
            "eps_steps": str(eps_steps),
            "batch_size": str(batch_size),
            "norm": str(norm),
            "use_model_preds": str(use_model_preds),
        }
        self.classifier = classifier
        self.attacker = TrojEpsAttack(
            self.classifier,
            eps_steps=eps_steps,
            batch_size=batch_size,
            norm=norm,
            use_model_preds=use_model_preds,
        )

    def attack(self, data, target, index, device=None):
        """
        Runs the attack.

        :param data: Input data
        :param target: Target labels
        :param index: Index of samples in dataframe
        :param device: If using Pytorch, one can specify the device.
        :return: A dictionary containing the minimum perturbation, the loss, adversarial loss, prediction, and adversarial
        prediction for each sample, along with a list of indices for the logging function.
        """

        # send data and target to cpu, convert to numpy
        data = np.ascontiguousarray(data.astype(np.float32))
        test_loss, preds = self.classifier.ComputeLoss(data, target)
        preds = np.argmax(preds, axis=1)
        adv_x, adv_preds, adv_loss = self.attacker.generate(data, target)
        # adv_loss, adv_preds = self.classifier.ComputeLoss(adv_x, target)
        perturbation = compute_Lp_distance(data, adv_x)
        adv_pred = np.argmax(adv_preds, axis=1)
        # generate the adversarial image using the data numpy array and label numpy array
        out_dict = {
            "Linf_perts": perturbation,
            "Loss": test_loss,
            "Adversarial_Loss": adv_loss,
            "prediction": preds,
            "Adversarial_prediction": adv_pred,
        }
        return (out_dict, index)
