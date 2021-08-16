import pandas as pd
import torch


def prediction(model, images, targets=None):
    """
    Makes and stores predictions on one batch of images.
    :param model: The model used for prediction.
    :param images: The batch of images on which to predict bounding boxes.
    :param targets: Optional ground truth labels and bounding boxes.
    :return: A Dataframe consisting of predicted and (if supplied) ground truth labels and bounding boxes.
    """
    predictions = {"pred_boxes": [],
                   "pred_scores": [],
                   "pred_labels": []}
    if targets:
        predictions["gt_boxes"] = [target["bboxes"].detach().cpu().numpy() for target in targets]
        predictions["gt_labels"] = [target["labels"].detach().cpu().numpy() for target in targets]
    with torch.no_grad():
        det = model(images)
        for i in range(images.shape[0]):
            pred_det = det[i]
            predictions["pred_boxes"].append(pred_det[:, :4].detach().cpu().numpy())
            predictions["pred_scores"].append(pred_det[:, 4].detach().cpu().numpy())
            predictions["pred_labels"].append(pred_det[:, 5].detach().cpu().numpy().astype(int))
    return predictions


def prediction_df(model, test_loader,
                  device=torch.device("cuda" if torch.cuda.is_available() else "cpu"),
                  verbose=0):
    """
    Creates a Dataframe of predictions from unlabeled test data.
    :param model: The model used for predictions.
    :param test_loader: Dataloader for unlabeled test data.
    :param device: Device to load the model on. CPU or CUDA. Defaults using CUDA if available, otherwise CPU.
    :param verbose: If positive prints output every "verbose" steps.
    :return: Dataframe of bounding box predictions.
    """
    assert verbose >= 0
    predictions = []
    n = 0
    for images in test_loader:
        n += 1
        images = torch.stack(images).to(device).float()
        predictions.append(pd.DataFrame(prediction(model, images)))
        if verbose and n % verbose == 0:
            print(f"Processed batch {n}.")

    return pd.concat(predictions).reset_index(drop=True)


def val_prediction_df(model, test_loader,
                      device=torch.device("cuda" if torch.cuda.is_available() else "cpu"),
                      verbose=0):
    """
    Creates a Dataframe of predictions from labeled data.
    :param model: The model used for predictions.
    :param test_loader: Dataloader for unlabeled test data.
    :param device: Device to load the model on. CPU or CUDA. Defaults using CUDA if available, otherwise CPU.
    :param verbose: If positive prints output every "verbose" steps.
    :return: Dataframe of predicted and ground truth bounding box labels.
    """
    assert verbose >= 0
    predictions = []
    n = 0
    for images, labels in test_loader:
        n += 1
        images = torch.stack(images).to(device).float()
        predictions.append(pd.DataFrame(prediction(model, images, labels)))
        if verbose and n % verbose == 0:
            print(f"Processed batch {n}.")

    return pd.concat(predictions).reset_index(drop=True)
