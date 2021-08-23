from __future__ import annotations

from typing import TYPE_CHECKING

import pandas as pd

from assistants.compliance.util.input_data_utility import completed_to_due_vector
from assistants.compliance.util.input_data_utility import date_end_sept_2021

if TYPE_CHECKING:
    import datetime

date_transition = pd.Timestamp(2020, 9, 15)


def calculate_compliance(data: pd.DataFrame, report_date: datetime.date) -> pd.DataFrame:
    """Calculate the values used in the Appointments sheet

    Unintentionally, everything in this function is in-place except for the by-adult values.
    """

    run_date = pd.Timestamp(report_date)
    data = _post_sep_20(data, run_date)
    data = _misc_stats(data)
    data = _by_adult(data, ["Mod1", "Trustee", "FirstAid", "Safety", "Safeguarding", "GDPR"])

    return data


def _post_sep_20(data: pd.DataFrame, run_date: pd.Timestamp) -> pd.DataFrame:
    run_date_plus_1_month = run_date + pd.DateOffset(months=1)                                  # +  1M
    run_date_plus_5_months = run_date + pd.DateOffset(months=5)                                 # +  5M

    # Transition processes
    trans_process_1 = data["TransProc"] == 1

    trans_3_start_pre_transition = (data["TransProc"] == 3) & (data["role_start_date"] < date_transition)
    trans_1_or_start_post_transition = trans_process_1 | (data["role_start_date"] >= date_transition)

    # Role starts
    role_start_plus_5_months = data["role_start_date"] + pd.DateOffset(months=5)
    role_start_plus_3_years = data["role_start_date"] + pd.DateOffset(years=3)  # NoQA
    role_start_plus_5_years = data["role_start_date"] + pd.DateOffset(years=5)  # NoQA

    # Due by vectors
    intro_training_due = role_start_plus_5_months.copy()
    intro_training_due[trans_3_start_pre_transition] = date_end_sept_2021

    trustee_due = role_start_plus_5_months.copy()
    trustee_due[data["mod_01"] < date_transition] = date_end_sept_2021

    first_aid_due = data["first_aid_renewal"].fillna(role_start_plus_3_years)
    first_aid_plus_3_years = data["first_aid"] + pd.DateOffset(years=3)  # NoQA
    # Clip First Aid due by date to 3 years max
    first_aid_due[first_aid_due > first_aid_plus_3_years] = first_aid_plus_3_years

    # Review date is the date of the *next* review, and should be in the future
    review_due = data["review_date"].fillna(role_start_plus_5_years)

    blank_safety = data["safety"].isna()
    safety_due = completed_to_due_vector(data["safety"], trans_process_1)
    safety_due[blank_safety & trans_1_or_start_post_transition] = role_start_plus_5_months
    safety_due[blank_safety & ~trans_1_or_start_post_transition] = date_end_sept_2021

    blank_safeguarding = data["safeguarding"].isna()
    safeguarding_due = completed_to_due_vector(data["safeguarding"], trans_process_1)
    safeguarding_due[blank_safeguarding & trans_1_or_start_post_transition] = role_start_plus_5_months
    safeguarding_due[blank_safeguarding & ~trans_1_or_start_post_transition] = date_end_sept_2021

    data["DueBySafety"] = safety_due
    data["DueBySafeguarding"] = safeguarding_due

    # Role Requirements
    req_aac = data["ReqAAC"]
    req_refs = data["ReqRefs"]
    req_commissioner = data["ReqCommissioner"]
    req_committee = data["ReqCommitteeCouncil"]
    req_mod_1 = data["ReqMod1"]
    req_trustee = data["ReqTrustee"]
    req_mod_2 = data["ReqMod2"]
    req_mod_3 = data["ReqMod3"]
    req_mod_4 = data["ReqMod4"]
    req_wood_badge = data["ReqWoodBadge"]
    req_section_wb = data["ReqSectionWb"]
    req_manager_wb = data["ReqMgrWb"]
    req_first_aid = data["ReqFirstAid"]
    req_safety = data["ReqSafety"]
    req_safeguarding = data["ReqSafeguarding"]
    req_gdpr = data["ReqGDPR"]
    req_review = data["ReqReview"]
    req_prereq_for_full = data["ReqPrereq4Full"]

    # Completed (validated == has at any point been validated, i.e. not blank)
    role_full = data["role_status"] == "Full"
    role_not_pre_prov = data["role_status"].isin({"Full", "Provisional"})
    validated_full_role = role_full & req_prereq_for_full
    validated_mod_1_or_1_ex = data["mod_01"].notna() | data["mod_01_ex"].notna()
    validated_mod_2 = data["mod_02"].notna()
    validated_mod_3 = data["mod_03"].notna()
    validated_mod_4 = data["mod_04"].notna()
    validated_wb = data["wood_badge"].notna()
    validated_gdpr = data["gdpr"].notna()

    # Overdue / Due Soon
    intro_training_overdue = intro_training_due <= run_date
    intro_training_due_soon = intro_training_due <= run_date_plus_1_month

    data.loc[role_full, "TypePreprov"] = "valid"
    data.loc[~role_full & intro_training_overdue, "TypePreprov"] = "overdue"
    data.loc[~role_full & ~intro_training_overdue & intro_training_due_soon, "TypePreprov"] = "soon"
    data.loc[~role_full & ~intro_training_overdue & ~intro_training_due_soon, "TypePreprov"] = "start"  # grace period after role start

    _completed_aac = (data["approval_panel"] == "Satisfactory") | role_not_pre_prov
    data.loc[req_aac & _completed_aac, "TypeAAC"] = "valid"
    data.loc[req_aac & ~_completed_aac & intro_training_overdue, "TypeAAC"] = "overdue"
    data.loc[req_aac & ~_completed_aac & ~intro_training_overdue & intro_training_due_soon, "TypeAAC"] = "soon"
    data.loc[req_aac & ~_completed_aac & ~intro_training_due_soon, "TypeAAC"] = "start"  # grace period after role start

    _completed_refs = (data["references"] == "Satisfactory") | role_not_pre_prov
    data.loc[req_refs & _completed_refs, "TypeRefs"] = "valid"
    data.loc[req_refs & ~_completed_refs & intro_training_overdue, "TypeRefs"] = "overdue"
    data.loc[req_refs & ~_completed_refs & ~intro_training_overdue & intro_training_due_soon, "TypeRefs"] = "soon"
    data.loc[req_refs & ~_completed_refs & ~intro_training_due_soon, "TypeRefs"] = "start"  # grace period after role start

    _completed_commissioner = (data["approval_commissioner"] == "Satisfactory") | role_not_pre_prov
    data.loc[req_commissioner & _completed_commissioner, "TypeCommissioner"] = "valid"
    data.loc[req_commissioner & ~_completed_commissioner & intro_training_overdue, "TypeCommissioner"] = "overdue"
    data.loc[req_commissioner & ~_completed_commissioner & ~intro_training_overdue & intro_training_due_soon, "TypeCommissioner"] = "soon"
    data.loc[req_commissioner & ~_completed_commissioner & ~intro_training_due_soon, "TypeCommissioner"] = "start"  # grace period after role start

    _completed_committee = (data["approval_committee"] == "Satisfactory") | role_not_pre_prov
    data.loc[req_committee & _completed_committee, "TypeCommittee"] = "valid"
    data.loc[req_committee & ~_completed_committee & intro_training_overdue, "TypeCommittee"] = "overdue"
    data.loc[req_committee & ~_completed_committee & ~intro_training_overdue & intro_training_due_soon, "TypeCommittee"] = "soon"
    data.loc[req_committee & ~_completed_committee & ~intro_training_due_soon, "TypeCommittee"] = "start"  # grace period after role start

    _completed_mod_1 = validated_mod_1_or_1_ex | validated_full_role
    data.loc[req_mod_1 & _completed_mod_1, "TypeMod1"] = "valid"
    data.loc[req_mod_1 & ~_completed_mod_1 & intro_training_overdue, "TypeMod1"] = "overdue"
    data.loc[req_mod_1 & ~_completed_mod_1 & ~intro_training_overdue & intro_training_due_soon, "TypeMod1"] = "soon"
    data.loc[req_mod_1 & ~_completed_mod_1 & ~intro_training_due_soon, "TypeMod1"] = "start"  # grace period after role start

    _completed_mod_2 = validated_mod_2 | validated_full_role
    data.loc[req_mod_2 & _completed_mod_2, "TypeMod2"] = "valid"
    data.loc[req_mod_2 & ~_completed_mod_2 & intro_training_overdue, "TypeMod2"] = "overdue"
    data.loc[req_mod_2 & ~_completed_mod_2 & ~intro_training_overdue & intro_training_due_soon, "TypeMod2"] = "soon"
    data.loc[req_mod_2 & ~_completed_mod_2 & ~intro_training_due_soon, "TypeMod2"] = "start"  # grace period after role start

    _completed_mod_3 = validated_mod_3 | validated_full_role
    data.loc[req_mod_3 & _completed_mod_3, "TypeMod3"] = "valid"
    data.loc[req_mod_3 & ~_completed_mod_3 & intro_training_overdue, "TypeMod3"] = "overdue"
    data.loc[req_mod_3 & ~_completed_mod_3 & ~intro_training_overdue & intro_training_due_soon, "TypeMod3"] = "soon"
    data.loc[req_mod_3 & ~_completed_mod_3 & ~intro_training_due_soon, "TypeMod3"] = "start"  # grace period after role start

    _completed_mod_4 = validated_mod_4 | validated_full_role
    data.loc[req_mod_4 & _completed_mod_4, "TypeMod4"] = "valid"
    data.loc[req_mod_4 & ~_completed_mod_4 & intro_training_overdue, "TypeMod4"] = "overdue"
    data.loc[req_mod_4 & ~_completed_mod_4 & ~intro_training_overdue & intro_training_due_soon, "TypeMod4"] = "soon"
    data.loc[req_mod_4 & ~_completed_mod_4 & ~intro_training_due_soon, "TypeMod4"] = "start"  # grace period after role start

    _completed_trustee = data["mod_01_ex"].notna() | data["trustee_intro"].notna()
    data.loc[req_trustee & _completed_trustee, "TypeTrustee"] = "valid"
    data.loc[req_trustee & ~_completed_trustee & (trustee_due <= run_date), "TypeTrustee"] = "overdue"
    data.loc[req_trustee & ~_completed_trustee & (trustee_due > run_date) & (trustee_due <= run_date_plus_1_month), "TypeTrustee"] = "soon"
    data.loc[req_trustee & ~_completed_trustee & (trustee_due > run_date_plus_1_month), "TypeTrustee"] = "start"  # grace period after role start

    data.loc[req_gdpr & validated_gdpr, "TypeGDPR"] = "valid"
    data.loc[req_gdpr & ~validated_gdpr & intro_training_overdue, "TypeGDPR"] = "overdue"
    data.loc[req_gdpr & ~validated_gdpr & ~intro_training_overdue & intro_training_due_soon, "TypeGDPR"] = "soon"
    data.loc[req_gdpr & ~validated_gdpr & ~intro_training_due_soon, "TypeGDPR"] = "start"  # grace period after role start

    data.loc[req_wood_badge & validated_wb, "TypeWoodBadge"] = "valid"
    data.loc[req_wood_badge & ~validated_wb & (role_start_plus_3_years <= run_date), "TypeWoodBadge"] = "overdue"  # three years to do a wood badge
    data.loc[req_wood_badge & ~validated_wb & (role_start_plus_3_years > run_date) & (role_start_plus_3_years <= run_date_plus_5_months), "TypeWoodBadge"] = "soon"
    data.loc[req_wood_badge & ~validated_wb & (role_start_plus_3_years > run_date_plus_5_months), "TypeWoodBadge"] = "start"  # grace period after role start

    data.loc[req_section_wb & (data["TypeWoodBadge"] == "valid"), "TypeSectionWb"] = "valid"
    data.loc[req_section_wb & (data["TypeWoodBadge"] == "overdue"), "TypeSectionWb"] = "overdue"
    data.loc[req_section_wb & (data["TypeWoodBadge"] == "soon"), "TypeSectionWb"] = "soon"
    data.loc[req_section_wb & (data["TypeWoodBadge"] == "start"), "TypeSectionWb"] = "start"  # grace period after role start

    data.loc[req_manager_wb & (data["TypeWoodBadge"] == "valid"), "TypeMgrWb"] = "valid"
    data.loc[req_manager_wb & (data["TypeWoodBadge"] == "overdue"), "TypeMgrWb"] = "overdue"
    data.loc[req_manager_wb & (data["TypeWoodBadge"] == "soon"), "TypeMgrWb"] = "soon"
    data.loc[req_manager_wb & (data["TypeWoodBadge"] == "start"), "TypeMgrWb"] = "start"  # grace period after role start

    data.loc[req_first_aid & (first_aid_due > run_date_plus_5_months), "TypeFirstAid"] = "valid"  # all not overdue or due soon
    data.loc[req_first_aid & (first_aid_due <= run_date), "TypeFirstAid"] = "overdue"
    data.loc[req_first_aid & (first_aid_due > run_date) & (first_aid_due <= run_date_plus_5_months), "TypeFirstAid"] = "soon"

    # SFTY/SAFE must be required, not valid (out of date or blank), have started more than five months ago
    data.loc[req_safety & (safety_due > run_date_plus_5_months), "TypeSafety"] = "valid"  # all not overdue or due soon
    data.loc[req_safety & (safety_due <= run_date), "TypeSafety"] = "overdue"
    data.loc[req_safety & (safety_due > run_date) & (safety_due <= run_date_plus_5_months), "TypeSafety"] = "soon"

    data.loc[req_safeguarding & (safeguarding_due > run_date_plus_5_months), "TypeSafeguarding"] = "valid"  # all not overdue or due soon
    data.loc[req_safeguarding & (safeguarding_due <= run_date), "TypeSafeguarding"] = "overdue"
    data.loc[req_safeguarding & (safeguarding_due > run_date) & (safeguarding_due <= run_date_plus_5_months), "TypeSafeguarding"] = "soon"

    # TODO can we actually say this for comp review? as e.g. review may be 3 years not 5, etc.
    data.loc[req_review & (review_due > run_date_plus_5_months) & (role_start_plus_5_years <= run_date), "TypeReview"] = "valid"  # all not overdue or due soon
    data.loc[req_review & (review_due <= run_date), "TypeReview"] = "overdue"
    data.loc[req_review & (review_due > run_date) & (review_due <= run_date_plus_5_months), "TypeReview"] = "soon"
    data.loc[req_review & (review_due > run_date_plus_5_months) & (role_start_plus_5_years > run_date), "TypeReview"] = "start"  # grace period after role start

    # fill NA values
    types = ['Preprov', 'AAC', 'Refs', 'Commissioner', 'Committee', 'Mod1', 'Mod2', 'Mod3', 'Mod4', 'Trustee', 'WoodBadge', 'SectionWb', 'MgrWb', 'FirstAid', 'Safety', 'Safeguarding', 'Review', 'GDPR']
    type_cols = [f"Type{t}" for t in types]
    data[type_cols] = data[type_cols].fillna("not_req")

    # remove requirements / due by columns
    data = data.drop(columns=[col for col in data.columns if col.startswith("Req")] + ["ApptProc", "TransProc"])

    return data


