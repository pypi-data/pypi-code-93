from __future__ import annotations

from typing import NamedTuple, TYPE_CHECKING

if TYPE_CHECKING:
    import pandas as pd


class SummaryStatistics:
    __slots__ = "total", "completed", "due_soon", "overdue", "start", "completed_percent", "due_soon_percent", "overdue_percent"

    def __repr__(self) -> str:
        return f"<SummaryStatistics Req: {self.total} | Overdue: {self.overdue} | Soon: {self.due_soon}>"

    def __init__(self, data: pd.DataFrame, types: list[str], by_adult: bool = False):
        prefix = "ByAdult" if by_adult else "Type"
        self.completed = self.due_soon = self.overdue = self.start = 0
        for t in types:
            aggregated_col: dict[str, int] = data[prefix + t].value_counts().to_dict()
            self.completed += aggregated_col.get("valid", 0)
            self.due_soon += aggregated_col.get("soon", 0)
            self.overdue += aggregated_col.get("overdue", 0)
            self.start += aggregated_col.get("start", 0)
        self.total = self.completed + self.due_soon + self.overdue + self.start

        self.completed_percent = self.due_soon_percent = self.overdue_percent = 0.0
        if self.total:
            self.completed_percent = (self.completed / self.total) * 100
            self.due_soon_percent = (self.due_soon / self.total) * 100
            self.overdue_percent = (self.overdue / self.total) * 100


class SummaryOverview(NamedTuple):
    adult_count: int  # Row 13
    roles: SummaryStatistics  # Row 14
    aac: SummaryStatistics  # Row 18
    references: SummaryStatistics  # Row 19
    commcomm: SummaryStatistics  # Row 20
    mod_01: SummaryStatistics  # Row 22
    mod_1ex: SummaryStatistics  # Row 23
    gdpr: SummaryStatistics  # Row 24
    mod_03: SummaryStatistics  # Row 23
    mod_04: SummaryStatistics  # Row 27
    mod_02: SummaryStatistics  # Row 28
    wb_sect: SummaryStatistics  # Row 32
    wb_mgr: SummaryStatistics  # Row 33
    first_aid: SummaryStatistics  # Row 35
    safety: SummaryStatistics  # Row 36
    safeguarding: SummaryStatistics  # Row 37
    review: SummaryStatistics  # Row 38


def generate_summary_stats(data: pd.DataFrame) -> SummaryOverview:
    return SummaryOverview(
        adult_count=data["AdultCount"].sum(),  # Row 13
        roles=SummaryStatistics(data, ["Preprov"]),  # Row 14
        aac=SummaryStatistics(data, ["AAC"]),  # Row 18
        references=SummaryStatistics(data, ["Refs"]),  # Row 19
        commcomm=SummaryStatistics(data, ["Commissioner", "Committee"]),  # Row 20
        mod_01=SummaryStatistics(data, ["Mod1"], by_adult=True),  # Row 22
        mod_1ex=SummaryStatistics(data, ["Trustee"], by_adult=True),  # Row 23
        gdpr=SummaryStatistics(data, ["GDPR"], by_adult=True),  # Row 24
        mod_03=SummaryStatistics(data, ["Mod3"]),  # Row 26
        mod_04=SummaryStatistics(data, ["Mod4"]),  # Row 27
        mod_02=SummaryStatistics(data, ["Mod2"]),  # Row 28
        wb_sect=SummaryStatistics(data, ["SectionWb"]),  # Row 32
        wb_mgr=SummaryStatistics(data, ["MgrWb"]),  # Row 33
        first_aid=SummaryStatistics(data, ["FirstAid"], by_adult=True),  # Row 35
        safety=SummaryStatistics(data, ["Safety"], by_adult=True),  # Row 36
        safeguarding=SummaryStatistics(data, ["Safeguarding"], by_adult=True),  # Row 37
        review=SummaryStatistics(data, ["Review"]),  # Row 38
    )
