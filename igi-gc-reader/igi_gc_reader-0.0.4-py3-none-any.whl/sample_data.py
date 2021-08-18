from dataclasses import dataclass, field
from typing import Iterator, Optional, DefaultDict, List, Any, Tuple
from collections import defaultdict
import logging

from igi_gc_reader.reader.gc_page import GcPageData


@dataclass
class TargetHeaders:
    a: str
    h: str
    ca: str
    ch: str


@dataclass
class SourceColumnNames:
    prop: str = field(default="")
    prop_desc: str = field(default="")
    a: str = field(default="")
    h: str = field(default="")
    ca: str = field(default="")
    ch: str = field(default="")
    ion: Optional[str] = field(default=None)

    def get_target_headers(self, prop_val: str, igi_analysis: str = "WO-GC") -> TargetHeaders:
        return TargetHeaders(
            a=f"{prop_val}[a].{igi_analysis}<count>",
            h=f"{prop_val}[h].{igi_analysis}<count>",
            ca=f"{prop_val}[ca].{igi_analysis}<{self.get_ca_uom()}>",
            ch=f"{prop_val}[ch].{igi_analysis}<{self.get_ch_uom()}>"
        )

    def get_ca_uom(self) -> str:
        return self.clean(self.ca, rmv=["area", "(", ")"])

    def get_ch_uom(self) -> str:
        return self.clean(self.ch, rmv=["height", "hght", "(", ")"])

    def clean(self, val: str, rmv: List[str]) -> str:
        val = val.lower()
        for rm in rmv:
            val = val.replace(rm, "")
        return val.strip()


@dataclass
class SampleData:
    """Page data restructured as a single sample row."""
    page_data: GcPageData
    igi_analysis: str
    _col_head_to_values: DefaultDict[str, List[Any]] = field(
        default_factory=lambda: defaultdict(list))
    _page_data_cols: SourceColumnNames = field(init=False)

    def __post_init__(self):
        heads = self.page_data.get_headers()
        for row in self.page_data.get_data():
            for head, val in zip(heads, row):
                self._col_head_to_values[head].append(val)
        self._page_data_cols = self._get_page_data_cols()

    def get_headers(self) -> Iterator[Tuple[str, Optional[str]]]:
        cols = self._page_data_cols
        ions = self._col_head_to_values[cols.ion] if cols.ion else [
            None for _ in self._col_head_to_values[cols.prop]]
        for prop_value, prop_desc, ion in zip(self._col_head_to_values[cols.prop],
                                              self._col_head_to_values[cols.prop_desc],
                                              ions):
            use_prop = prop_value if prop_value else prop_desc
            target_headers = cols.get_target_headers(use_prop, self.igi_analysis)
            yield target_headers.a, ion
            yield target_headers.h, ion
            yield target_headers.ca, ion
            yield target_headers.ch, ion

    def get_sample_row(self) -> Iterator[str]:
        cols = self._page_data_cols
        d = self._col_head_to_values
        for a, h, ca, ch in zip(d[cols.a], d[cols.h], d[cols.ca], d[cols.ch]):
            yield a
            yield h
            yield ca
            yield ch

    @property
    def n_header_rows(self) -> int:
        return 2 if self._page_data_cols.ion is not None else 1

    def _get_page_data_cols(self) -> SourceColumnNames:
        cols = SourceColumnNames()
        heads = self.page_data.get_headers()
        for head in heads:
            formatted_header = head.title()
            if formatted_header == "Ion":
                cols.ion = head
            elif formatted_header == "Peak Label":
                cols.prop = head
            elif formatted_header == "Compound Name":
                cols.prop_desc = head
            elif formatted_header == "Ret. Time":
                continue
            elif formatted_header == "Area":
                cols.a = head
            elif formatted_header == "Height":
                cols.h = head
            elif "Area" in formatted_header:
                cols.ca = head
            elif "ght" in formatted_header:  # seen "<uom> (Hght)", "<uom> (Height)" & "Hght%"
                cols.ch = head
            else:
                logging.warning(f"Unexpected header found in page data: {head} - failed to assign")
        return cols