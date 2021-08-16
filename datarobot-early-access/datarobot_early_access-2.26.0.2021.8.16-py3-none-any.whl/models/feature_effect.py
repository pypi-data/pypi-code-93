import trafaret as t

from datarobot._compat import Int, String
from datarobot.enums import FEATURE_TYPE
from datarobot.models.api_object import APIObject
from datarobot.utils import encode_utf8_if_py2, from_api


class FeatureEffectMetadata(APIObject):
    """ Feature Effect Metadata for model, contains status and available model sources.

    Notes
    -----

    `source` is expected parameter to retrieve Feature Fit. One of provided sources
    shall be used.

    """

    _converter = t.Dict({t.Key("status"): String, t.Key("sources"): t.List(String)}).ignore_extra(
        "*"
    )

    def __init__(self, status, sources):
        self.status = status
        self.sources = sources

    def __repr__(self):
        return encode_utf8_if_py2(u"FeatureEffectMetadata({}/{})".format(self.status, self.sources))


class FeatureEffectMetadataDatetime(APIObject):
    """ Feature Effect Metadata for datetime model, contains list of
    feature effect metadata per backtest.

    Notes
    -----
    ``feature effect metadata per backtest`` contains:
        * ``status`` : string.
        * ``backtest_index`` : string.
        * ``sources`` : list(string).

    `source` is expected parameter to retrieve Feature Fit. One of provided sources
    shall be used.

    `backtest_index` is expected parameter to submit compute request and retrieve Feature Effect.
    One of provided backtest indexes shall be used.

    Attributes
    ----------
    data : list[FeatureEffectMetadataDatetimePerBacktest]
        List feature effect metadata per backtest

    """

    _converter = t.Dict(
        {
            t.Key("data"): t.List(
                t.Dict(
                    {
                        t.Key("backtest_index"): String,
                        t.Key("status"): String,
                        t.Key("sources"): t.List(String),
                    }
                ).ignore_extra("*")
            )
        }
    ).ignore_extra("*")

    def __init__(self, data):
        self.data = [
            FeatureEffectMetadataDatetimePerBacktest(fe_meta_per_backtest)
            for fe_meta_per_backtest in data
        ]

    def __repr__(self):
        return encode_utf8_if_py2(u"FeatureEffectDatetimeMetadata({})".format(self.data))

    def __iter__(self):
        return iter(self.data)


class FeatureEffectMetadataDatetimePerBacktest(object):
    """Convert dictionary into feature effect metadata per backtest which contains backtest_index,
    status and sources.
    """

    def __init__(self, ff_metadata_datetime_per_backtest):
        self.backtest_index = ff_metadata_datetime_per_backtest["backtest_index"]
        self.status = ff_metadata_datetime_per_backtest["status"]
        self.sources = ff_metadata_datetime_per_backtest["sources"]

    def __repr__(self):
        return encode_utf8_if_py2(
            u"FeatureEffectMetadataDatetimePerBacktest(backtest_index={},"
            u"status={}, sources={}".format(self.backtest_index, self.status, self.sources)
        )

    def __eq__(self, other):
        return all(
            [
                self.backtest_index == other.backtest_index,
                self.status == other.status,
                sorted(self.sources) == sorted(other.sources),
            ]
        )

    def __lt__(self, other):
        return self.backtest_index < other.backtest_index


