from __future__ import annotations

from pathlib import Path
import shutil

import pandas as pd

from assistants.utility import excel_interface

ADULT_INFO_FIELDS = ["membership_number", "known_as", "surname", "email", "country", "region", "county", "district", "scout_group"]


def overdue_adults_by_type(
    extract_data: pd.DataFrame,
    types: list[str],
    types_map: dict[str, str] = None,
) -> pd.DataFrame:
    extract_data = extract_data.copy()  # fix set with copy warning (we assign to the original data when adding overdue since dates)
    if types_map:
        names = [types_map.get(t, t) for t in types]
    else:
        names = types
    cols = [f"ByAdult{t}" for t in types]

    # Get boolean matrix of overdue or not by adult, and a scalar per adult if any are overdue
    od_arr = extract_data[cols] == "overdue"
    od_adults = od_arr.any(axis=1)

    # add overdue since dates, if they exist
    g = extract_data.groupby("membership_number")
    _od_since_cols = []
    for t in types:
        if f"DueBy{t}" not in extract_data.columns:
            continue
        _od_since_cols.append(f"{t.lower()}_od_since")
        # Min non-compliant since//due by date by member
        extract_data[f"{t.lower()}_od_since"] = g[f"DueBy{t}"].transform("min")
        # Blank out compliant values
        extract_data.loc[~od_arr[f"ByAdult{t}"], f"{t.lower()}_od_since"] = float("NaN")

    # Create output array
    overdue_out = extract_data.loc[od_adults, ADULT_INFO_FIELDS + _od_since_cols].sort_values("membership_number").reset_index(drop=True)

    # Map true values to the names list
    mapped = od_arr[od_adults] * names

    # Join the columns, ignoring blank strings
    overdue_out["type"] = [", ".join(filter(None, row)) for row in zip(*(mapped.iloc[:, i] for i in range(len(cols))))]

    # Sort for presentation
    overdue_out = overdue_out.sort_values(["district", "scout_group"], kind="stable")
    overdue_out["district"] = overdue_out["district"].fillna("County")

    return overdue_out


def compliance_supporting_data(data: pd.DataFrame, region: str) -> None:
    date = data.attrs["report_date"]
    print(f"CSD - {date}")

    # data sources (dataframe, file slug, excel sheet/tab name)
    sources: dict[str, pd.DataFrame] = {
        "Appointments": data,
        "Auto Safety": _old_safety_auto_validate(data),  # Old safety auto validate modules
        "Persistent": overdue_adults_by_type(data, ["Safety", "Safeguarding"]),  # persistently
        "No Email": _no_email(data),  # No email address
    }

    template_report = Path("data/compliance-supporting-data/csd-county-template.xlsx")
    counties = sorted(c for c in set(data["county"].array.to_numpy()) if c == c) + ["Region"]
    for county in counties:
        is_region_team = county == "Region"
        print(f"CSD - {county} starting")
        report_path = template_report.parent / region / county / f"csd - {date} - {county}.xlsx"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(template_report, report_path)
        with excel_interface.excel_interface(report_path) as xl:
            for sheet_name, source in sources.items():
                # r = range(10**6)  # Helper
                mask = source["county"].isna() if is_region_team else source["county"] == county
                excel_interface.write_to_workbook(
                    xl,
                    source.loc[mask],
                    sheet_name=sheet_name,
                    start_row=2,
                    # hidden_columns={"Appointments": r[35:161 + 1], },
                    df_to_excel_kwargs={"header": False, "index": False},
                )


def _old_safety_auto_validate(data: pd.DataFrame) -> pd.DataFrame:
    data = data.copy()  # we assign to the original data
    old_auto_safety_cols = ["safety", "mod_lms", "mod_23"]

    # Are auto-safety columns present (subset check)?
    if not {"mod_23", "mod_lms"} < set(data.columns):
        return pd.DataFrame(data=None, columns=ADULT_INFO_FIELDS + old_auto_safety_cols)  # empty DF

    g = data.groupby("membership_number")
    for col in old_auto_safety_cols:
        data[col] = g[col].transform("max")
    return data.loc[data["safety_flag"], ADULT_INFO_FIELDS + old_auto_safety_cols].drop_duplicates(subset={"membership_number"})


def _no_email(data: pd.DataFrame) -> pd.DataFrame:
    """No email address"""
    return data.loc[data["email"].isna(), ADULT_INFO_FIELDS].drop_duplicates(subset={"membership_number"})
