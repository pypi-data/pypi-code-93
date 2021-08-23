from __future__ import annotations

import datetime
import json
import operator
from pathlib import Path
from typing import Any, TYPE_CHECKING

import pandas as pd

if TYPE_CHECKING:
    from collections.abc import Iterable

TWO_WEEKS = 7 * 2
FOUR_WEEKS = 7 * 4
SIX_WEEKS = 7 * 6


def write_narrative(
    path: Path,
    district_data: pd.DataFrame,
    latest_date: datetime.date,
    region: str,
    england_avg_compliance: float,
    sections: Iterable[str]
) -> None:
    overview_stats, narrative_text = create_narrative(district_data, latest_date, england_avg_compliance, region, sections)
    path.with_suffix(".md").write_text(narrative_text)
    path.with_suffix(".json").write_text(json.dumps(overview_stats, default=str))


def create_narrative(
    district_data: pd.DataFrame,
    date: datetime.date,
    england_avg_compliance: float,
    region: str,
    sections: Iterable[str] = None,
) -> tuple[dict[str, dict[str, Any]], str]:
    # create_overview
    days_from_earliest = (date - district_data["Date"].array.to_numpy().min()).days
    if days_from_earliest >= FOUR_WEEKS:
        comp_date = date - datetime.timedelta(days=FOUR_WEEKS)
        print(f"Comparing 4 weeks (comp date: {comp_date})")
    elif days_from_earliest >= TWO_WEEKS:
        comp_date = date - datetime.timedelta(days=TWO_WEEKS)
        print(f"Comparing 2 weeks (comp date: {comp_date})")
    else:
        raise RuntimeError("Cannot find a valid compare date")

    idx_cols = ["Date", "region", "county", "district"]

    # DataFrame setup
    summary_data, district_records = _setup_summary_frame(district_data, date, comp_date, idx_cols)

    b3_worst_abs = {}
    b4_worst_pct = {}

    summary = {col: {} for col in summary_data.columns.levels[0]}
    timestamp = pd.Timestamp(date)
    for col, summary_dict in summary.items():
        summary_dict["latest"] = df_latest = summary_data.loc[district_records, (col, timestamp.date())]
        summary_dict["diff"] = summary_data.loc[district_records, col].groupby(level=-1, axis=1).diff(1, axis=1).dropna(axis=1).droplevel(level=0, axis=1)

        # Overall bullet 6 (get name of worst district by # overdue)
        b3_worst_abs[col] = df_latest["Overdue"].sort_values().index[-1][2]

        # Overall bullet 7 (get name of worst district by % overdue)
        b4_worst_pct[col] = df_latest["Over%Req"].sort_values().index[-1][2]

    # Setup dicts
    stats = {}
    overall = stats["Overall"] = {}

    # Setup further bullets
    overall["worst_abs"] = b3_worst_abs
    overall["worst_pct"] = b4_worst_pct

    # narrative_text
    narrative: list[str] = []

    # Stringify dates
    run_date_str = date.strftime("%d %B %Y")
    next_fortnight_str = (date + datetime.timedelta(days=TWO_WEEKS)).strftime("%d %B %Y")

    # For multi-key lookups, define core and additional MOGL types
    core_mogl = ("Safety", "Safeguarding")
    adtl_mogl = ("FirstAid", "GDPR")

    # OVERALL BULLETS SECTION STARTS

    narrative.append(f"**{run_date_str} Training Compliance Summary - {region}:**")
    narrative.append("")  # newline

    # Overall Section
    narrative.append("*Overall:*")

    # Bullet 1 (Overall)
    if days_from_earliest >= SIX_WEEKS:  # Previous fortnight
        six_weeks = date - datetime.timedelta(days=SIX_WEEKS)
        two_weeks = date - datetime.timedelta(days=TWO_WEEKS)
        prev_fortnight, pf_district_records = _setup_summary_frame(district_data, two_weeks, six_weeks, idx_cols)
        prev_fortnight_means = prev_fortnight[pf_district_records].xs("Overdue", level=-1, axis=1)
        prev_fortnight_means = prev_fortnight_means.groupby(level=0, axis=1).diff(1, axis=1).mean()
        overall["prev_fortnight_means"] = prev_fortnight_means = prev_fortnight_means.dropna().droplevel("Date").to_dict()
    else:
        prev_fortnight_means = None

    overall["means"] = b1_means = {col: float(summary_dict["diff"]["Overdue"].mean()) for col, summary_dict in summary.items()}
    b1_mean_improvement = sum(_mkl(b1_means, core_mogl)) / -len(core_mogl)
    b1_status = "improving" if b1_mean_improvement > 0 else "worsening"
    if prev_fortnight_means is not None:
        prev_fortnight_mean_improvement = sum(_mkl(prev_fortnight_means, core_mogl)) / -len(core_mogl)
        b1_changed = "increased" if b1_mean_improvement >= prev_fortnight_mean_improvement else "decreased"
        b1_comparison = f"This has {b1_changed} from {prev_fortnight_mean_improvement:.1f} adults/district/month last fortnight."
    else:
        b1_comparison = ""
    narrative.append(
        f"""- Compliance is generally {b1_status}, with each district improving their 
        average compliance figures by an average of {b1_mean_improvement:.1f} adults. 
        {b1_comparison}
        """
    )

    # Bullet 2 (Overall)
    region_avg_compliance = summary_data.loc[(region, region, region), (("Safety", "Safeguarding"), timestamp.date(), "Over%Req")].mean()
    comp_england = "better" if region_avg_compliance < england_avg_compliance else "worse"
    narrative.append(
        f"""- As a region, we are on average {comp_england} than England as a whole 
        ({region_avg_compliance:.2%} vs {england_avg_compliance:.2%})."""
    )

    # Bullet 3 (Overall)
    worst_abs_safe_sfty = _singular_plural(b3_worst_abs, core_mogl)
    worst_abs_fa_gdpr = _singular_plural(b3_worst_abs, adtl_mogl)
    narrative.append(
        f"""- By the total adults overdue, {worst_abs_safe_sfty} the lowest performance across both Safety and 
        Safeguarding compliance respectively. 
        {worst_abs_fa_gdpr} the lowest performance across First Aid and GDPR compliance."""
    )

    # Bullet 4 (Overall)
    worst_pct_safe_sfty = _singular_plural(b4_worst_pct, core_mogl)
    worst_pct_fa_gdpr = _singular_plural(b4_worst_pct, adtl_mogl)
    narrative.append(
        f"""- By percent of adults overdue, {worst_pct_safe_sfty} the lowest performance across both Safety and 
        Safeguarding compliance. 
        {worst_pct_fa_gdpr} the lowest performance across First Aid and GDPR compliance."""
    )

    narrative.append("")  # newline

    # Loop through specific training types (if sections is unset use sensible defaults)
    for category in sections or ("Safety", "Safeguarding", "FirstAid", "GDPR"):
        training_dicts = summary[category]

        df_diff = training_dicts["diff"]
        diff_sorted_abs = df_diff["Overdue"].sort_values(ascending=False)
        diff_sorted_pct = df_diff["Over%Req"].sort_values(ascending=False)

        districts_abs_diffs = diff_sorted_abs.droplevel([0, 1])
        districts_pct_diffs = diff_sorted_pct.droplevel([0, 1])

        stats[category] = specific_stats = {}

        category_str = "First Aid" if category == "FirstAid" else category
        narrative.append(f"*{category_str}:*")

        # Bullet 1 (Specific)
        specific_stats["best_pct"] = pct_best_dist, pct_best = districts_pct_diffs.index[-1], -districts_pct_diffs.array[-1]
        # Want at least 3 districts with given change
        bound = _get_bound((-0.5, -1, -1.5, -2, -5), diff_sorted_pct, clip_lower=3, maximise=False)
        if bound:
            pct_ten = (diff_sorted_pct <= bound / 100).sum()
            specific_stats["ten_pct"] = pct_ten, bound
            pct_ten_str = f"{pct_ten} districts have generated a {bound}% or greater improvement."
        else:
            specific_stats["ten_pct"] = None, None
            pct_ten_str = ""
        narrative.append(
            f"""- The district with the largest improvement in {category_str} training was **{pct_best_dist}**, with a {pct_best:.1%} improvement. """
            + pct_ten_str
        )

        # Bullet 2 (Specific)
        specific_stats["best_abs"] = abs_best_dist, abs_best = districts_abs_diffs.index[-1], -districts_abs_diffs.array[-1]
        # min improvement of 5 adults or actual improvement rounded up (closer to 0 as -ve) to nearest 5
        bound = min(-5, int(-abs_best / 5) * 5)
        specific_stats["abs_next_best"] = abs_next_best = diff_sorted_abs.droplevel([0, 1]).index[diff_sorted_abs <= bound].tolist()[:-1]
        if abs_next_best:
            next_best_text = _stringify_list(abs_next_best, concat="and") + " have each generated a net decrease of over 10 non-compliant adults!"
        else:
            next_best_text = ""
        narrative.append(
            f"""- **{abs_best_dist}** has generated a net decrease of {abs_best} adults with 
            overdue {category_str} training! """
            + next_best_text
        )

        # Bullet 3 (Specific)
        overdue_pct = training_dicts["latest"]["Over%Req"].reset_index([0, 1], drop=True)
        latest_sorted_pct = overdue_pct.sort_index(ascending=False).sort_values(ascending=False, kind="stable")
        specific_stats["number_one"] = number_one = latest_sorted_pct.index[-1]
        specific_stats["number_one_pct"] = number_one_pct = latest_sorted_pct.array[-1]
        # If best percentage is better than 5%, add an exclamation mark!
        number_one_exclaim = "!" if number_one_pct < 5 / 100 else "."

        # Want max# of districts at given % clipped to 20
        if (latest_sorted_pct == 0).sum() < 20:
            bound = _get_bound((0.1, 0.25, 0.5, 1, 2, 3, 4, 5, 10, 15, 20), latest_sorted_pct, clip_upper=20, maximise=True)
        else:
            bound = 0
        if bound is not None:
            district_labels = latest_sorted_pct.index.get_level_values("district")
            best_districts_lst = [*reversed(district_labels[latest_sorted_pct <= (bound / 100)])][1:]
            best_districts_bound = bound
        else:
            best_districts_lst = best_districts_bound = None
        specific_stats["best_districts"] = best_districts_lst, best_districts_bound

        best_districts = _stringify_list(best_districts_lst, include_first=False)
        narrative.append(
            f"""- The best district for {category_str} compliance (by % overdue) is **{number_one}**, at 
            {number_one_pct:.1%} overdue {category_str} training{number_one_exclaim} 
            Districts under {best_districts_bound}% non-compliance are {best_districts}."""
        )
        narrative.append("")  # newline

    narrative.append(f"The next bulletin will come using data from {next_fortnight_str}.")
    return stats, "\n".join(" ".join(line.split()) for line in narrative)


