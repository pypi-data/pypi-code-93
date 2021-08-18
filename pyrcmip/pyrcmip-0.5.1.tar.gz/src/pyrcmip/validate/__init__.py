"""
Validation of RCMIP submissions
"""
from logging import getLogger

import pandas as pd
import pint.errors
from scmdata.run import run_append

from ..errors import ProtocolConsistencyError
from .utils import load_submission_template_definitions

LOGGER = getLogger(__name__)


def validate_submission_bundle(timeseries, model_reported, metadata, protocol=None):
    """
    Validate that an RCMIP submission bundle complies with the required formats

    Parameters
    ----------
    timeseries : :obj:`scmdata.ScmRun`
        Timeseries to validate

    model_reported : :obj:`pd.DataFrame`
        Model reported metrics

    metadata : :obj:`pd.DataFrame`
        Model metadata

    protocol : str
        Data file containing the RCMIP protocol against which to validate the
        timeseries. If ``None``, the submission template will be loaded from
        ``pyrcmip/data/rcmip-data-submission-template-v4-0-0.xlsx``.

    Returns
    -------
    (:obj:`scmdata.ScmRun`, :obj:`pd.DataFrame`, :obj:`pd.DataFrame`)
        Validated timeseries, model reported metrics and model metadata

    Raises
    ------
    ProtocolConsistencyError
        The submission bundle is not consistent with the RCMIP protocol

    ValueError
        A value for ``climate_model`` is found in ``timeseries`` or ``model_reported``
        but isn't found in the ``climate_model`` column of ``metadata``.
    """
    raise_error = False

    try:
        metadata_consistent = validate_submission_model_meta(metadata)
        LOGGER.info("valid metadata")
    except ProtocolConsistencyError:
        LOGGER.exception("problems with metadata in submission")
        raise_error = True

    try:
        model_reported_consistent = validate_submission_model_reported_metrics(
            model_reported
        )
        LOGGER.info("valid model reported csv")
    except ProtocolConsistencyError:
        LOGGER.exception("problems with model reported csv in submission")
        raise_error = True

    try:
        timeseries_consistent = validate_submission(timeseries, protocol=protocol)
        LOGGER.info("valid timeseries")
    except ProtocolConsistencyError:
        LOGGER.exception("problems with timeseries in submission")
        raise_error = True

    if raise_error:
        raise ProtocolConsistencyError(
            "submission bundle is inconsistent with the RCMIP protocol"
        )

    climate_model_consistency = True

    metadata_climate_models = metadata_consistent["climate_model"].unique().tolist()
    timeseries_climate_models = timeseries_consistent.get_unique_meta("climate_model")
    model_reported_climate_models = (
        model_reported_consistent["climate_model"].unique().tolist()
    )

    timeseries_climate_models_extras = set(timeseries_climate_models) - set(
        metadata_climate_models
    )
    if timeseries_climate_models_extras:
        error_msg = "climate_model(s) `{}` in timeseries is not found in metadata".format(
            timeseries_climate_models_extras
        )
        LOGGER.error(error_msg)
        climate_model_consistency = False

    model_reported_climate_models_extras = set(model_reported_climate_models) - set(
        metadata_climate_models
    )
    if model_reported_climate_models_extras:
        error_msg = "climate_model(s) `{}` in model reported csv is not found in metadata".format(
            model_reported_climate_models_extras
        )
        LOGGER.error(error_msg)
        climate_model_consistency = False

    if not climate_model_consistency:
        raise ValueError("climate_model not consistent across the bundle")

    LOGGER.info("valid submission bundle")

    return timeseries_consistent, model_reported_consistent, metadata_consistent


