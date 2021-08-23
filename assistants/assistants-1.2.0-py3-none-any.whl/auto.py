from __future__ import annotations

from pathlib import Path

import compass.core as ci


def appointments_report(export_path: Path, username: str, password: str, *, role: str | None = None) -> None:
    api = ci.login(username, password, role=role)
    appointments_report_csv = api.reports.get_report("Appointments Report")
    export_path.write_text(appointments_report_csv, "utf-8")
