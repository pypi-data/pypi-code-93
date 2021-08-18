from enum import Enum
from typing import Any, Dict, List

from igi_gc_reader.reader.excel_address import ExcelAddress


class GcFileClass(Enum):
    One = 1
    Two = 2
    Unclassified = 99


class_to_expected_analysis_addr: Dict[GcFileClass, List[ExcelAddress]] = {
    GcFileClass.One: [ExcelAddress('BE1'), ExcelAddress('AM1'), ExcelAddress('AU2')],
    GcFileClass.Two: [ExcelAddress('E6')]
}

# for some file formats the main data headers start in the first couple of rows
# so just detecting a value e.g. in BE1 isn't enough to classify - we need to know
# whether it is an analysis. examples of analysis I have seen are: "WHOLE OIL GC", 
# "AROMATIC GCMS", "SATURATE GCMS", "Saturate Biomarkers", "AROMATIC BIOMARKERS",
# "Hight Temp GC" and "Extract GC".
treat_as_analysis_if_contains = ["gc", "saturate", "arom", "biom", "whole"]


def is_an_analysis(val: Any) -> bool:
    val = str(val).lower()
    return any(snippet in val for snippet in treat_as_analysis_if_contains)