def validate_submission(submission, protocol=None):
    """
    Validate that an RCMIP submission complies with the required data format

    Parameters
    ----------
    submission : :obj:`scmdata.ScmRun`
        Data to validate

    protocol : str
        Data file containing the RCMIP protocol against which to validate the
        data. If ``None``, the submission template will be loaded from
        ``pyrcmip/data/rcmip-data-submission-template-v4-0-0.xlsx``.

    Returns
    -------
    :obj:`scmdata.ScmRun`
        Input data, converted to match RCMIP units

    Raises
    ------
    ProtocolConsistencyError
        The data is not consistent with the protocol
    """
    raise_error = False

    protocol_variables = load_submission_template_definitions(protocol, "variables")

    try:
        validate_variables(
            submission.get_unique_meta("variable"),
            protocol_variables["variable"].tolist(),
        )
        LOGGER.info("valid variables")
    except ProtocolConsistencyError:
        LOGGER.exception("problems with variables in submission")
        raise_error = True

    try:
        validate_regions(
            submission.get_unique_meta("region"),
            load_submission_template_definitions(protocol, "regions")[
                "region"
            ].tolist(),
        )
        LOGGER.info("valid regions")
    except ProtocolConsistencyError:
        LOGGER.exception("problems with regions in submission")
        raise_error = True

    try:
        validate_scenarios(
            submission.get_unique_meta("scenario"),
            load_submission_template_definitions(protocol, "scenarios")[
                "scenario_id"
            ].tolist(),
        )
        LOGGER.info("valid scenarios")
    except ProtocolConsistencyError:
        LOGGER.exception("problems with scenarios in submission")
        raise_error = True

    required_cols = ("climate_model", "ensemble_member")
    for required_col in required_cols:
        if required_col not in submission.meta:
            LOGGER.exception(
                "no {} metadata included in submission".format(required_col)
            )
            raise_error = True

    if "unit" not in submission.meta:
        LOGGER.exception("no unit metadata included in submission")
        raise_error = True
    else:
        try:
            out = convert_units_to_rcmip_units(submission, protocol_variables)
            LOGGER.info("succesfully converted units")
        except ProtocolConsistencyError:
            LOGGER.exception("problems converting units in submission")
            raise_error = True

    if raise_error:
        raise ProtocolConsistencyError(
            "submission is inconsistent with the RCMIP protocol"
        )

    LOGGER.info("valid submission")

    return out


def _validate_sets(to_check, protocol, error_str_id):
    not_included = set(to_check) - set(protocol)

    if not_included:
        raise ProtocolConsistencyError(
            "{} do not match the RCMIP protocol:\n{}".format(
                error_str_id, sorted(not_included)
            )
        )


def validate_variables(vars_to_check, protocol_variables):
    """
    Validate variables against variables in the RCMIP protocol

    Parameters
    ----------
    vars_to_check : list-like
        Variables to check

    protocol_variables : list-like
        Variables in the RCMIP protocol

    Raises
    ------
    ProtocolConsistencyError
        ``vars_to_check`` contains variables not included in ``protocol_variables``
    """
    _validate_sets(vars_to_check, protocol_variables, "Variables")


def validate_regions(regions_to_check, protocol_regions):
    """
    Validate regions against regions in the RCMIP protocol

    Parameters
    ----------
    regions_to_check : list-like
        Regions to check

    protocol_regions : list-like
        Regions in the RCMIP protocol

    Raises
    ------
    ProtocolConsistencyError
        ``regions_to_check`` contains regions not included in ``protocol_regions``
    """
    _validate_sets(regions_to_check, protocol_regions, "Regions")


def validate_scenarios(scenarios_to_check, protocol_scenarios):
    """
    Validate scenarios against scenarios in the RCMIP protocol

    Parameters
    ----------
    scenarios_to_check : list-like
        Scenarios to check

    protocol_scenarios : list-like
        Scenarios in the RCMIP protocol

    Raises
    ------
    ProtocolConsistencyError
        ``scenarios_to_check`` contains scenarios not included in ``protocol_scenarios``
    """
    _validate_sets(scenarios_to_check, protocol_scenarios, "scenarios")


def convert_units_to_rcmip_units(submission, protocol_variables):
    """
    Convert units to RCMIP units

    Parameters
    ----------
    submission : :obj:`scmdata.ScmRun`
        Submission to convert

    protocol_variables : :obj:`pd.DataFrame`
        Variables and units as defined by the RCMIP protocol

    Returns
    -------
    :obj:`scmdata.ScmRun`
        Submission with units converted to RCMIP units

    Raises
    ------
    ProtocolConsistencyError
        Units could not be converted to RCMIP units
    """
    res = []
    for vgroup in submission.groupby("variable"):
        res.append(_convert_to_rcmip_units(vgroup, protocol_variables))

    errors = [r for r in res if isinstance(r, dict)]
    if errors:
        errors = pd.DataFrame(errors)

        raise ProtocolConsistencyError(
            "Could not convert submission to protocol units. Errors:\n{}".format(errors)
        )

    return run_append(res)


