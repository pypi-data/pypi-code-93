import torchvision.ops
import torch
import numpy as np
from .attack_utils import nms_reduction, get_objects_of_type, check_flip


class EvoDAttack:
    def __init__(
        self,
        model,
        attack_class,
        iterations=25,
        init_pop_size=4,
        thresh=0.05,
        max_val=0.1,
        init_pop_mean=0,
        init_pop_dev=0.05,
        num_offspring=2,
        mut_mean=0,
        mut_deviation=0.005,
        pop_reduction_factor=2,
        device="cuda",
        **kwargs
    ):
        """
        A simple blackbox attack for object detection algorithms using evolutionary strategies, intended as a measure of
        classifier robustness against a simple adversary. The user selects a class the want to try to fool. Given an image
        containing such a class, the algorithm finds the instance in the image of that class and tries to find noise which
        causes the classifier to miss that instance.

        :param model: Pytorch Object detection model. That is, any model which outputs predictions as a dictionary
        containing the keys [boxes, labels, scores] where boxes are the bounding boxes for
        predicted objects in the form [x,y, x+w, y+h] where w,h are the width and height of the bounding box. Labels are the
        predicted labels, and scores are the confidence of prediction, where each value is of the correct Pytorch dtype.
        :param attack_class: The class to perform the attack on.
        :param iterations: Number of generations for the attack.
        :param init_pop_size: Size of the initial population
        :param thresh: The maximum fitness for an individual is 0. The value thresh specifies a stopping bound by -thresh
        meaning that if an individual with such a fitness score is found, the algorithm stops.
        :param max_val: Maximum allowable perturbation
        :param init_pop_mean: Mean of the values in the initial population. (population sampled from Gaussian)
        :param init_pop_dev: Standard deviation of the initial population.
        :param num_offspring: Number of offspring at each timestep.
        :param mut_mean: Mean value of mutations applied to offspring
        :param mut_deviation: Deviation of mutation values.
        :param pop_reduction_factor: Factor to reduce the population by after each timestep.
        :param device: Device for tensors
        :param kwargs:
        """
        if type(model).__name__ == "PytorchObjectDetector":
            self.model = model.model
        else:
            self.model = model
        self.attack_class = attack_class
        self.init_pop_size = init_pop_size
        self.thresh = thresh
        self.max_val = max_val
        self.iterations = iterations
        self.init_pop_mean = init_pop_mean
        self.init_pop_dev = init_pop_dev
        self.num_offspring = num_offspring
        self.mut_mean = mut_mean
        self.mut_deviation = mut_deviation
        self.device = device
        self.pop_reduction_factor = pop_reduction_factor

    def get_weakest(self, predictions):
        """
        Takes in the predictions for the class we care about, and finds the weakest one

        :param predictions: Predictions of class we wish to fool
        :return: Dictionary containing the weakest sample
        """
        scores = predictions["scores"]
        weak_id = torch.argmin(scores)
        reduced_predictions = {
            "boxes": predictions["boxes"][weak_id],
            "labels": predictions["labels"][weak_id],
            "scores": predictions["scores"][weak_id],
        }
        return reduced_predictions

    def get_ground_truth(self, annots, wl_pred):
        """
        Finds the ground truth object for the weakest prediction of the model for the class we are attacking.

        :param annots: Labeled sample containing only instances of class we wish to perturb
        :param wl_pred: Model prediction of the class with the lowest score.
        :return: The ground truth annotation for the weakest prediction.
        """
        ious = torchvision.ops.box_iou(wl_pred["boxes"], annots["boxes"].squeeze(dim=1))
        gt_idx = torch.argmax(ious, dim=1)[0]
        true_gt = {"boxes": annots["boxes"][gt_idx], "labels": annots["labels"][gt_idx]}
        return true_gt

    def find_vulnerable(self, predicts, targ, thresh=0.05):
        """
        Finds the most vulnerable ground truth label.

        :param predicts: All model predictions on sample.
        :param targ: Targets for the sample.
        :param thresh: Thresh for NMS.
        :return: The most vulnerable ground truth instance.
        """
        obj_id = self.attack_class
        with torch.no_grad():
            red_preds = nms_reduction(predicts, thresh=thresh)
            object_preds = get_objects_of_type(predicts, obj_id, inc_scores=True)
            object_target = get_objects_of_type(targ, obj_id, inc_scores=False)
            if object_target["boxes"].shape[0] == 0:
                gt = None
            elif object_preds["boxes"].shape[0] == 0:
                gt = None
            else:
                weakest_link = self.get_weakest(object_preds)
                gt = self.get_ground_truth(object_target, weakest_link)
        return gt

    def get_prediction(self, gt, predictions):
        """
        Returns the label y ={1, -1} where y=1 if the label is the desired label, and -1 if the iou with
        the ground truth box is 0 (since the class has either flipped or is background). We also return the score, and the iou.
        :param gt: Ground truth object we are attacking.
        :param predictions: All model predictions
        :return: The IOU (intersection over union), the score, and the flip indication.
        """
        obj_type = gt["labels"][0]
        object_preds = get_objects_of_type(predictions, obj_type, inc_scores=True)
        if len(object_preds["labels"]) == 0:
            obj_iou = 0
            score = 0
            label = -1
        else:
            ious = torchvision.ops.box_iou(
                gt["boxes"], object_preds["boxes"].squeeze(dim=1)
            )
            comparison_tensor = torch.zeros_like(ious)
            if torch.equal(comparison_tensor, ious):
                obj_iou = 0
                score = 0
                label = -1
            else:
                associated_pred_id = torch.argmax(ious, dim=1)
                associated_pred = {
                    "boxes": object_preds["boxes"][associated_pred_id],
                    "labels": object_preds["labels"][associated_pred_id],
                    "scores": object_preds["scores"][associated_pred_id],
                }
                obj_iou = ious[0][associated_pred_id][0].item()
                label = 1
                score = object_preds["scores"][associated_pred_id][0].item()

        return obj_iou, score, label

    def generate_population(self, num_indiv, shape):
        """
        Generates initial population.

        :param num_indiv: Number of individuals to generate.
        :param shape: Shape of elements of population.
        :return: Initial population.
        """
        # generate initial population
        population = torch.nn.init.normal_(
            torch.zeros((num_indiv, shape[0], shape[1], shape[2]), requires_grad=False),
            mean=self.init_pop_mean,
            std=self.init_pop_dev,
        )
        return population

    def generate_offspring_asexual(self, population):
        """
        Generates offspring asexually (meaning no recombination between members of the population)

        :param population: Input population
        :return: New population with p_{i-1}*n individuals, where p_{i-1} is the number of individuals in the previous
        population and n is the number of offspring.
        """
        # generate offspring for recombination and add random mutations
        new_population = []
        for i in range(self.num_offspring - 1):
            new_population.append(population)
        new_population = torch.cat(new_population)
        mutations = torch.nn.init.normal_(
            torch.zeros_like(new_population, requires_grad=False),
            mean=self.mut_mean,
            std=self.mut_deviation,
        )
        new_population = new_population + mutations
        new_population = torch.clamp(new_population, -self.max_val, self.max_val)
        new_population = torch.cat([population, new_population])
        return new_population

    # inp is tensor of shape C, W, H (no batch dimension)
    def evaluate_fitness(self, inp, gt, population):
        """
        Evaluate fitness of population
        :param inp: Tensor of shape C, W, H (no batch dimension)
        :param gt: Ground truth annotation for vulnerable object.
        :param population: Current population
        :return: Fitness of population members and their returned flip indicators.
        """
        device = self.device
        # evaluate fitness of members of population
        self.model.eval()
        pop_fitness = []
        inp_tile = []
        for i in range(population.shape[0]):
            inp_tile.append(inp)
        inp_tile = torch.stack(inp_tile)
        perturbed_inp = inp_tile.cpu() + population
        perturbed_inp = [
            perturbed_inp[i].to(device) for i in range(perturbed_inp.shape[0])
        ]
        with torch.no_grad():
            model_preds = self.model(perturbed_inp)
        returned_labels = []
        for i in range(len(perturbed_inp)):
            iou, score, label = self.get_prediction(gt, model_preds[i])
            flip = check_flip(model_preds[i], gt, self.attack_class)
            if flip == 1:
                label = -1 * flip
            else:
                label = 1
            perturb = population[i]
            perturb = perturb.view(-1)
            pert_norm = torch.norm(perturb, p=np.inf)
            returned_labels.append(label)
            fitness = -1 * label - pert_norm - score * iou
            pop_fitness.append(fitness)
        return torch.Tensor(pop_fitness), torch.Tensor(returned_labels)

    def reduce_population(self, population, fitness, ret_lab):
        """

        Splits population based on reduction factor (reduces based on fitness)

        :param population: Current population
        :param fitness: Fitness of current population
        :param ret_lab: Flip indicators
        :return: Reduced population
        """
        sorted_fitness, indices = torch.sort(fitness, descending=True)
        remaining_pop = int(fitness.shape[0] / self.pop_reduction_factor)
        asc_to_desc = indices
        pop_by_fitness = population[asc_to_desc]
        lab_by_fitness = ret_lab[asc_to_desc]
        reduced_pop = pop_by_fitness[0:remaining_pop]
        reduced_lab = lab_by_fitness[0:remaining_pop]
        reduced_fitness = sorted_fitness[0:remaining_pop]
        return reduced_pop, reduced_lab, reduced_fitness

    def attack(self, x, y, verbose=True):
        """
        Perform an attack on a sample.

        :param x: a tensor of shape C W H with no batch dimension
        :param y:  y are the annotations for x converted to the appropriate format (bounding box as [x,y, x+w, y+h]).
        :param verbose: Print progress
        :return: The found perturbation, the vulnerable ground truth, and the initial model predictions.
        """
        pop_fits = []
        init_preds = self.model([x])[0]
        if y == None:
            y = init_preds
        gt = self.find_vulnerable(init_preds, y, self.attack_class)
        if gt == None:
            return None, None, None
        population = self.generate_population(self.init_pop_size, x.shape)
        for i in range(self.iterations):
            population = self.generate_offspring_asexual(population)
            fit, returned_labs = self.evaluate_fitness(x, gt, population)
            population, labs, red_fit = self.reduce_population(
                population, fit, returned_labs
            )
            av_fitness = torch.mean(red_fit)
            pop_fits.append(av_fitness.item())
            if verbose == True:
                print("average fitness at generation {}: ".format(i), av_fitness.item())
            if torch.max(fit) > self.thresh:
                break
        negated = torch.where(labs == 0, labs, torch.tensor([-1.0]).float()[0])
        flipped_locs = negated == -1
        flipped_idx = negated.nonzero()
        if flipped_idx.nelement() > 0:
            population = population[flipped_idx]

        outs = population[0]
        if len(outs.shape) > 3:
            outs = outs[0]
        # return av pop fitness
        return outs, gt, init_preds
