from trojai.data import log_to_dataframe
from trojai.attacks.attack_utils import check_flip, get_class_ap, nms_pred_reduce
from trojai.metrics.metric_utils import get_pred_data
from trojai.attacks.BlackBoxODAttacks import EvoDAttack
import torch
import numpy as np


class BlackBoxODEvaluator:
    # different run form to classification
    def __init__(
        self,
        model,
        obj_class,
        loader,
        batch_iterator,
        df=None,
        device="cuda",
        iou_thresh=0.5,
        nms_thresh=0.05,
        return_nms=False,
        use_preds=False,
        verbose=True,
        **attkwargs
    ):
        """
        The class used for evaluating the robustness of an object detection algorithm against the simple blackbox attack.

        :param model:  Pytorch Object detection model. That is, any model which outputs predictions as a dictionary
        containing the keys [boxes, labels, scores] where boxes are the bounding boxes for
        predicted objects in the form [x,y, x+w, y+h] where w,h are the width and height of the bounding box. Labels are the
        predicted labels, and scores are the confidence of prediction, where each value is of the correct Pytorch dtype.
        :param obj_class: The class to perform the attack on.
        :param loader: Dataloader
        :param batch_iterator: Troj OD batch iterator
        :param df: Dataframe
        :param device: Deprecated
        :param iou_thresh: IOU threshold for a positive detection of an object
        :param nms_thresh: Threshold used when applying NMS.
        :param return_nms: When saving predictions to dataframe, whether or not apply NMS to the predictions first.
        :param use_preds: Whether or not to use the true annotations or annotations predicted by the model. #TODO implement
        :param verbose: Whether or not print info during attack.
        :param return_prc: Whether or not to return the precision recall curve.
        :param attkwargs: Arguments for the evolutionary attack.
        """
        if type(model).__name__ == "PytorchObjectDetector":
            self.model = model.model
        else:
            self.model = model
        self.obj_class = obj_class
        self.loader = loader
        self.batch_iterator = batch_iterator
        self.df = df
        if self.df == None:
            self.df = loader.dataframe
        self.device = device
        self.iou_thresh = iou_thresh
        self.nms_thresh = nms_thresh
        self.return_nms = return_nms
        self.use_preds = use_preds
        self.attacker = EvoDAttack(self.model, self.obj_class, **attkwargs)
        self.verbose = verbose
        self.atk_meta = {
            "model_name": str(model.__class__.__name__),
            "iou_thresh": str(iou_thresh),
            "nms_thresh": str(nms_thresh),
        }

        for arg in attkwargs:
            print("arg:", arg)

    def _save_bbox_ims(self, image, target_box, fname, out_path=""):
        # TODO don't fix the save location
        import torchvision.transforms as transforms
        import os

        arr = image
        im = transforms.ToPILImage()(arr)

        directory = "./perts/"

        if not os.path.exists(directory):
            os.makedirs(directory)
        im.save("perts/" + fname)

    def run(self, num_samples, save_perts=False):
        """
        #TODO add save perturbation option here.
        Run the black box robustness evaluation on a set number of samples.

        :param num_samples: number of samples containing the attack class to run attack on.
        :return: the dataframe and the ids of the attacked samples.
        """
        # TODO: Should the dataset task checker be in here?
        tracker = 0
        attacked_ids = []
        batch_enum = enumerate(self.batch_iterator)

        while tracker < num_samples:
            batch_id, (ims, labs, ids) = next(batch_enum)

            if tracker > 0 and batch_id == 0:
                break

            for idx in range(len(labs)):
                sample_id = ids[idx]
                data_dict = {}
                if self.use_preds == False:
                    perturb, gt, preds = self.attacker.attack(ims[idx], labs[idx])
                else:
                    perturb, gt, preds = self.attacker.attack(ims[idx], None)
                # make sure we have a ground truth object
                if gt != None:
                    # Add the perturbation to the image
                    pert_im = ims[idx] + perturb.to(self.device)
                    # get predictions on perturbed image
                    pert_preds = self.model([pert_im])[0]
                    # Apply non-maximal suppression to predictions
                    nms_pert_preds = nms_pred_reduce(pert_preds, self.nms_thresh)
                    nms_preds = nms_pred_reduce(preds, self.nms_thresh)
                    # check to see if gt object has disappeared
                    flip = check_flip(
                        nms_pert_preds,
                        gt,
                        self.obj_class,
                        self.iou_thresh,
                        self.nms_thresh,
                    )
                    # Get imagewise AP for class
                    troj_ap, _ = get_class_ap(
                        self.obj_class, nms_preds, labs[idx], self.iou_thresh
                    )
                    adv_troj_ap, _ = get_class_ap(
                        self.obj_class, nms_pert_preds, labs[idx], self.iou_thresh
                    )
                    # compute perturbation norm
                    pert_vec = perturb.view(-1)
                    linf_pert = torch.norm(pert_vec, p=np.inf)
                    tracker += 1
                    if self.return_nms == True:
                        (
                            orig_boxes,
                            orig_labels,
                            orig_scores,
                        ) = get_pred_data(nms_preds)
                        (
                            pert_boxes,
                            pert_labels,
                            pert_scores,
                        ) = get_pred_data(nms_pert_preds)
                    else:
                        (
                            orig_boxes,
                            orig_labels,
                            orig_scores,
                        ) = get_pred_data(preds)
                        (
                            pert_boxes,
                            pert_labels,
                            pert_scores,
                        ) = get_pred_data(pert_preds)
                    gt_boxes = gt["boxes"].detach().cpu().numpy()
                    data_dict = {
                        "flip": flip,
                        "TmAP": troj_ap.item(),
                        "Adv_TmAP": adv_troj_ap.item(),
                        "Linf": linf_pert.item(),
                        "iou_thresh": self.iou_thresh,
                        "nms_thresh": self.nms_thresh,
                        'pred_boxes':np.expand_dims(orig_boxes, axis=0).tolist(),
                        'pred_labels': np.expand_dims(orig_labels, axis=1).tolist(),
                        'pred_scores': np.expand_dims(orig_scores, axis=1).tolist(),
                        'adversarial_boxes': np.expand_dims(pert_boxes, axis=0).tolist(),
                        'adversarial_labels': np.expand_dims(pert_labels, axis=1).tolist(),
                        'adversarial_scores': np.expand_dims(pert_scores, axis=1).tolist(),
                        'gt_box':np.expand_dims(gt_boxes, axis=0).tolist()
                        }

                    self.df = log_to_dataframe(self.df, sample_id, data_dict)

                    attacked_ids.append(sample_id)
                    if save_perts:
                        self._save_bbox_ims(
                            pert_im, gt_boxes, self.df["file_name"][sample_id]
                        )
            return self.df, attacked_ids
