from pathlib import Path

import pandas as pd

DATA_ROOT = Path(__file__).parent.parent / "data"
NO_INFORMATION = "zzzz DUMMY ROLE WITH NO REQUIREMENTS zzzz"
FIELD_MAP = {
    # Sep 2020:
    "Appt Process": "ApptProc",
    "AAC": "ReqAAC",
    "Refs": "ReqRefs",
    "Commissioner Approval": "ReqCommissioner",
    "Committee / Council": "ReqCommitteeCouncil",
    "Transition Process": "TransProc",
    "Mod 1": "ReqMod1",
    "Trustee Intro": "ReqTrustee",
    "Mod 2": "ReqMod2",
    "Mod 3": "ReqMod3",
    "Mod 4": "ReqMod4",
    "ReqWB": "ReqWoodBadge",
    "Wood Badge": "ReqWoodBadge",
    "Sect WB": "ReqSectionWb",
    "Mgr WB": "ReqMgrWb",
    "First Aid": "ReqFirstAid",
    "Safety": "ReqSafety",
    "Safeguarding": "ReqSafeguarding",
    "GDPR": "ReqGDPR",
    "Review": "ReqReview",
    "Prereq 4 Full": "ReqPrereq4Full",
}


def merge_roles_table(data: pd.DataFrame) -> pd.DataFrame:
    # make sure we have role requirements collection set up
    roles_lookup = r2r_sep_20

    # do the merge
    data["merge_key"] = data["role"].str.lower().str.strip().str.replace(r"\s+", " ", regex=True)  # TODO check unmatched roles
    data = data.merge(roles_lookup, on="merge_key", how="left").drop("merge_key", axis=1).reset_index(drop=True)
    data["role_found"] = data["role_found"].fillna(False)
    return data


def _load_sep_2020_r2r() -> pd.DataFrame:
    r2r_sep_20_original = pd.read_csv(DATA_ROOT / "r2r_sep_20.csv", encoding="utf-8")  # September 2020 R2R table from CA
    translation_sep_20 = pd.read_csv(DATA_ROOT / "translation_sep_20.csv", encoding="utf-8")  # Roles translation table

    # Construct 'full' September 2020 Roles to Requirements table
    # September 2020 R2R table merged with translation table
    r2r_table = pd.concat([
        r2r_sep_20_original.drop_duplicates(subset="Role"),
        translation_sep_20
            .fillna(NO_INFORMATION)
            .drop_duplicates()
            .merge(r2r_sep_20_original.drop_duplicates(subset=["Role"]), how="left", left_on="Table 2 Role", right_on="Role")
            .drop(["Table 2 Role", "Role"], axis=1)
            .rename(columns={"Compass Role": "Role"}, copy=False)
    ]).drop_duplicates(subset="Role")

    r2r_table = _setup_for_merge(r2r_table).drop(columns=["Disclosure Req", "Membership"])
    return r2r_table.rename(columns=FIELD_MAP, copy=False)


def _setup_for_merge(r2r_table: pd.DataFrame) -> pd.DataFrame:
    r2r_table = _fix_r2r_data_types(r2r_table)

    r2r_table["role_found"] = True
    r2r_table = r2r_table.drop_duplicates(subset="Role")

    # case-insensitive merging
    r2r_table["merge_key"] = r2r_table["Role"].str.lower()
    r2r_table = r2r_table.drop("Role", axis=1)

    return r2r_table


def _fix_r2r_data_types(r2r_table: pd.DataFrame) -> pd.DataFrame:
    # Fix data types
    for col in r2r_table.columns:
        # fields to skip
        if col in {"Role", "DELMGRGOVSUP", "Membership"}:
            continue
        if col in {"Appt Process", "Transition Process"}:
            r2r_table[col] = r2r_table[col].astype("UInt8")
        else:
            r2r_table[col] = r2r_table[col].astype("boolean")
    return r2r_table


r2r_sep_20 = _load_sep_2020_r2r()
