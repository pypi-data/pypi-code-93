from __future__ import annotations

import datetime
from pathlib import Path
from typing import Optional, TYPE_CHECKING
import warnings

import pandas as pd
import pandas.errors

from assistants.compliance.util import canonicalisation, fields
from assistants.log_status import log
from assistants.log_status import log_dataframe
from assistants.training import canonicalisation as canonicalisation_training, fields as fields_training

if TYPE_CHECKING:
    from collections.abc import Iterable

today = pd.Timestamp(datetime.date.today())
tomorrow = today + pd.DateOffset(days=1)  # NoQA
sixty_years = today - pd.DateOffset(years=60)  # NoQA
five_years = today + pd.DateOffset(years=5)  # NoQA  # TODO check what still is 5Y not 3Y, get more specific

# so we can delete Occasional Helpers from the report
blacklisted_roles = {
    # occasional helper roles
    "Group Occasional Helper",
    "Group Occasional Helper.",
    "District Occasional Helper",
    "County Occasional Helper",
    # council roles:
    "County Scout Council Member",
    "County Scout Council Member - Nominated Representative",
    "County Scout Council Member - Nominated Youth Representative",
    "County Scout Council Member - Nominated Member (18-24)",
    # staff roles:
    "District Staff",
    "County Staff",
    # network member roles:
    "Scout Network Member",
    "District Scout Network",
    "District Scout Network Member",
    "County Scout Network Member",
}  # TODO add PVG, TSA council, etc


def preprocess_data(path_appointments: Path, path_training: Optional[Path] = None, log_raw_data: bool = False) -> pd.DataFrame:
    # first Appointments
    # the source is the whole of the input sheet
    data_appointments = _load_data(path_appointments, debug_copy_data=log_raw_data)

    # for Appointments assume first row is the headings
    # check those
    try:
        columns_map = canonicalisation.map_input_fields(data_appointments.columns)
    except ValueError as err:
        raise RuntimeError(f"Input data does not match any known format! Please report this to the developers.") from err

    # rename headings
    data_appointments.columns = data_appointments.columns.map(columns_map)

    # Canonicalise columns (ignores disclosure/address/phone/sections & useless data - OGL hours/manager info etc.
    data_appointments = data_appointments.reindex(copy=False, columns=canonicalisation.canonical_headings)

    # Clean/tidy appointments data. Removes unneeded roles, sanitises membership numbers, parses datetimes.
    data_appointments = _clean_appointments_data(data_appointments)

    if path_training is None or not path_training.is_file():
        return data_appointments

    data_training = _load_training_report(path_training)
    return _merge_training_report(data_training, data_appointments)[canonicalisation.canonical_headings]  # fix col order


def _load_data(file_name: Path, debug_copy_data: bool = False, skip_rows: Optional[int] = None) -> pd.DataFrame:
    """Load raw data."""
    try:
        raw_data = pd.read_csv(file_name, encoding="UTF-8", skiprows=skip_rows)
    except FileNotFoundError as err:
        log.error(f"Unable to load the data as the following file was not found: {file_name}")
        raise err
    except pandas.errors.EmptyDataError as err:
        log.error(f"Loaded data is empty! File: {file_name}")
        raise err
    except Exception as err:
        log.error("Unable to open the file specified. An exception occurred.")
        raise err

    if debug_copy_data:
        log_dataframe(raw_data)
    log.info(f"Loaded raw data from {file_name}")

    return raw_data