def _convert_to_rcmip_units(variable_group, protocol_variables):
    variable = variable_group.get_unique_meta("variable", no_duplicates=True)

    if variable.startswith("Emissions|NOx"):
        conversion_context = "NOx_conversions"
    else:
        conversion_context = None

    try:
        protocol_unit = protocol_variables[protocol_variables["variable"] == variable][
            "unit"
        ].iloc[0]
        out = variable_group.convert_unit(protocol_unit, context=conversion_context)
        if conversion_context:
            out = out.drop_meta("unit_context", inplace=False)

        return out
    except IndexError as exc:
        input_unit = variable_group.get_unique_meta("unit", no_duplicates=True)
        return {
            "variable": variable,
            "input_unit": input_unit,
            "protocol_unit": "None",
            "exc_type": type(exc),
            "exc_message": str(exc),
        }
    except (pint.errors.DimensionalityError, pint.errors.UndefinedUnitError) as exc:
        input_unit = variable_group.get_unique_meta("unit", no_duplicates=True)
        return {
            "variable": variable,
            "input_unit": input_unit,
            "protocol_unit": protocol_unit,
            "exc_type": type(exc),
            "exc_message": str(exc),
        }


def _check_expected_columns(inp, expected_columns):
    correct_columns = set(inp.columns) == expected_columns
    if not correct_columns:
        raise ProtocolConsistencyError(
            "Input columns: {}. Expected columns: {}.".format(
                set(inp.columns), expected_columns
            )
        )


def validate_submission_model_reported_metrics(inp):
    """
    Validate a submission of model reported metrics

    Parameters
    ----------
    inp : :obj:`pd.DataFrame`
        Input to validate

    Returns
    -------
    :obj:`pd.DataFrame`
        Validated input

    Raises
    ------
    ProtocolConsistencyError
        The columns of res are not as expected (i.e.
        ``{"value", "ensemble_member", "RCMIP name", "unit", "climate_model"}``),
        more than one climate model is included in ``res``, the ``ensemble_member``
        column is not integers, an unrecognised metric is provided or the provided
        unit is not compatible with RCMIP.
    """
    out = inp.copy()

    expected_columns = {
        "value",
        "ensemble_member",
        "RCMIP name",
        "unit",
        "climate_model",
    }
    _check_expected_columns(out, expected_columns)

    if (out["ensemble_member"].astype(int) == out["ensemble_member"]).all():
        out["ensemble_member"] = out["ensemble_member"].astype(int)
    else:
        raise ProtocolConsistencyError("`ensemble_member` column must be integers")

    # TODO: better system for this
    allowed_metrics = ["Equilibrium Climate Sensitivity"]
    allowed_units = ["K"]
    if not all(out["RCMIP name"].isin(allowed_metrics)):
        raise ProtocolConsistencyError(
            "The `RCMIP name` column should only contain 'Equilibrium Climate Sensitivity"
        )

    if not all(out["unit"].isin(allowed_units)):
        raise ProtocolConsistencyError("values must be provided in 'K'")

    return out


def validate_submission_model_meta(inp):
    """
    Validate a submission's metadata

    Parameters
    ----------
    inp : :obj:`pd.DataFrame`
        Metadata submission to validate

    Returns
    -------
    :obj:`pd.DataFrame`
        Validated metadata submission

    Raises
    ------
    ProtocolConsistencyError
        The columns of res are not as expected (i.e.
        ``{"climate_model", "climate_model_name", "climate_model_version", "climate_model_configuration_label", "climate_model_configuration_description", "project", "name_of_person", "literature_reference"}``).
    """
    out = inp.copy()
    expected_columns = {
        "climate_model",
        "climate_model_name",
        "climate_model_version",
        "climate_model_configuration_label",
        "climate_model_configuration_description",
        "project",
        "name_of_person",
        "literature_reference",
    }
    _check_expected_columns(out, expected_columns)

    return out
