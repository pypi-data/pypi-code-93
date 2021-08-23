from .feature_discovery import *  # noqa
from .partitioning_methods import *  # noqa


class AdvancedOptions(object):
    """
    Used when setting the target of a project to set advanced options of modeling process.

    Parameters
    ----------
    weights : string, optional
        The name of a column indicating the weight of each row
    response_cap : float in [0.5, 1), optional
        Quantile of the response distribution to use for response capping.
    blueprint_threshold : int, optional
        Number of hours models are permitted to run before being excluded from later autopilot
        stages
        Minimum 1
    seed : int
        a seed to use for randomization
    smart_downsampled : bool
        whether to use smart downsampling to throw away excess rows of the majority class.  Only
        applicable to classification and zero-boosted regression projects.
    majority_downsampling_rate : float
        the percentage between 0 and 100 of the majority rows that should be kept.  Specify only if
        using smart downsampling.  May not cause the majority class to become smaller than the
        minority class.
    offset : list of str, optional
        (New in version v2.6) the list of the names of the columns containing the offset
        of each row
    exposure : string, optional
        (New in version v2.6) the name of a column containing the exposure of each row
    accuracy_optimized_mb : bool, optional
        (New in version v2.6) Include additional, longer-running models that will be run by the
        autopilot and available to run manually.
    scaleout_modeling_mode : string, optional
        (New in version v2.8) Specifies the behavior of Scaleout models for the project.
        This is one of ``datarobot.enums.SCALEOUT_MODELING_MODE``.
        If ``datarobot.enums.SCALEOUT_MODELING_MODE.DISABLED``, no
        models will run during autopilot or show in the list of available blueprints.
        Scaleout models must be disabled for some partitioning settings including projects
        using datetime partitioning or projects using offset or exposure columns.
        If ``datarobot.enums.SCALEOUT_MODELING_MODE.REPOSITORY_ONLY``,
        scaleout models will be in the list of available blueprints
        but not run during autopilot.
        If ``datarobot.enums.SCALEOUT_MODELING_MODE.AUTOPILOT``,
        scaleout models will run during autopilot and be in the list of
        available blueprints.
        Scaleout models are only supported in the Hadoop enviroment with
        the corresponding user permission set.
    events_count : string, optional
        (New in version v2.8) the name of a column specifying events count.
    monotonic_increasing_featurelist_id : string, optional
        (new in version 2.11) the id of the featurelist that defines the set of features
        with a monotonically increasing relationship to the target. If None,
        no such constraints are enforced. When specified, this will set a default for the project
        that can be overriden at model submission time if desired.
    monotonic_decreasing_featurelist_id : string, optional
        (new in version 2.11) the id of the featurelist that defines the set of features
        with a monotonically decreasing relationship to the target. If None,
        no such constraints are enforced. When specified, this will set a default for the project
        that can be overriden at model submission time if desired.
    only_include_monotonic_blueprints : bool, optional
        (new in version 2.11) when true, only blueprints that support enforcing
        monotonic constraints will be available in the project or selected for the autopilot.
    allowed_pairwise_interaction_groups : list of tuple, optional
        (New in version v2.19) For GA2M models - specify groups of columns for which pairwise
        interactions will be allowed. E.g. if set to [(A, B, C), (C, D)] then GA2M models will
        allow interactions between columns AxB, BxC, AxC, CxD. All others (AxD, BxD) will
        not be considered.
    blend_best_models: bool, optional
        (New in version v2.19) blend best models during Autopilot run
    scoring_code_only: bool, optional
        (New in version v2.19) Keep only models that can be converted to scorable java code
        during Autopilot run
    shap_only_mode: bool, optional
        (New in version v2.21) Keep only models that support SHAP values during Autopilot run. Use
        SHAP-based insights wherever possible. Defaults to False.
    prepare_model_for_deployment: bool, optional
        (New in version v2.19) Prepare model for deployment during Autopilot run.
        The preparation includes creating reduced feature list models, retraining best model
        on higher sample size, computing insights and assigning "RECOMMENDED FOR DEPLOYMENT" label.
    consider_blenders_in_recommendation: bool, optional
        (New in version 2.22.0) Include blenders when selecting a model to prepare for
        deployment in an Autopilot Run. Defaults to False.
    min_secondary_validation_model_count: int, optional
        (New in version v2.19) Compute "All backtest" scores (datetime models) or cross validation
        scores for the specified number of highest ranking models on the Leaderboard,
        if over the Autopilot default.
    autopilot_data_sampling_method: str, optional
        (New in version v2.23) one of ``datarobot.enums.DATETIME_AUTOPILOT_DATA_SAMPLING_METHOD``.
        Applicable for OTV projects only, defines if autopilot uses "random" or "latest" sampling
        when iteratively building models on various training samples. Defaults to "random" for
        duration-based projects and to "latest" for row-based projects.
    run_leakage_removed_feature_list: bool, optional
        (New in version v2.23) Run Autopilot on Leakage Removed feature list (if exists).
    autopilot_with_feature_discovery: bool, optional.
        (New in version v2.23) If true, autopilot will run on a feature list that includes features
        found via search for interactions.
    feature_discovery_supervised_feature_reduction: bool,  default ``True` optional
        (New in version v2.23) Run supervised feature reduction for feature discovery projects.
    exponentially_weighted_moving_alpha: float, optional
        (New in version v2.26) defaults to None, value between 0 and 1 (inclusive), indicates
        alpha parameter used in exponentially weighted moving average within feature derivation
        window.
    external_time_series_baseline_dataset_id: str, optional.
        (New in version v2.26) If provided, will generate metrics scaled by external model
        predictions metric for time series projects. The external predictions catalog
        must be validated before autopilot starts, see
        ``Project.validate_external_time_series_baseline`` and
        :ref:`external baseline predictions documentation <external_baseline_predictions>`
        for further explanation.

    Examples
    --------
    .. code-block:: python

        import datarobot as dr
        advanced_options = dr.AdvancedOptions(
            weights='weights_column',
            offset=['offset_column'],
            exposure='exposure_column',
            response_cap=0.7,
            blueprint_threshold=2,
            smart_downsampled=True, majority_downsampling_rate=75.0)

    """

    def __init__(
        self,
        weights=None,
        response_cap=None,
        blueprint_threshold=None,
        seed=None,
        smart_downsampled=False,
        majority_downsampling_rate=None,
        offset=None,
        exposure=None,
        accuracy_optimized_mb=None,
        scaleout_modeling_mode=None,
        events_count=None,
        monotonic_increasing_featurelist_id=None,
        monotonic_decreasing_featurelist_id=None,
        only_include_monotonic_blueprints=None,
        allowed_pairwise_interaction_groups=None,
        blend_best_models=None,
        scoring_code_only=None,
        prepare_model_for_deployment=None,
        consider_blenders_in_recommendation=None,
        min_secondary_validation_model_count=None,
        shap_only_mode=None,
        autopilot_data_sampling_method=None,
        run_leakage_removed_feature_list=None,
        autopilot_with_feature_discovery=False,
        feature_discovery_supervised_feature_reduction=True,
        exponentially_weighted_moving_alpha=None,
        external_time_series_baseline_dataset_id=None,
    ):
        self.weights = weights
        self.response_cap = response_cap
        self.blueprint_threshold = blueprint_threshold
        self.seed = seed
        self.smart_downsampled = smart_downsampled
        self.majority_downsampling_rate = majority_downsampling_rate
        self.offset = offset
        self.exposure = exposure
        self.accuracy_optimized_mb = accuracy_optimized_mb
        self.scaleout_modeling_mode = scaleout_modeling_mode
        self.events_count = events_count
        self.monotonic_increasing_featurelist_id = monotonic_increasing_featurelist_id
        self.monotonic_decreasing_featurelist_id = monotonic_decreasing_featurelist_id
        self.only_include_monotonic_blueprints = only_include_monotonic_blueprints
        self.allowed_pairwise_interaction_groups = allowed_pairwise_interaction_groups
        self.blend_best_models = blend_best_models
        self.scoring_code_only = scoring_code_only
        self.shap_only_mode = shap_only_mode
        self.prepare_model_for_deployment = prepare_model_for_deployment
        self.consider_blenders_in_recommendation = consider_blenders_in_recommendation
        self.min_secondary_validation_model_count = min_secondary_validation_model_count
        self.autopilot_data_sampling_method = autopilot_data_sampling_method
        self.run_leakage_removed_feature_list = run_leakage_removed_feature_list
        self.autopilot_with_feature_discovery = autopilot_with_feature_discovery
        self.feature_discovery_supervised_feature_reduction = (
            feature_discovery_supervised_feature_reduction
        )
        self.exponentially_weighted_moving_alpha = exponentially_weighted_moving_alpha
        self.external_time_series_baseline_dataset_id = external_time_series_baseline_dataset_id

    def collect_payload(self):

        payload = dict(
            weights=self.weights,
            response_cap=self.response_cap,
            blueprint_threshold=self.blueprint_threshold,
            seed=self.seed,
            smart_downsampled=self.smart_downsampled,
            majority_downsampling_rate=self.majority_downsampling_rate,
            offset=self.offset,
            exposure=self.exposure,
            accuracy_optimized_mb=self.accuracy_optimized_mb,
            scaleout_modeling_mode=self.scaleout_modeling_mode,
            events_count=self.events_count,
            monotonic_increasing_featurelist_id=self.monotonic_increasing_featurelist_id,
            monotonic_decreasing_featurelist_id=self.monotonic_decreasing_featurelist_id,
            only_include_monotonic_blueprints=self.only_include_monotonic_blueprints,
            allowed_pairwise_interaction_groups=self.allowed_pairwise_interaction_groups,
        )

        # Some of the optional parameters are incompatible with the others.
        # For example, scoring_code_only is not compatible with scaleout_modeling_mode.
        # Api will return 422 if both parameters are present.
        sfd = self.feature_discovery_supervised_feature_reduction
        optional = dict(
            blend_best_models=self.blend_best_models,
            scoring_code_only=self.scoring_code_only,
            shap_only_mode=self.shap_only_mode,
            prepare_model_for_deployment=self.prepare_model_for_deployment,
            consider_blenders_in_recommendation=self.consider_blenders_in_recommendation,
            min_secondary_validation_model_count=self.min_secondary_validation_model_count,
            autopilot_data_sampling_method=self.autopilot_data_sampling_method,
            run_leakage_removed_feature_list=self.run_leakage_removed_feature_list,
            autopilot_with_feature_discovery=self.autopilot_with_feature_discovery,
            feature_discovery_supervised_feature_reduction=sfd,
            exponentially_weighted_moving_alpha=self.exponentially_weighted_moving_alpha,
            external_time_series_baseline_dataset_id=self.external_time_series_baseline_dataset_id,
        )

        payload.update({k: v for k, v in optional.items() if v is not None})

        return payload
