import torchvision.ops
import torch
from collections import Counter
import numpy as np

# import pandas as pd


"""
ODAttack.py
====================================
Generic Object Detection attack created by Troj
"""


def nms_reduction(predictions, thresh=0.05):
    """
    Performs non-maximal suppression on output dictionary of network.

    :param predictions: A dictionary containing the keys [boxes, labels, scores] where boxes are the bounding boxes for
    predicted objects in the form [x,y, x+w, y+h] where w,h are the width and height of the bounding box. Labels are the
    predicted labels, and scores are the confidence of prediction.
    :param thresh: Threshold with which to perform the suppression.
    :return: Supressed predictions.
    """
    # returns predictions after NMS
    fixed_indices = torchvision.ops.nms(
        predictions["boxes"], predictions["scores"], thresh
    )
    reduced_predictions = {
        "boxes": predictions["boxes"][fixed_indices],
        "labels": predictions["labels"][fixed_indices],
        "scores": predictions["scores"][fixed_indices],
    }
    return reduced_predictions


def get_objects_of_type(predictions, object_class, inc_scores=True):
    """
    Gets predictions for objects only of a given type.

    :param predictions: Original predictions. Model typically outputs list, this expects only elements of that list.
    :param object_class: Object class id
    :param inc_scores: whether or not to include the scores in the output
    :return: The prediction dictionary containing only the desired class.
    """
    # extracts predictions for the class we wish to evaluate
    labels = predictions["labels"]
    obj_ids = (labels == object_class).nonzero()
    if inc_scores == True:
        reduced_predictions = {
            "boxes": predictions["boxes"][obj_ids],
            "labels": predictions["labels"][obj_ids],
            "scores": predictions["scores"][obj_ids],
        }
    else:
        reduced_predictions = {
            "boxes": predictions["boxes"][obj_ids],
            "labels": predictions["labels"][obj_ids],
        }
    return reduced_predictions


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
        mutation=True,
        mut_mean=0,
        mut_deviation=0.005,
        device="cuda",
        **kwargs
    ):
        #TODO make stronger, potentially using reconstruction error or limiting the area we are allowed to act on. Better fitness function.
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
        :param kwargs:
        """
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
        '''
        Returns the label y ={1, -1} where y=1 if the label is the desired label, and -1 if the iou with
        the ground truth box is 0 (since the class has either flipped or is background). We also return the score, and the iou.
        :param gt: Ground truth object we are attacking.
        :param predictions: All model predictions
        :return: The IOU (intersection over union), the score, and the flip indication.
        '''
        obj_type = gt["labels"][0]
        object_preds = get_objects_of_type(predictions, obj_type, inc_scores=True)
        if len(object_preds["labels"]) == 0:
            obj_iou = 0
            score = 0
            label = 0
        else:
            ious = torchvision.ops.box_iou(
                gt["boxes"], object_preds["boxes"].squeeze(dim=1)
            )
            comparison_tensor = torch.zeros_like(ious)
            if torch.equal(comparison_tensor, ious):
                obj_iou = 0
                score = 0
                label = 0
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
        for i in range(self.num_offspring):
            new_population.append(population)
        new_population = torch.cat(new_population)
        mutations = torch.nn.init.normal_(
            torch.zeros_like(new_population, requires_grad=False),
            mean=self.mut_mean,
            std=self.mut_deviation,
        )
        new_population = new_population + mutations
        new_population = torch.clamp(new_population, -self.max_val, self.max_val)
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
        model_preds = self.model(perturbed_inp)
        returned_labels = []
        for i in range(len(perturbed_inp)):
            iou, score, label = self.get_prediction(gt, model_preds[i])
            perturb = population[i]
            perturb = perturb.view(-1)
            pert_norm = torch.norm(perturb, p=np.inf)
            returned_labels.append(label)
            fitness = -pert_norm - (score * iou * label)
            pop_fitness.append(fitness)
        return torch.Tensor(pop_fitness), torch.Tensor(returned_labels)

    def reduce_population(self, population, fitness, ret_lab):
        """
        Splits population in half (reduces based on fitness)

        :param population: Current population
        :param fitness: Fitness of current population
        :param ret_lab: Flip indicators
        :return: Reduced population
        """
        remaining_pop = None
        sorted_fitness, indices = torch.sort(fitness)
        if remaining_pop == None:
            remaining_pop = int(fitness.shape[0] / 2)
        asc_to_desc = torch.flip(indices, dims=[0])
        pop_by_fitness = population[asc_to_desc]
        lab_by_fitness = ret_lab[asc_to_desc]
        reduced_pop = pop_by_fitness[0:remaining_pop]
        reduced_lab = lab_by_fitness[0:remaining_pop]
        return reduced_pop, reduced_lab

    def attack(self, x, y, verbose=True):
        '''
        Perform an attack on a sample.

        :param x: a tensor of shape C W H with no batch dimension
        :param y:  y are the annotations for x converted to the appropriate format (bounding box as [x,y, x+w, y+h]).
        :param verbose: Print progress
        :return: The found perturbation, the vulnerable ground truth, and the initial model predictions.
        '''
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
            if verbose == True:
                av_fitness = torch.mean(fit)
                print("average fitness at generation {}: ".format(i), av_fitness.item())
            if torch.max(fit) > -self.thresh:
                population, labs = self.reduce_population(
                    population, fit, returned_labs
                )
                break
            population, labs = self.reduce_population(population, fit, returned_labs)
        negated = torch.where(labs == 0, labs, torch.tensor([-1.0]).float()[0])
        flipped_locs = negated == -1
        flipped_idx = negated.nonzero()
        if flipped_idx.nelement() > 0:
            population = population[flipped_idx]

        outs = population[0]
        if len(outs.shape) > 3:
            outs = outs[0]
        return outs, gt, init_preds


def detect_dict_from_idx(inp_dict, ids):
    """
    Return subdictionary of prediction dictionary based on sets of value ids.

    :param inp_dict: Input dictionary
    :param ids: list of ids
    :return: Dictionary containing the values at the locations specified by the ids.
    """
    key_list = list(inp_dict.keys())
    new_dict = {}
    for key in key_list:
        new_dict[key] = inp_dict[key][ids]
    return new_dict


def get_gt_indices(indicator_matrix):
    # gets the ground truth objects corresponding to the predictions
    # indicator matrix is two dimensional matrix of booleans
    ground_truth_objs = []
    for idx in range(indicator_matrix.shape[0]):
        gt = indicator_matrix[idx].nonzero()
        if gt.shape[0] == 0:
            gt_obj = -1
        else:
            gt_obj = gt[0]
        ground_truth_objs.append(gt_obj)
    return torch.tensor(ground_truth_objs)


def get_tp_fp(gt_inds):
    # gets the true positives and false positives as a list. If a ground truth object is predicted more than once, every prediction after the first is
    # a false positive.
    taken_idxs = []
    tp_fp_list = []
    for idx in gt_inds:
        if idx not in taken_idxs and idx != -1:
            taken_idxs.append(idx)
            tp_fp_list.append(1)
        else:
            tp_fp_list.append(0)
    return torch.tensor(tp_fp_list)


def get_fn_indicators(indicator_matrix):
    # check for false negatives
    fn_inds = []
    indices = torch.tensor([i for i in range(indicator_matrix.shape[1])])
    for idx in indices:
        # 1 if false negative, 0 otherwise
        val = 1
        for obj_indicators in indicator_matrix:
            if obj_indicators[idx] == True:
                val = 0
                break
        fn_inds.append(val)
    return torch.tensor(fn_inds)


def accumulated_tp_fp(tp_fp_indicators):
    # computes accumulated true positive and false positive
    tp_list = []
    fp_list = []
    for idx in range(tp_fp_indicators.shape[0]):
        tp = torch.sum(tp_fp_indicators[:idx + 1])
        tp_list.append(tp)
        fp_list.append(tp_fp_indicators.shape[0] - tp)
    return torch.tensor(tp_list), torch.tensor(fp_list)


def AP(precisions, recalls):
    # AP for PASCAL VOC 2010
    vals = []
    for i in range(recalls.shape[0]):
        p_interp = torch.max(precisions[i:])
        vals.append(p_interp)
    return torch.mean(torch.tensor(vals))


def get_class_ap(class_id, predicts, annots, iou_thresh=0.5):
    # Gets average precision of a class on a single image at a certain threshold.
    # if predicts is list of dictionaries, take first entry
    if isinstance(predicts, list):
        predicts = predicts[0]
    # get objects of the given type from annotations and predictions
    obj_preds = get_objects_of_type(predicts, class_id, inc_scores=True)
    obj_annots = get_objects_of_type(annots, class_id, inc_scores=False)
    # compute IOU values between objects of class class_id in annotations and all predictions made by model
    iou_matrix = torchvision.ops.box_iou(obj_annots['boxes'].squeeze(1), obj_preds['boxes'].squeeze(1))
    # Get the indices where the IOU of the bounding box is greater than the threshold.
    positive_det = iou_matrix >= iou_thresh
    # store the (transpose) positive detection matrix in the obj_preds dictionary
    obj_preds['iou_thresh_indicator'] = torch.transpose(positive_det, 0, 1)
    # now, sort obj_preds dictionary based on the descending confidence scores
    sorting_args = torch.argsort(obj_preds['scores'].squeeze(1), descending=True)
    sorted_obj_preds = {}
    for key in obj_preds.keys():
        sorted_obj_preds[key] = obj_preds[key][sorting_args]
    # Get the indices for ground truth objects corresponding to predictions. A -1 means a false positive.
    ind_matrix = sorted_obj_preds['iou_thresh_indicator']
    false_negs = get_fn_indicators(ind_matrix)
    obj_annots['false_neg'] = false_negs
    gto = get_gt_indices(ind_matrix)
    sorted_obj_preds['gt_idx'] = gto
    # indicate whether prediction is true positive or false positive. In OD, true negative has no meaning, so it is ignored.
    tp_fp_tensor = get_tp_fp(sorted_obj_preds['gt_idx'])
    sorted_obj_preds['tp_fp_indicator'] = tp_fp_tensor
    # get accumulated true and false positives
    acc_tp, acc_fp = accumulated_tp_fp(tp_fp_tensor)
    sorted_obj_preds['acc_tp'] = acc_tp
    sorted_obj_preds['acc_fp'] = acc_fp
    # compute precision and recall at different confidences
    recalls = acc_tp / ind_matrix.shape[1]
    precisions = acc_tp / tp_fp_tensor.shape[0]
    sorted_obj_preds['recall'] = recalls
    sorted_obj_preds['precision'] = precisions
    av_prec = AP(precisions, recalls)
    return av_prec, sorted_obj_preds


def check_flip(predictions, ground_truth, obj_cat, iou_thresh=0.5, nms_thresh=0.05):
    """
    Checks for flips of the gt object.

    :param predictions: Model predictions (after nms)
    :param ground_truth: ground truth object.
    :param obj_cat: Deprecated
    :param iou_thresh: Minimum iou thresh to count as detection.
    :param nms_thresh: Deprecated
    :return:
    """

    nms_reduced_preds = predictions  # detect_dict_from_idx(predictions, pred_ids)
    reduced_preds = get_objects_of_type(nms_reduced_preds, obj_cat)
    if reduced_preds["boxes"].nelement() == 0:
        flip = 1
        return flip
        # return flip, nms_reduced_preds
    ious = torchvision.ops.box_iou(
        ground_truth["boxes"], reduced_preds["boxes"].squeeze(dim=1)
    )
    flip = 1
    if torch.max(ious) >= iou_thresh:
        flip = 0
    return flip


def nms_pred_reduce(predictions, nms_thresh=0.05):
    '''
    Performs nms on predictions.
    :param predictions: original predictions.
    :param nms_thresh: Suppression threshold
    :return: Suppressed predictions
    '''
    pred_ids = torchvision.ops.nms(
        predictions["boxes"], predictions["scores"], nms_thresh
    )
    nms_reduced_preds = detect_dict_from_idx(predictions, pred_ids)
    return nms_reduced_preds
