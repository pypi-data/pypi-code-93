import tempfile
import zipfile
from pathlib import Path

import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.csv as pcsv

from .types import FilenameType

GEO_FIELDS = {
    "FILEID": pa.string(),
    "STUSAB": pa.string(),
    "SUMLEV": pa.string(),
    "GEOVAR": pa.string(),
    "GEOCOMP": pa.string(),
    "CHARITER": pa.string(),
    "CIFSN": pa.string(),
    "LOGRECNO": pa.int64(),
    "GEOID": pa.string(),
    "GEOCODE": pa.string(),
    "REGION": pa.string(),
    "DIVISION": pa.string(),
    "STATE": pa.string(),
    "STATENS": pa.string(),
    "COUNTY": pa.string(),
    "COUNTYCC": pa.string(),
    "COUNTYNS": pa.string(),
    "COUSUB": pa.string(),
    "COUSUBCC": pa.string(),
    "COUSUBNS": pa.string(),
    "SUBMCD": pa.string(),
    "SUBMCDCC": pa.string(),
    "SUBMCDNS": pa.string(),
    "ESTATE": pa.string(),
    "ESTATECC": pa.string(),
    "ESTATENS": pa.string(),
    "CONCIT": pa.string(),
    "CONCITCC": pa.string(),
    "CONCITNS": pa.string(),
    "PLACE": pa.string(),
    "PLACECC": pa.string(),
    "PLACENS": pa.string(),
    "TRACT": pa.string(),
    "BLKGRP": pa.string(),
    "BLOCK": pa.string(),
    "AIANHH": pa.string(),
    "AIHHTLI": pa.string(),
    "AIANHHFP": pa.string(),
    "AIANHHCC": pa.string(),
    "AIANHHNS": pa.string(),
    "AITS": pa.string(),
    "AITSFP": pa.string(),
    "AITSCC": pa.string(),
    "AITSNS": pa.string(),
    "TTRACT": pa.string(),
    "TBLKGRP": pa.string(),
    "ANRC": pa.string(),
    "ANRCCC": pa.string(),
    "ANRCNS": pa.string(),
    "CBSA": pa.string(),
    "MEMI": pa.string(),
    "CSA": pa.string(),
    "METDIV": pa.string(),
    "NECTA": pa.string(),
    "NMEMI": pa.string(),
    "CNECTA": pa.string(),
    "NECTADIV": pa.string(),
    "CBSAPCI": pa.string(),
    "NECTAPCI": pa.string(),
    "UA": pa.string(),
    "UATYPE": pa.string(),
    "UR": pa.string(),
    "CD116": pa.string(),
    "CD118": pa.string(),
    "CD119": pa.string(),
    "CD120": pa.string(),
    "CD121": pa.string(),
    "SLDU18": pa.string(),
    "SLDU22": pa.string(),
    "SLDU24": pa.string(),
    "SLDU26": pa.string(),
    "SLDU28": pa.string(),
    "SLDL18": pa.string(),
    "SLDL22": pa.string(),
    "SLDL24": pa.string(),
    "SLDL26": pa.string(),
    "SLDL28": pa.string(),
    "VTD": pa.string(),
    "VTDI": pa.string(),
    "ZCTA": pa.string(),
    "SDELM": pa.string(),
    "SDSEC": pa.string(),
    "SDUNI": pa.string(),
    "PUMA": pa.string(),
    "AREALAND": pa.int64(),
    "AREAWATR": pa.int64(),
    "BASENAME": pa.string(),
    "NAME": pa.string(),
    "FUNCSTAT": pa.string(),
    "GCUNI": pa.string(),
    "POP100": pa.int64(),
    "HU100": pa.int64(),
    "INTPTLAT": pa.string(),
    "INTPTLON": pa.string(),
    "LSADC": pa.string(),
    "PARTFLAG": pa.string(),
    "UGA": pa.string(),
}

PART1_FIELDS = {
    "FILEID": pa.string(),
    "STUSAB": pa.string(),
    "CHARITER": pa.string(),
    "CIFSN": pa.string(),
    "LOGRECNO": pa.int64(),
    **{f"P00{i}": pa.int64() for i in range(10001, 10072)},
    **{f"P00{i}": pa.int64() for i in range(20001, 20074)},
}


PART2_FIELDS = {
    "FILEID": pa.string(),
    "STUSAB": pa.string(),
    "CHARITER": pa.string(),
    "CIFSN": pa.string(),
    "LOGRECNO": pa.int64(),
    **{f"P00{i}": pa.int64() for i in range(30001, 30072)},
    **{f"P00{i}": pa.int64() for i in range(40001, 40074)},
    **{f"H00{i}": pa.int64() for i in range(10001, 10004)},
}