def _clean_appointments_data(input_data: pd.DataFrame) -> pd.DataFrame:
    """Remove roles we don't want, blank rows, secondary headings, and the columns we don't need"""

    # check if we have normalised (lower case)
    if "membership_number" not in input_data.columns:
        raise ValueError("Headings are invalid or not normalised, no membership number field!")

    # check we've got something that begins with a (membership) number
    # this removes blank lines plus non-numeric data
    input_data["membership_number"] = pd.to_numeric(input_data["membership_number"], errors="coerce")  # make numeric
    input_data = input_data[input_data["membership_number"].notna() & (input_data["membership_number"] > 0)]  # Drop member numbers == 0 (or negative/non-numeric!)
    input_data["membership_number"] = pd.to_numeric(input_data["membership_number"], downcast="unsigned")  # downcast

    # There are some 'phantom' blank roles which show up in Reports but not compass itself. Very odd...
    input_data = input_data[input_data["role"].notna()]

    # what "roles" are we ignoring?
    records_to_keep = ~input_data["role"].isin(blacklisted_roles)
    input_data = input_data[records_to_keep]

    # parse dates
    # Check for invalid / out of bounds datetimes. For simplicity we check 80 years ago (DoB)
    # and either tomorrow (most cols) or five years away (columns with legal future dates,
    # such as Review).
    # fmt: off
    date_cols = (
        fields.ROLE_START_DATE, fields.ROLE_END_DATE, fields.REVIEW_DATE, fields.MOD_01, fields.MOD_01_EX, fields.TRUSTEE_INTRO,
        fields.MOD_02, fields.MOD_03, fields.MOD_04, fields.GDPR, fields.WOOD_BADGE,
        fields.SAFETY, fields.SAFETY_RENEWAL, fields.SAFEGUARDING, fields.SAFEGUARDING_RENEWAL, fields.FIRST_AID, fields.FIRST_AID_RENEWAL,
        fields.MOD_LMS, fields.MOD_23,
    )  # TODO date cols list
    future_cols = {
        fields.ROLE_START_DATE, fields.ROLE_END_DATE, fields.REVIEW_DATE,
        fields.SAFETY_RENEWAL, fields.SAFEGUARDING_RENEWAL, fields.FIRST_AID_RENEWAL,
    }
    # fmt: on
    input_data = _parse_datetimes_lenient(input_data, date_cols, future_cols)

    return input_data.reset_index(drop=True)


def _parse_datetimes_lenient(data: pd.DataFrame, date_columns: Iterable[str], future_columns: set[str]) -> pd.DataFrame:
    out_of_bounds: list[pd.DataFrame] = []
    for col in date_columns:
        if col not in data.columns:
            warnings.warn(f"Column {col} not in data!")
            continue

        # parse bit
        try:
            parsed = pd.to_datetime(data[col], cache=True, dayfirst=True)
        except Exception as err:  # OutOfBoundsDatetime
            warnings.warn("Date parsing error, coercing errors", RuntimeWarning, source=err)
            parsed = pd.to_datetime(data[col], cache=True, dayfirst=True, errors="coerce")
        data[col] = parsed

        # out-of-bounds bit
        mask_small = data[col] < sixty_years  # oldest are likely role start/end and WB dates. 60 years seems reasonable
        if col in future_columns:
            mask = mask_small | (data[col] >= five_years)
        else:
            mask = mask_small | (data[col] >= tomorrow)
        if mask.to_numpy().any():  # NoQA (typing)
            out_of_bounds += [data.loc[mask, ["membership_number", "role", col]].rename(columns={col: "date"}).assign(module=col)]
    if out_of_bounds:
        oob_string = pd.concat(out_of_bounds).sort_values("membership_number").to_string(index=False)
        warnings.warn(f"Dates out of bound: \n {oob_string}", RuntimeWarning)

    return data


