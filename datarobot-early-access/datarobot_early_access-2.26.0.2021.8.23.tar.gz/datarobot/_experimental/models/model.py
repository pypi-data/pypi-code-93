import pandas as pd
import six
import trafaret as t

from datarobot import errors, Model
from datarobot._experimental.models.segmentation import SegmentInfo


class CombinedModel(Model):
    """
    A model from a segmented project. Combination of ordinary models in child segments projects.

    Attributes
    ----------
    id : str
        the id of the model
    project_id : str
        the id of the project the model belongs to
    segmentation_task_id : str
        the id of a segmentation task used in this model
    """

    _converter = t.Dict(
        {
            t.Key("combined_model_id") >> "id": t.String,
            t.Key("project_id"): t.String,
            t.Key("segmentation_task_id"): t.String,
        }
    ).ignore_extra("*")

    # noinspection PyMissingConstructor
    def __init__(self, id=None, project_id=None, segmentation_task_id=None):
        self.id = id
        self.project_id = project_id
        self.segmentation_task_id = segmentation_task_id

    def __repr__(self):
        return "CombinedModel({})".format(self.id)

    @classmethod
    def get(cls, project_id, combined_model_id):
        """ Retrieve combined model

        Parameters
        ----------
        project_id : str
            The project's id.
        combined_model_id : str
            Id of the combined model.

        Returns
        -------
        CombinedModel
            The queried combined model.
        """
        url = "projects/{}/combinedModels/{}/".format(project_id, combined_model_id)
        return cls.from_location(url)

    @classmethod
    def set_segment_champion(cls, project_id, model_id):
        """ Update a segment champion in a combined model by setting the model_id
        that belongs to the child project_id as the champion.

        Parameters
        ----------
        project_id : str
            The project id for the child model that contains the model id.
        model_id : str
            Id of the model to mark as the champion

        Returns
        -------
        combined_model_id : str
            Id of the combined model that was updated

        """
        url = "projects/{}/segmentChampion/".format(project_id)
        response = cls._client.put(url, json={"modelId": model_id})
        return response.json().get("combinedModelId")

    def get_segments_info(self):
        """Retrieve Combined Model segments info

        Returns
        -------
        list[SegmentInfo]
            List of segments
        """
        return SegmentInfo.list(self.project_id, self.id)

    def get_segments_as_dataframe(self, encoding="utf-8"):
        """ Retrieve Combine Models segments as a DataFrame.

        Parameters
        ----------
        encoding : str, optional
            A string representing the encoding to use in the output csv file.
            Defaults to 'utf-8'.

        Returns
        -------
        DataFrame
            Combined model segments
        """
        path = "projects/{}/combinedModels/{}/segments/download/".format(self.project_id, self.id)
        resp = self._client.get(path, headers={"Accept": "text/csv"}, stream=True)
        if resp.status_code == 200:
            content = resp.content.decode("utf-8")
            return pd.read_csv(six.StringIO(content), index_col=0, encoding=encoding)
        else:
            raise errors.ServerError(
                "Server returned unknown status code: {}".format(resp.status_code),
                resp.status_code,
            )

    def get_segments_as_csv(
        self, filename, encoding="utf-8",
    ):
        """ Save the Combine Models segments to a csv.

        Parameters
        ----------
        filename : str or file object
            The path or file object to save the data to.
        encoding : str, optional
            A string representing the encoding to use in the output csv file.
            Defaults to 'utf-8'.
        """
        data = self.get_segments_as_dataframe(encoding=encoding)
        data.to_csv(
            path_or_buf=filename, header=True, index=False, encoding=encoding,
        )
