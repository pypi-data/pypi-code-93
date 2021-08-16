import numpy as np
import json
import torch

"""

"""


class TrojSession:
    def __init__(self):
        super().__init__()
        self.client = None

    def create_project(self, project_name: str):
        return self.client.create_project(project_name)

    def create_dataset(self, project_name: str, dataset_name: str):
        return self.client.create_dataset(project_name, dataset_name)

    def upload_dataframe(
        self, dataframe, project_name: str, dataset_name: str, drop_na=True
    ):
        if drop_na == True:
            dataframe["dataframe"] = dataframe["dataframe"].dropna()
        dataframe["dataframe"] = json.loads(dataframe["dataframe"].to_json(orient="index"))
        jsonified_df = dataframe

        return self.client.upload_df_results(project_name, dataset_name, jsonified_df)

    def metadata_collection(self, classifier, evaluator, dataloader, dataframe, tags = []):
        classifier_metadata = classifier.classifier_meta
        evaluator_meta = evaluator.atk_meta
        dataloader_meta = dataloader.dataset_meta
        dataframe['prediction'].replace('', np.nan, inplace=True)
        dataframe.dropna(inplace=True)
        out_dict = {"metadata": {"classifier_metadata": classifier_metadata, "evaluator_metadata": evaluator_meta, "dataloader_metadata": dataloader_meta, "tags": str(tags)}, "dataframe": dataframe}

        return out_dict
        
        

    def CreateClassifierInstance(self, 
        model, input_shape, num_classes, loss_func=None, framework="pt", preprocessing=None, channels_first=True
    ):
        '''
        :param model: model, either Pytorch or Tensorflow
        :param input_shape: Expected input shape
        :param num_classes: number of output classes.
        :param loss_func: Loss function. Must be provided with Pytorch
        :param framework: One of either 'pt' (for Pytorch) or 'tf' (Tensorflow)
        :return: A TrojClassier (a specific instance of ART classifier)
        '''
        self.classifier_meta = {"model":str(model), "input_shape": str(input_shape), "num_classes": str(num_classes), "loss_func":str(loss_func), "framework": framework, "preprocessing": str(preprocessing), "channels_first": str(channels_first)}
        if framework == "pt":
            if loss_func is not None:
                from art.estimators.classification import PyTorchClassifier
                class TrojClassifier(PyTorchClassifier):

                    def ComputeLoss(self,x, y, return_preds = True, reduction='none'):
                        old_reduction =  self._loss.reduction
                        self._loss.reduction=reduction
                        preds = torch.tensor(self.predict(x))
                        y = torch.tensor(y)
                        loss_val = self._loss(preds, y)
                        self._loss.reduction = old_reduction
                        if return_preds:
                            return loss_val.numpy(), preds.numpy()
                        else:
                            return loss_val.numpy()
                # ensure model is in eval mode, not sure how to check that rn
                # classifier = TrojClassifier(model, loss_func, input_shape, num_classes)
                classifier = TrojClassifier(model, loss_func, input_shape, num_classes, preprocessing=preprocessing, channels_first=channels_first)
            else:
                print("Pass in loss function with pytorch classifier!")

        elif framework == "tf":
            # ensure model is compiled tensorflow
            from art.estimators.classification import KerasClassifier
            import tensorflow.keras.losses
            class TrojClassifier(KerasClassifier):
                def ComputeLoss(self, x, y, return_preds=True, reduction = tensorflow.keras.losses.Reduction.NONE):
                    old_reduction = self._loss.reduction
                    self._loss.reduction = reduction
                    preds = self.predict(x)
                    loss_val = self._loss(preds, y)
                    self._loss.reduction = old_reduction
                    if return_preds:
                        return loss_val.numpy(), preds
                    else:
                        return loss_val.numpy()

            if True:
                classifier = TrojClassifier(model)
        return classifier
