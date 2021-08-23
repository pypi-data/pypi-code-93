from __future__ import annotations

from typing import Optional, TYPE_CHECKING

import pandas as pd

from assistants.compliance import calculation_logic
from assistants.compliance.cleaning import fix_compliance_dates
from assistants.compliance.cleaning import roles_to_requirements
from assistants.compliance.cleaning import preprocessing
from assistants.log_status import log

if TYPE_CHECKING:
    import datetime
    from pathlib import Path


# ========================================================================================
#
# Main entry point
#
# ========================================================================================
def create_compliance_assistant_report(run_date: datetime.date, filename: Path, training_file: Optional[Path] = None) -> pd.DataFrame:
    if run_date < calculation_logic.date_transition.date():
        raise ValueError("This version of the Compliance Assistant only supports extracts from after the September 2020 Compass changes.")

    # Load & preprocess data
    raw_data = preprocessing.preprocess_data(filename, training_file, log_raw_data=False)
    log.info("Data loaded and cleaned.")

    # make sure gdpr, Module 1, Safety Safeguarding and First Aid are applied across all roles
    data = fix_compliance_dates.fix_some_dates(raw_data)
    log.info("Dates fixed")

    # now do the hard work - put in requirements
    data = roles_to_requirements.merge_roles_table(data)
    log.info("Roles table joined")

    # work out compliance stuff
    data = calculation_logic.calculate_compliance(data, run_date)
    log.info("Compliance calculated")

    data = data.drop(columns=["mod_lms", "mod_23", "safety_flag"], errors="ignore")
    log.info(f"Compliance report processed - {run_date}")

    data.attrs["report_date"] = run_date

    return data