PART3_FIELDS = {
    "FILEID": pa.string(),
    "STUSAB": pa.string(),
    "CHARITER": pa.string(),
    "CIFSN": pa.string(),
    "LOGRECNO": pa.int64(),
    **{f"P00{i}": pa.int64() for i in range(50001, 50011)},
}


def parse_census_part1(filename: FilenameType) -> pa.Table:
    """
    Parse a Part 1 table from the Census Bureau

    Args:
        filename: The file (should end in 12020.pl)

    Returns:
        A pyarrow Table version of the data
    """
    return pcsv.read_csv(
        filename,
        read_options=pa.csv.ReadOptions(
            column_names=list(PART1_FIELDS), encoding="latin1"
        ),
        parse_options=pcsv.ParseOptions(delimiter="|"),
        convert_options=pcsv.ConvertOptions(column_types=PART1_FIELDS),
    )


def parse_census_part2(filename: FilenameType) -> pa.Table:
    """
    Parse a Part 2 table from the Census Bureau

    Args:
        filename: The file (should end in 22020.pl)

    Returns:
        A pyarrow Table version of the data
    """
    return pcsv.read_csv(
        filename,
        read_options=pa.csv.ReadOptions(
            column_names=list(PART2_FIELDS), encoding="latin1"
        ),
        parse_options=pcsv.ParseOptions(delimiter="|"),
        convert_options=pcsv.ConvertOptions(column_types=PART2_FIELDS),
    )


def parse_census_part3(filename: FilenameType) -> pa.Table:
    """
    Parse a Part 3 table from the Census Bureau

    Args:
        filename: The file (should end in 32020.pl)

    Returns:
        A pyarrow Table version of the data
    """
    return pcsv.read_csv(
        filename,
        read_options=pa.csv.ReadOptions(
            column_names=list(PART3_FIELDS), encoding="latin1"
        ),
        parse_options=pcsv.ParseOptions(delimiter="|"),
        convert_options=pcsv.ConvertOptions(column_types=PART3_FIELDS),
    )


def parse_census_geo(filename: FilenameType) -> pa.Table:
    """
    Parse a geo table from the Census Bureau

    Args:
        filename: The file (should end in geo2020.pl)

    Returns:
        A pyarrow Table version of the data
    """
    return pcsv.read_csv(
        filename,
        read_options=pa.csv.ReadOptions(
            column_names=list(GEO_FIELDS), encoding="latin1"
        ),
        parse_options=pcsv.ParseOptions(delimiter="|"),
        convert_options=pcsv.ConvertOptions(column_types=GEO_FIELDS),
    )


def parse_all(filename: FilenameType) -> pa.Table:
    """
    From a ZIP file of PL94 data, parse all subtables into a single table

    Args:
        filename: The file (should end in .pl.zip)

    Returns:
        A pyarrow Table version of the data
    """
    with tempfile.TemporaryDirectory() as tmp:
        tmpdir = Path(tmp)
        with zipfile.ZipFile(filename, "r") as zfile:
            zfile.extractall(tmpdir)

        table1 = parse_census_part1(list(tmpdir.rglob("*12020.pl"))[0])
        table2 = parse_census_part2(list(tmpdir.rglob("*22020.pl"))[0])
        table3 = parse_census_part3(list(tmpdir.rglob("*32020.pl"))[0])
        tablegeo = parse_census_geo(list(tmpdir.rglob("*geo2020.pl"))[0])

    return combine_tables(table1, table2, table3, tablegeo)


def combine_tables(
    table1: pa.Table, table2: pa.Table, table3: pa.Table, tablegeo: pa.Table
) -> pa.Table:
    """
    Combine all four Census tables into a single table
    """
    # Verify everything is sorted
    table1 = table1.take(pc.sort_indices(table1["LOGRECNO"]))
    table2 = table2.take(pc.sort_indices(table2["LOGRECNO"]))
    table3 = table3.take(pc.sort_indices(table3["LOGRECNO"]))
    tablegeo = tablegeo.take(pc.sort_indices(tablegeo["LOGRECNO"]))

    # Remove common columns
    table1 = table1.drop(["LOGRECNO", "STUSAB", "FILEID", "CHARITER", "CIFSN"])
    table2 = table2.drop(["LOGRECNO", "STUSAB", "FILEID", "CHARITER", "CIFSN"])
    table3 = table3.drop(["LOGRECNO", "STUSAB", "FILEID", "CHARITER", "CIFSN"])

    # Create final schema
    final_schema = tablegeo.schema
    for field in table1.schema:
        final_schema = final_schema.append(field)
    for field in table2.schema:
        final_schema = final_schema.append(field)
    for field in table3.schema:
        final_schema = final_schema.append(field)

    # Create final table
    final_table = pa.Table.from_arrays(
        [*tablegeo.columns, *table1.columns, *table2.columns, *table3.columns],
        schema=final_schema,
    )

    return final_table
