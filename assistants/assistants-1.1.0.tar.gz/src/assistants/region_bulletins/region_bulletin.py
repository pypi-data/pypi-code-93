from __future__ import annotations

import datetime
from pathlib import Path
from typing import TYPE_CHECKING

import pandas as pd

from assistants.compliance.compliance_assistant import create_compliance_assistant_report
from assistants.log_status import log
from assistants.region_bulletins.aggregate import get_stacked
from assistants.region_bulletins.narrative_text import write_narrative
from assistants.region_bulletins.supporting_data import compliance_supporting_data

if TYPE_CHECKING:
    from collections.abc import Iterable

DATA_ROOT = Path(__file__).parent.parent.parent.parent / "data"


def run_for_region(
    root_path: Path,
    training_types: Iterable[str],
    appointments_folder: str,
    training_folder: str,
    region: str,
    england_avg_compliance: float,
    report_narrative: bool = True,
    csd: bool = True,
) -> None:
    all_totals: list[pd.DataFrame] = []
    all_extracts: list[pd.DataFrame] = []

    appointments_root = root_path / region / appointments_folder
    training_root = root_path / region / training_folder
    extracts = list(appointments_root.glob(f"Region Appointments Report (Beta) - {region} - *.csv"))

    # Mapping of renamed districts
    renamed_districts = {
        "Harborough": "Market Harborough",  # East Midlands, Leicestershire: renamed 2020-11-02/09
        "Leven": "North Hambleton",  # North East, North Yorkshire: merged & renamed 2021-04-01
        "Northallerton": "North Hambleton",  # North East, North Yorkshire: merged & renamed 2021-04-01
    }

    for file in extracts:
        extract_date = datetime.date.fromisoformat(file.stem[-10:])  # len("YYYY-mm-dd") == 10
        output = DATA_ROOT / f"reports/{file.stem.replace('Region Appointments Report (Beta)', 'region appts report')}.feather"
        if output.is_file():
            extract_data = pd.read_feather(output)
            extract_data.attrs["report_date"] = extract_date
            log.info(f"Loaded compliance report - {extract_date}")
        else:
            training_file = training_root / file.stem.replace("Appointments", "Training")
            extract_data = create_compliance_assistant_report(extract_date, file, training_file=training_file)
            extract_data.to_feather(output)  # preserve booleans

        extract_data["district"] = extract_data["district"].replace(renamed_districts)  # rename districts
        # extract_data = extract_data[extract_data["DELMGRGOVSUP"] == "DEL"]  # filer to delivery roles
        totals = get_stacked(extract_data, training_types)
        all_totals.append(totals)
        all_extracts.append(extract_data)

    latest_extract = all_extracts[-1]
    latest_date = latest_extract.attrs["report_date"]
    print(f"LATEST DATE: {latest_date}")

    if report_narrative:
        district_data = pd.concat(all_totals).reset_index(drop=True)
        totals_for_pivot_table = get_stacked(latest_extract, training_types, hierarchy_level="group", pre_calculate=False)

        bulletins_root = DATA_ROOT / "bulletins"
        file_name = bulletins_root / f"district data - {region} - {latest_date}"
        district_data.to_csv(file_name.with_suffix(".csv"), encoding="utf-8-sig", index=False)
        totals_for_pivot_table.to_csv(f"{file_name} [pivot].csv", encoding="utf-8-sig", index=False)

        # experimental JSON save
        district_data.to_json(file_name.with_suffix(".json"), "split", date_format="epoch", date_unit="s", index=False)
        totals_for_pivot_table.to_json(f"{file_name} [pivot].json", "split", date_format="epoch", date_unit="s", index=False)

        write_narrative(
            bulletins_root / f"overview_stats - {latest_date} - {region}.md",
            district_data,
            latest_date,
            region,
            england_avg_compliance,
            training_types,
        )

    if csd:
        compliance_supporting_data(latest_extract.data, region)

    # TODO Features, Improvements:
    #  - report DBS
    #  - ---
    #  - report category (M/S/D/G)
    #  - report ASU etc - perhaps linked to category
    #  - report role level aggregate (somehow) - i.e. XXX at group section level, YYY at group level, ....
    #  - ---
    #  - generalise the entire excel workbook
    #  - ---
    #  - improve group roles etc workbooks from 28 Aug minutes
