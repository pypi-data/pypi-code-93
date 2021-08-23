from __future__ import annotations

from typing import Literal, TYPE_CHECKING
import warnings

import pandas as pd

from assistants.log_status import log

if TYPE_CHECKING:
    from collections.abc import Iterable
    import datetime


def get_stacked(
    data: pd.DataFrame,
    cols: Iterable[str],
    hierarchy_level: Literal["group", "district", "county"] = "district",
    pre_calculate: bool = True,
    sub_totals: bool = True,
) -> pd.DataFrame:
    run_date: datetime.date = data.attrs["report_date"]
    cols = [*cols]
    log.info(f"Getting compliance types by location: {', '.join(cols)}")

    location_cols = ["region", "county"]
    if hierarchy_level == "district":
        location_cols += ["district"]
    elif hierarchy_level == "group":
        location_cols += ["district", "scout_group"]

    # Get aggregated compliance report by location
    aggregated = _get_aggregated(data, cols, location_cols, pre_calculate, sub_totals)

    # Add date column
    aggregated.insert(0, "Date", run_date)
    return aggregated


def _get_aggregated(
    data: pd.DataFrame,
    compliance_types: list[str],
    location_cols: list[str],
    pre_calculate: bool,
    sub_totals: bool,
) -> pd.DataFrame:
    # Prepare and group data
    data[location_cols] = data[location_cols].fillna("| <blank>")

    # Check compliance types present
    existing_types = {col[7:] for col in data.columns if col.startswith("ByAdult")}
    if missing_types := set(compliance_types) - existing_types:
        warnings.warn(f"Did not run for missing compliance type(s) {sorted(missing_types)}!", RuntimeWarning)
        compliance_types = [col for col in compliance_types if col in existing_types]

    # Aggregate
    by_adult_cols = [f"ByAdult{col}" for col in compliance_types]
    required_cols = ~data[by_adult_cols].isin({"not_req", "not_primary_role"}).set_axis([f"Required|{col}" for col in compliance_types], axis=1)
    overdue_cols = (data[by_adult_cols] == "overdue").set_axis([f"Overdue|{col}" for col in compliance_types], axis=1)
    totals = pd.concat([data[location_cols], required_cols, overdue_cols], axis=1).groupby(by=location_cols).sum()

    # Replace <blank> with `level` Team
    naming_map = {"scout_group": "group"}
    totals_index = totals.index.to_frame(index=False)
    for i, hierarchy_level in enumerate(location_cols[1:]):
        prev_level = location_cols[i]
        curr_level_down = location_cols[i + 1:]
        proper_name = naming_map.get(prev_level, prev_level)
        totals_index.loc[totals_index[hierarchy_level] == "| <blank>", curr_level_down] = f"| # {proper_name.title()} Team"
    totals.index = pd.MultiIndex.from_frame(totals_index)

    if pre_calculate:
        aggregated_totals = [totals]
        if sub_totals:
            for i, level in enumerate(location_cols[:-1]):
                # helper definitions
                curr_level_up = location_cols[:i + 1]
                descendent_levels = location_cols[i + 1:]

                # aggregate
                level_totals = totals.groupby(by=curr_level_up).sum()

                # set index
                level_index = level_totals.index.to_frame(index=False)
                descendent_levels_indices = [("| " + level_index[level]).str.replace("| |", "|", regex=False)]
                level_index[descendent_levels] = pd.concat(descendent_levels_indices * len(descendent_levels), axis=1, keys=descendent_levels)

                # add to aggregated_totals
                aggregated_totals.append(level_totals.set_index(pd.MultiIndex.from_frame(level_index)))

        # Combine and sort
        all_totals = pd.concat(aggregated_totals).reset_index()

        # Sort and remove tokens that force sort order (# and |)
        all_totals = all_totals.sort_values(by=location_cols).drop_duplicates().reset_index(drop=True)
        for hierarchy_level in location_cols:
            all_totals[hierarchy_level] = all_totals[hierarchy_level].str.replace(r"\| (# )?", "", regex=True)

        # Calculate rates
        for col in compliance_types:
            all_totals["Over%Req|" + col] = all_totals[f"Overdue|{col}"] / all_totals[f"Required|{col}"]
            all_totals = all_totals.drop(columns=f"Required|{col}")

        order = location_cols + [f"Overdue|{col}" for col in compliance_types] + [f"Over%Req|{col}" for col in compliance_types]
        return all_totals[order]

    # Move index to columns
    all_totals = totals.reset_index()

    # Sort and remove tokens that force sort order (# and |)
    for hierarchy_level in location_cols:
        all_totals[hierarchy_level] = all_totals[hierarchy_level].str.replace(r"\| (# )?", "", regex=True)

    order = location_cols + [f"Overdue|{col}" for col in compliance_types] + [f"Required|{col}" for col in compliance_types]
    return all_totals[order]
