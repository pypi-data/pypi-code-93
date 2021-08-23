from art.attacks.evasion import FastGradientMethod
from ..metrics import true_min_pert
import numpy as np


class LpAttack:
    def __init__(self, model, attack, use_model_preds=False, **attkwargs):
        """
        Makes a generic L^p attacker instance.

        :param model: TrojClassifier
        :param attack: an undeclared instance of an ART evasion attack i.e art.evasion.pgd
        :param attkwargs: keyword arguments for the attack
        """
        self.model = model
        attack_dict = {}
        att_name = "attack"
        attack_dict[att_name] = attack(model, **attkwargs)
        self.attack_dict = attack_dict
        self.use_model_preds = use_model_preds

    def generate(self, x, y):
        """
        :param x: inputs
        :param y: labels, either true labels or original unperturbed model labels. y might need to be expanded along
        the first dimension because of art bug.
        :return: adversarial examples with minimal perturbation, adversarial losses, adversarial predictions
        """
        generated_examples = []
        model_adv_losses = []
        model_adv_preds = []
        # For each attack method in the attack dictionary, generate adversarial examples, then compute the loss
        # and the class predictions.
        for attacker in list(self.attack_dict.values()):
            adv_x = attacker.generate(x, y)
            if len(y.shape) == 1:
                adv_losses, adv_preds = self.model.ComputeLoss(adv_x, y)
                if self.use_model_preds == True:
                    true_losses, true_preds = self.model.ComputeLoss(x, y)
            else:
                adv_losses, adv_preds = self.model.ComputeLoss(
                    adv_x, np.squeeze(y, axis=1)
                )
                if self.use_model_preds == True:
                    true_losses, true_preds = self.model.ComputeLoss(
                        x, np.squeeze(y, axis=1)
                    )
            model_adv_losses.append(adv_losses)
            generated_examples.append(adv_x)
            model_adv_preds.append(adv_preds)
        # reshape arrays so that they each have shape [batch_size, num_attacks, *]
        generated_examples = np.stack(generated_examples)
        generated_examples = np.swapaxes(generated_examples, 0, 1)

        model_adv_losses = np.stack(model_adv_losses)
        model_adv_losses = np.swapaxes(model_adv_losses, 0, 1)

        model_adv_preds = np.stack(model_adv_preds)
        model_adv_preds = np.swapaxes(model_adv_preds, 0, 1)

        # Whether or not to compute the perturbations quickly, or in such a way as to minimize
        # the perturbation that flips the label.
        if self.use_model_preds == True:
            labels = true_preds
        else:
            labels = y
        output, preds, losses = true_min_pert(
            labels, model_adv_preds, x, generated_examples, model_adv_losses
        )

        return output, preds, losses


class TrojEpsAttack:
    def __init__(
        self,
        model,
        eps_steps=0.01,
        max_eps=0.5,
        batch_size=128,
        norm=np.inf,
        use_model_preds=False,
    ):
        """
        This is the basic evaluation attack, and is equivalent to
         LpAttack(model, art.evasion.fgm, attkwargs = {'minimal'=True, ...}). This is meant to provide a simple evaluation
         of a classifier against the simplest whitebox attack algorithm.


        :param model: Troj/ART classifier instance.
        :param eps_steps: Size of steps in FGSM
        :param max_eps: Largest allowable perturbation
        :param batch_size: Batch size for each attack.
        :param norm: The attack norm for FGSM.
        :param use_model_preds: if minimum is true, whether or not to use the true labels or the model preds for
        evauluating the minimum perturbation
        """
        self.model = model
        self.max_eps = max_eps
        self.eps_steps = eps_steps
        self.batch_size = batch_size
        self.norm = norm
        self.use_model_preds = use_model_preds

        # store instantiate attack instances in dictionary
        attack_dict = {}
        fgm_name = "fgsm_{}".format(0)
        attack_dict[fgm_name] = FastGradientMethod(
            self.model,
            norm=self.norm,
            eps=self.max_eps,
            eps_step=self.eps_steps,
            batch_size=self.batch_size,
            minimal=True,
        )

        self.attack_dict = attack_dict

    def generate(self, x, y):
        """
        :param x: inputs
        :param y: labels, either true labels or original unperturbed model labels. y might need to be expanded along
        the first dimension because of art bug.
        :return: adversarial examples with minimal perturbation, adversarial losses, adversarial predictions
        """
        generated_examples = []
        model_adv_losses = []
        model_adv_preds = []
        # For each attack method in the attack dictionary, generate adversarial examples, then compute the loss
        # and the class predictions.
        for attacker in list(self.attack_dict.values()):
            adv_x = attacker.generate(x, y)
            if len(y.shape) == 1:
                adv_losses, adv_preds = self.model.ComputeLoss(adv_x, y)
                if self.use_model_preds == True:
                    true_losses, true_preds = self.model.ComputeLoss(x, y)
            else:
                adv_losses, adv_preds = self.model.ComputeLoss(
                    adv_x, np.squeeze(y, axis=1)
                )
                if self.use_model_preds == True:
                    true_losses, true_preds = self.model.ComputeLoss(
                        x, np.squeeze(y, axis=1)
                    )
            model_adv_losses.append(adv_losses)
            generated_examples.append(adv_x)
            model_adv_preds.append(adv_preds)
        # reshape arrays so that they each have shape [batch_size, num_attacks, *]
        generated_examples = np.stack(generated_examples)
        generated_examples = np.swapaxes(generated_examples, 0, 1)

        model_adv_losses = np.stack(model_adv_losses)
        model_adv_losses = np.swapaxes(model_adv_losses, 0, 1)

        model_adv_preds = np.stack(model_adv_preds)
        model_adv_preds = np.swapaxes(model_adv_preds, 0, 1)

        # Whether or not to compute the perturbations quickly, or in such a way as to minimize
        # the perturbation that flips the label.
        if self.use_model_preds == True:
            labels = true_preds
        else:
            labels = y
        output, preds, losses = true_min_pert(
            labels, model_adv_preds, x, generated_examples, model_adv_losses
        )

        return output, preds, losses