def _misc_stats(data: pd.DataFrame) -> pd.DataFrame:
    """Misc Stats"""
    # fmt: off
    types = (
        'Preprov', 'AAC', 'Refs', 'Commissioner', 'Committee', 'Mod1', 'Mod2', 'Mod3', 'Mod4', 'Trustee',
        'WoodBadge', 'SectionWb', 'MgrWb', 'FirstAid', 'Safety', 'Safeguarding', 'Review', 'GDPR'
    )
    # fmt: on
    type_cols = [f"Type{t}" for t in types]

    data["QAny"] = data[type_cols].isin({"overdue", "soon"}).any(axis=1) | (data["role_found"] == False)
    data["RoleCount"] = 1
    data["Overdue"] = (data[type_cols] == "overdue").any(axis=1)
    data["DueSoon"] = (data[type_cols] == "soon").any(axis=1)

    return data


def _by_adult(data: pd.DataFrame, by_adult_compliance: list[str]) -> pd.DataFrame:
    """By Adult"""
    member_index = data.reset_index().groupby("membership_number")["index"].first().to_frame()
    data["AdultCount"] = 0
    data.loc[member_index["index"], "AdultCount"] = 1

    types_fields = data.set_index("membership_number")[[f"Type{t}" for t in by_adult_compliance]]

    # order important!
    # not_req is overridden by any other value (as that implies required)
    # start is overridden by any valid/overdue status (as start grace period only applies once per member)
    # valid is overridden by soon and overdue (to stop things looking better than reality)
    # soon is overridden by overdue (as overdue is actually invalid compliance)
    for status in ("not_req", "start", "valid", "soon", "overdue"):
        match_status = (types_fields == status).groupby("membership_number").any()
        for col in by_adult_compliance:
            member_index.loc[match_status[f"Type{col}"], f"ByAdult{col}"] = status
    data = data.merge(member_index.set_index("index"), left_index=True, right_index=True, how="left")

    by_adult_types = [f"ByAdult{t}" for t in by_adult_compliance]
    assert data.loc[member_index["index"], by_adult_types].isna().sum().sum() == 0
    data[by_adult_types] = data[by_adult_types].fillna("not_primary_role")

    return data