class FeatureEffects(APIObject):
    """
    Feature Effects provides partial dependence and predicted vs actual values for top-500
    features ordered by feature impact score.

    The partial dependence shows marginal effect of a feature on the target variable after
    accounting for the average effects of all other predictive features. It indicates how, holding
    all other variables except the feature of interest as they were, the value of this feature
    affects your prediction.

    Attributes
    ----------
    project_id: string
        The project that contains requested model
    model_id: string
        The model to retrieve Feature Effects for
    source: string
        The source to retrieve Feature Effects for
    feature_effects: list
        Feature Effects for every feature
    backtest_index: string, required only for DatetimeModels,
        The backtest index to retrieve Feature Effects for.

    Notes
    ------
    ``featureEffects`` is a dict containing the following:

        * ``feature_name`` (string) Name of the feature
        * ``feature_type`` (string) `dr.enums.FEATURE_TYPE`, \
          Feature type either numeric or categorical
        * ``feature_impact_score`` (float) Feature impact score
        * ``weight_label`` (string) optional, Weight label if configured for the project else null
        * ``partial_dependence`` (List) Partial dependence results
        * ``predicted_vs_actual`` (List) optional, Predicted versus actual results, \
          may be omitted if there are insufficient qualified samples

    ``partial_dependence`` is a dict containing the following:
        * ``is_capped`` (bool) Indicates whether the data for computation is capped
        * ``data`` (List) partial dependence results in the following format

    ``data`` is a list of dict containing the following:
        * ``label`` (string) Contains label for categorical and numeric features as string
        * ``dependence`` (float) Value of partial dependence

    ``predicted_vs_actual`` is a dict containing the following:
        * ``is_capped`` (bool) Indicates whether the data for computation is capped
        * ``data`` (List) pred vs actual results in the following format

    ``data`` is a list of dict containing the following:
        * ``label`` (string) Contains label for categorical features \
          for numeric features contains range or numeric value.
        * ``bin`` (List) optional, For numeric features contains \
          labels for left and right bin limits
        * ``predicted`` (float) Predicted value
        * ``actual`` (float) Actual value. Actual value is null \
          for unsupervised timeseries models
        * ``row_count`` (int or float) Number of rows for the label and bin. \
          Type is float if weight or exposure is set for the project.
    """

    _PartialDependence = t.Dict(
        {
            t.Key("is_capped"): t.Bool,
            t.Key("data"): t.List(
                t.Dict({t.Key("label"): String | Int, t.Key("dependence"): t.Float}).ignore_extra(
                    "*"
                )
            ),
        }
    ).ignore_extra("*")

    _PredictedVsActual = t.Dict(
        {
            t.Key("is_capped"): t.Bool,
            t.Key("data"): t.List(
                t.Dict(
                    {
                        t.Key("row_count"): Int | t.Float,
                        t.Key("label"): String,
                        t.Key("bin", optional=True): t.List(String),
                        t.Key("predicted"): t.Float | t.Null,
                        t.Key("actual"): t.Float | t.Null,
                    }
                ).ignore_extra("*")
            ),
        }
    ).ignore_extra("*")

    _converter = t.Dict(
        {
            t.Key("project_id"): String,
            t.Key("model_id"): String,
            t.Key("source"): String,
            t.Key("backtest_index", optional=True): String,
            t.Key("feature_effects"): t.List(
                t.Dict(
                    {
                        t.Key("feature_name"): String,
                        t.Key("feature_impact_score"): t.Float,
                        t.Key("feature_type"): t.Enum(
                            FEATURE_TYPE.NUMERIC, FEATURE_TYPE.CATEGORICAL
                        ),
                        t.Key("partial_dependence"): _PartialDependence,
                        t.Key("predicted_vs_actual", optional=True): _PredictedVsActual,
                        t.Key("weight_label", optional=True): String | t.Null,
                    }
                ).ignore_extra("*")
            ),
        }
    ).ignore_extra("*")

    def __init__(
        self, project_id, model_id, source, feature_effects, backtest_index=None,
    ):
        self.project_id = project_id
        self.model_id = model_id
        self.source = source
        self.backtest_index = backtest_index
        self.feature_effects = feature_effects

    def __repr__(self):
        return encode_utf8_if_py2(
            u"{}(project_id={},"
            u"model_id={}, source={}, backtest_index={}, feature_effects={}".format(
                self.__class__.__name__,
                self.project_id,
                self.model_id,
                self.source,
                self.backtest_index,
                self.feature_effects,
            )
        )

    def __eq__(self, other):
        return all(
            [
                self.project_id == other.project_id,
                self.model_id == other.model_id,
                self.source == other.source,
                self.backtest_index == other.backtest_index,
                (
                    sorted(self.feature_effects, key=lambda k: k["feature_name"])
                    == sorted(other.feature_effects, key=lambda k: k["feature_name"])
                ),
            ]
        )

    def __hash__(self):
        return hash(
            (
                self.__class__.__name__,
                self.project_id,
                self.model_id,
                self.source,
                self.backtest_index,
            )
        )

    def __iter__(self):
        return iter(self.feature_effects)

    @classmethod
    def from_server_data(cls, data):
        """
        Instantiate an object of this class using the data directly from the server,
        meaning that the keys may have the wrong camel casing.

        Parameters
        ----------
        data : dict
            The directly translated dict of JSON from the server. No casing fixes have
            taken place
        """
        # keep_null_keys is required for predicted/actual
        case_converted = from_api(data, keep_null_keys=True)
        return cls.from_data(case_converted)