def _load_training_report(path_training: Path) -> pd.DataFrame:
    log.debug("Merging with training report data")

    # now Training
    data_training = _load_data(path_training, skip_rows=3)
    try:
        training_cols_map = canonicalisation_training.map_input_fields(data_training.columns)
    except ValueError as err:
        raise RuntimeError("Columns aren't valid!") from err

    # rename headings
    data_training.columns = data_training.columns.map(training_cols_map)

    # Remove non-numeric membership numbers
    data_training[fields_training.CONTACT_NUMBER] = pd.to_numeric(data_training[fields_training.CONTACT_NUMBER], errors="coerce")
    data_training = data_training.dropna(subset=[fields_training.CONTACT_NUMBER])
    data_training[fields_training.CONTACT_NUMBER] = pd.to_numeric(data_training[fields_training.CONTACT_NUMBER], downcast="unsigned")

    # Remove unneeded & null roles
    data_training = data_training[data_training[fields_training.ROLE].notna()]
    data_training = data_training[~data_training[fields_training.ROLE].str.contains("Occasional Helper", regex=False, case=False)]

    # Parse validated_date & remove null
    data_training = data_training.dropna(subset=[fields_training.VALIDATED_DATE])
    data_training[fields_training.VALIDATED_DATE] = pd.to_datetime(data_training[fields_training.VALIDATED_DATE], format="%d/%m/%Y")

    return data_training


def _merge_training_report(data_training: pd.DataFrame, data_appointments: pd.DataFrame) -> pd.DataFrame:

    # Modules we want to capture from the training report.
    # Currently, M01Ex, M04, GDPR, LMS, M23
    lookup = {
        fields_training.module_GDPR: fields.GDPR,  # Always
        fields_training.module_mod_4: fields.MOD_04,  # Always
        fields_training.module_mod_23_ended: fields.MOD_23,  # Always

        fields_training.module_mod_1_ex_ended: fields.MOD_01_EX,  # If after Sep 2020
        fields_training.module_mod_1_ex_ended2: fields.MOD_01_EX,  # If immediately after Sep 2020
        fields_training.module_mod_1_ex: fields.MOD_01_EX,  # If before Sep 2020

        # We only want the type of training that validated Safety automatically, so not the new SMS etc
        fields_training.module_mod_LMS_ended: fields.MOD_LMS,  # If after Sep 2020
        fields_training.module_mod_LMS: fields.MOD_LMS,  # Always
    }
    data_training = data_training[data_training[fields_training.MODULE].isin(lookup.keys())]

    # OK, got the data.  What common sort columns do we have?
    keys = ["membership_number", "region", "county", "district", "scout_group", "role"]

    # reshape training

    # extract the sort keys, module & validated date
    reshape_cols = keys + [fields_training.MODULE]
    reshaped_training = data_training[[*reshape_cols, fields_training.VALIDATED_DATE]]
    # Keep latest date for each role, module pair
    reshaped_training = reshaped_training.sort_values(fields_training.VALIDATED_DATE, ascending=False).drop_duplicates(subset=reshape_cols)
    # create a multi-index and yank modules to columns, with cells of validation dates.
    reshaped_training = reshaped_training.fillna("<blank>").set_index(reshape_cols)
    reshaped_training = reshaped_training.unstack(-1)

    # OK, tidy up a bit

    # drop column multi-index, to just keep labels as module values
    reshaped_training.columns = reshaped_training.columns.droplevel()
    # back to 'normal' dataframe
    reshaped_training = reshaped_training.reset_index().replace("<blank>", pd.NA)

    # filter modules not wanted, rename columns
    fields_to_keep = keys + list(set(reshaped_training.columns) & lookup.keys())
    reshaped_training = reshaped_training[fields_to_keep]

    # Merge & drop the training keys
    merged = data_appointments.merge(reshaped_training, how="left", on=keys)

    log.info("Appointments and Training Reports merged")
    # TODO does Peter sort the data?

    # Cols training report also (maybe) in appointments report
    merged_columns = set(merged.columns)
    for training_mod, headings_mod in lookup.items():
        if training_mod in merged_columns:
            if headings_mod in merged_columns:
                # If module is in both Training & Appointments reports, use latest date
                # (not applicable for M01/M01Ex)
                merged[headings_mod] = merged[[training_mod, headings_mod]].max(axis=1)
            else:
                # Otherwise (if just in training report), rename
                merged[headings_mod] = merged[training_mod]

    # Drop all Training Report modules, ignore errors if non-extant key.
    merged = merged.drop(columns=lookup.keys(), errors="ignore")

    return merged
