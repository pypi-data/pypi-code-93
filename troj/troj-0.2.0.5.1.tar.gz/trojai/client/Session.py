import numpy as np
import json


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
        if "dataframe" not in dataframe:
            tmp = dataframe
            dataframe = {}
            dataframe["dataframe"] = tmp
        if drop_na == True:
            dataframe["dataframe"] = dataframe["dataframe"].dropna()
        dataframe["dataframe"] = json.loads(
            dataframe["dataframe"].to_json(orient="index")
        )
        jsonified_df = dataframe

        return self.client.upload_df_results(project_name, dataset_name, jsonified_df)

    def metadata_collection(
        self, classifier=None, evaluator=None, dataloader=None, dataframe=None, tags=[]
    ):
        classifier_meta = {}
        evaluator_meta = {}
        dataloader_meta = {}

        if classifier is not None:
            classifier_meta = classifier.get_classifier_meta()
        if evaluator is not None:
            evaluator_meta = evaluator.atk_meta
        if dataloader is not None:
            dataloader_meta = dataloader.dataset_meta
        if "prediction" in dataframe:
            dataframe["prediction"].replace("", np.nan, inplace=True)
        dataframe.dropna(inplace=True)
        out_dict = {
            "metadata": {
                "classifier_metadata": classifier_meta,
                "evaluator_metadata": evaluator_meta,
                "dataloader_metadata": dataloader_meta,
                "tags": str(tags),
            },
            "dataframe": dataframe,
        }

        return out_dict
