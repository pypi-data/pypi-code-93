import trafaret as t

from datarobot._compat import Int, String
from datarobot.models.api_object import APIObject
from datarobot.utils import encode_utf8_if_py2, get_id_from_response


class ShapImpact(APIObject):
    """
    Represents SHAP impact score for a feature in a model.

    .. versionadded:: v2.21

    Notes
    -----
    SHAP impact score for a feature has the following structure:

    * ``feature_name`` : (str) the feature name in dataset
    * ``impact_normalized`` : (float) normalized impact score value (largest value is 1)
    * ``impact_unnormalized`` : (float) raw impact score value

    Attributes
    ----------
    count : int
        the number of SHAP Impact object returned
    shap_impacts : list
        a list which contains SHAP impact scores for top 1000 features used by a model
    """

    _path = "projects/{}/models/{}/shapImpact/"
    _converter = t.Dict(
        {
            t.Key("count"): Int(),
            t.Key("shap_impacts"): t.List(
                t.Dict(
                    {
                        t.Key("feature_name"): String(),
                        t.Key("impact_normalized"): t.Float(),
                        t.Key("impact_unnormalized"): t.Float(),
                    }
                )
            ),
        }
    )

    def __init__(self, count, shap_impacts):
        self.count = count
        self.shap_impacts = shap_impacts

    def __repr__(self):
        template = u"{}(count={!r})"
        return encode_utf8_if_py2(template.format(type(self).__name__, self.count))

    @classmethod
    def create(cls, project_id, model_id):
        """Create SHAP impact for the specified model.

        Parameters
        ----------
        project_id : str
            id of the project the model belongs to
        model_id : str
            id of the model to calculate shap impact for

        Returns
        -------
        job : Job
            an instance of created async job
        """
        url = cls._path.format(project_id, model_id)
        response = cls._client.post(url)
        job_id = get_id_from_response(response)
        from .job import Job

        return Job.get(project_id=project_id, job_id=job_id)

    @classmethod
    def get(cls, project_id, model_id):
        """
        Retrieve SHAP impact scores for features in a model.

        Parameters
        ----------
        project_id : str
            id of the project the model belongs to
        model_id : str
            id of the model the SHAP impact is for

        Returns
        -------
        shap_impact : ShapImpact
            The queried instance.

        Raises
        ------
        ClientError (404)
            If the project or model does not exist or the SHAP impact has not been computed.
        """
        path = cls._path.format(project_id, model_id)
        return cls.from_location(path)