def _setup_summary_frame(data: pd.DataFrame, curr_date: datetime.date, old_date: datetime.date, idx_cols: list[str]):
    # Get relevant data
    date_mask = data["Date"].isin({curr_date, old_date})
    summary_frame = data.loc[date_mask].set_index(idx_cols)
    summary_frame.columns = summary_frame.columns.str.split("|", expand=True)
    summary_frame = summary_frame.unstack(0).reorder_levels([1, 2, 0], axis=1).sort_index(axis=1)

    # Get locations of `true` districts (i.e. not counties / county teams / region teams)
    non_district_names = {"County Team"} | set(summary_frame.index.get_level_values("county"))
    district_mask = ~summary_frame.index.isin(non_district_names, level="district")
    return summary_frame, district_mask


def _get_bound(trial_values, array, *, clip_upper: int = None, clip_lower: int = None, maximise: bool = True) -> float | int:
    # clips & max can only be keyword
    if clip_upper is not None:
        if clip_lower is not None:
            raise ValueError("Only one of clip_upper or clip_lower must be set!")
        bound = -(2 ** 16)
        clip = clip_upper
    else:
        if clip_lower is None:
            raise ValueError("At least one of clip_upper or clip_lower must be set!")
        bound = 2 ** 16
        clip = clip_lower

    for x in trial_values:
        count = (array <= x / 100).sum()
        if maximise:
            if count <= clip and x > bound:
                bound = x
        else:
            if count >= clip and x < bound:
                bound = x
    return bound if abs(bound) != 2 ** 16 else None


def _mkl(dictionary: dict, keys: tuple) -> tuple:
    """multi-key lookup."""
    return operator.itemgetter(*keys)(dictionary)


# bullets 6/7
def _singular_plural(dct: dict, keys: tuple) -> str:
    if dct[keys[0]] == dct[keys[1]]:
        return f"**{dct[keys[0]]}** has"
    return f"**{dct[keys[0]]}** and **{dct[keys[1]]}** have"


def _stringify_list(values: list[str], include_first: bool = True, concat: str = "&") -> str:
    start = 0 if include_first else 1
    return "**" + ", ".join(values[start:-1]) + f"** {concat} **" + "".join(values[-1:]) + "**"
