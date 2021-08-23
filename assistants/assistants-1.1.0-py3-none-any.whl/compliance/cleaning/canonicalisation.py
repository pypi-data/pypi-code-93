from __future__ import annotations

from typing import TYPE_CHECKING

from assistants.compliance.util import fields

if TYPE_CHECKING:
    from collections.abc import Iterable

_headings_region_post_sep_2020 = {
    "Membership_Number": fields.MEMBERSHIP_NUMBER,

    "Forenames": fields.FORENAMES,
    "Surname": fields.SURNAME,
    "Known_As": fields.KNOWN_AS,

    "Email": fields.EMAIL,

    "Address": fields.ADDRESS,
    "Postcode": fields.POSTCODE,
    "Phone_number": fields.PHONE_NUMBER,

    "Role": fields.ROLE,
    "Role_Start_Date": fields.ROLE_START_DATE,
    "Role_End_Date": fields.ROLE_END_DATE,

    "CE_Check": fields.CE_CHECK,
    "Commissioner_Approval": fields.APPROVAL_COMMISSIONER,
    "Committee_Approval": fields.APPROVAL_COMMITTEE,
    "References": fields.REFERENCES,

    "RoleStatus": fields.ROLE_STATUS,
    "Line_manager_number": fields.LINE_MANAGER_NUMBER,
    "LineManager": fields.LINE_MANAGER_NAME,
    "review_date": fields.REVIEW_DATE,

    "Region": fields.REGION,
    "County": fields.COUNTY,
    "County_Section": fields.COUNTY_SECTION,
    "District": fields.DISTRICT,
    "District_Section": fields.DISTRICT_SECTION,
    "ScoutGroup": fields.SCOUT_GROUP,
    "scout_group_section": fields.SCOUT_GROUP_SECTION,

    "AppAdvComm_Approval": fields.APPROVAL_PANEL,

    "Essential_Info": fields.MOD_01,
    "PersonalLearningPlan": fields.MOD_02,
    # if we got gdpr then new format, so headings change
    "Tools_for_Role_Section_Leaders": fields.MOD_03,
    "Tools4Role": fields.MOD_04,

    "Essential_Info_Exec1": fields.MOD_01_EX,
    "Trustee_Introduction": fields.TRUSTEE_INTRO,

    "GDPR1": fields.GDPR,

    "WoodBadgeReceived": fields.WOOD_BADGE,

    "OngoingSafetyTraining": fields.SAFETY,
    "MOGL_Safety_renewal": fields.SAFETY_RENEWAL,

    "OngoingSafeguardingTraining": fields.SAFEGUARDING,
    "MOGL_Safeguarding_renewal": fields.SAFEGUARDING_RENEWAL,

    "FirstAidTraining": fields.FIRST_AID,
    "MOGL_First_Aid_renewal": fields.FIRST_AID_RENEWAL,

    "OngoingLearningHours": fields.ONGOING_LEARNING_HOURS,
}

_headings_region_post_nov_2020 = {
    "Membership_Number": fields.MEMBERSHIP_NUMBER,

    "Forenames": fields.FORENAMES,
    "Surname": fields.SURNAME,
    "Known_As": fields.KNOWN_AS,

    "Email": fields.EMAIL,

    "Address": fields.ADDRESS,
    "Postcode": fields.POSTCODE,
    "Telephone": fields.PHONE_NUMBER,

    "Role": fields.ROLE,
    "Role_Start_Date": fields.ROLE_START_DATE,
    "Role_End_Date": fields.ROLE_END_DATE,

    "CE_Check": fields.CE_CHECK,
    "Commissioner_Approval": fields.APPROVAL_COMMISSIONER,
    "Committee_Approval": fields.APPROVAL_COMMITTEE,
    "References": fields.REFERENCES,

    "Role_Status": fields.ROLE_STATUS,
    "Line_Manager_Membership_Number": fields.LINE_MANAGER_NUMBER,
    "Line_Manager_Name": fields.LINE_MANAGER_NAME,
    "Appointment_Review_Date": fields.REVIEW_DATE,

    "Role_Country": fields.COUNTRY,
    "Role_Region": fields.REGION,
    "Role_County": fields.COUNTY,
    "Role_County_Section": fields.COUNTY_SECTION,
    "Role_District": fields.DISTRICT,
    "Role_District_Section": fields.DISTRICT_SECTION,
    "Role_Scout_Group": fields.SCOUT_GROUP,
    "Role_Scout_Group_Section": fields.SCOUT_GROUP_SECTION,

    "Appointments_Advisory_Commitee_Approval": fields.APPROVAL_PANEL,

    "Getting_Started_Essential_Info": fields.MOD_01,
    "Getting_Started_Personal_Learning_Plan": fields.MOD_02,
    "Getting_Started_Tools_for_the_Role_Section_Leaders": fields.MOD_03,
    "Getting_Started_Tools_for_the_Role_Managers_and_Supporters": fields.MOD_04,

    "Getting_Started_Essential_Info_M1EX": fields.MOD_01_EX,
    "Getting_Started_Trustee_Introduction": fields.TRUSTEE_INTRO,

    "Getting_Started_GDPR": fields.GDPR,

    "Wood_Badge": fields.WOOD_BADGE,

    "MOGL_Safety_completed_date": fields.SAFETY,
    "MOGL_Safety_renewal_date": fields.SAFETY_RENEWAL,

    "MOGL_Safeguarding_completed_date": fields.SAFEGUARDING,
    "MOGL_Safeguarding_renewal_date": fields.SAFEGUARDING_RENEWAL,

    "MOGL_First_Aid_completed_date": fields.FIRST_AID,
    "MOGL_First_Aid_renewal_date": fields.FIRST_AID_RENEWAL,

    "Ongoing_Learning_Hours": fields.ONGOING_LEARNING_HOURS,
}


_headings_district_post_nov_2020 = {
    "Membership_Number": fields.MEMBERSHIP_NUMBER,

    "forenames": fields.FORENAMES,
    "surname": fields.SURNAME,
    "Known_As": fields.KNOWN_AS,

    "Email": fields.EMAIL,

    "Address": fields.ADDRESS,
    "Postcode": fields.POSTCODE,
    "Telephone": fields.PHONE_NUMBER,

    "Role": fields.ROLE,
    "Role_Start_Date": fields.ROLE_START_DATE,
    "Role_End_Date": fields.ROLE_END_DATE,

    "CE_Check": fields.CE_CHECK,
    "Commissioner_Approval": fields.APPROVAL_COMMISSIONER,
    "Committee_Approval": fields.APPROVAL_COMMITTEE,
    "Reference": fields.REFERENCES,

    "Role_Status": fields.ROLE_STATUS,
    "Line_Manager_Membership_Number": fields.LINE_MANAGER_NUMBER,
    "Line_Manager_Name": fields.LINE_MANAGER_NAME,
    "Appointment_Review_Date": fields.REVIEW_DATE,

    "Role_Country": fields.COUNTRY,
    "Role_Region": fields.REGION,
    "Role_County": fields.COUNTY,
    "Role_District": fields.DISTRICT,
    "Role_District_Section": fields.DISTRICT_SECTION,
    "Role_Scout_Group": fields.SCOUT_GROUP,
    "Role_Scout_Group_Section": fields.SCOUT_GROUP_SECTION,

    "Appointments_Advisory_Commitee_Approval": fields.APPROVAL_PANEL,

    "Getting_Started_Essential_Info": fields.MOD_01,
    "Getting_Started_Personal_Learning_Plan": fields.MOD_02,
    "Getting_Started_Tools_for_the_Role_Section_Leaders": fields.MOD_03,
    "Getting_Started_Tools_for_the_Role_Managers_and_Supporters": fields.MOD_04,

    "Getting_Started_Essential_Info_M1EX": fields.MOD_01_EX,
    "Getting_Started_Trustee_Introduction": fields.TRUSTEE_INTRO,

    "Getting_Started_GDPR": fields.GDPR,

    "Wood_Badge": fields.WOOD_BADGE,

    "MOGL_Safety_completed_date": fields.SAFETY,
    "MOGL_Safety_renewal_date": fields.SAFETY_RENEWAL,

    "MOGL_Safeguarding_completed_date": fields.SAFEGUARDING,
    "MOGL_Safeguarding_renewal_date": fields.SAFEGUARDING_RENEWAL,

    "MOGL_First_Aid_completed_date": fields.FIRST_AID,
    "MOGL_First_Aid_renewal_date": fields.FIRST_AID_RENEWAL,

    "Ongoing_Learning_Hours": fields.ONGOING_LEARNING_HOURS,
}

_headings_county_post_nov_2020 = {
    "Membership_Number": fields.MEMBERSHIP_NUMBER,

    "Forenames": fields.FORENAMES,
    "Surname": fields.SURNAME,
    "Known_As": fields.KNOWN_AS,

    "Email": fields.EMAIL,

    "Address": fields.ADDRESS,
    "Postcode": fields.POSTCODE,
    "Telephone": fields.PHONE_NUMBER,

    "Role": fields.ROLE,
    "Role_Start_Date": fields.ROLE_START_DATE,
    "Role_End_Date": fields.ROLE_END_DATE,

    "CE_Check": fields.CE_CHECK,
    "Commissioner_Approval": fields.APPROVAL_COMMISSIONER,
    "Committee_Approval": fields.APPROVAL_COMMITTEE,
    "References": fields.REFERENCES,

    "Role_Status": fields.ROLE_STATUS,
    "Line_Manager_Membership_Number": fields.LINE_MANAGER_NUMBER,
    "Line_Manager_Name": fields.LINE_MANAGER_NAME,
    "Appointment_Review_Date": fields.REVIEW_DATE,

    "Role_Country": fields.COUNTRY,
    "Role_Region": fields.REGION,
    "Role_County": fields.COUNTY,
    "county_section": fields.COUNTY_SECTION,
    "Role_District": fields.DISTRICT,
    "Role_District_Section": fields.DISTRICT_SECTION,
    "Role_Scout_Group": fields.SCOUT_GROUP,
    "Role_Scout_Group_Section": fields.SCOUT_GROUP_SECTION,

    "Appointments_Advisory_Commitee_Approval": fields.APPROVAL_PANEL,

    "Getting_Started_Essential_Info": fields.MOD_01,
    "Getting_Started_Personal_Learning_Plan": fields.MOD_02,
    "Getting_Started_Tools_for_the_Role_Section_Leaders": fields.MOD_03,
    "Getting_Started_Tools_for_the_Role_Managers_and_Supporters": fields.MOD_04,

    "Getting_Started_Essential_Info_M1EX": fields.MOD_01_EX,
    "Getting_Started_Trustee_Introduction": fields.TRUSTEE_INTRO,

    "Getting_Started_GDPR": fields.GDPR,

    "Wood_Badge": fields.WOOD_BADGE,

    "MOGL_Safety_completed_date": fields.SAFETY,
    "MOGL_Safety_renewal_date": fields.SAFETY_RENEWAL,

    "MOGL_Safeguarding_completed_date": fields.SAFEGUARDING,
    "MOGL_Safeguarding_renewal_date": fields.SAFEGUARDING_RENEWAL,

    "MOGL_First_Aid_completed_date": fields.FIRST_AID,
    "MOGL_First_Aid_renewal_date": fields.FIRST_AID_RENEWAL,

    "Ongoing_Learning_Hours": fields.ONGOING_LEARNING_HOURS,
}


def map_input_fields(headings: Iterable[str]) -> dict[str, str]:
    headings_set = set(headings)

    if "county_section" in headings_set:
        return _check_headings_names(_headings_county_post_nov_2020, headings_set)
    if "Reference" in headings_set:  # needs to be before MOGL Safety check
        return _check_headings_names(_headings_district_post_nov_2020, headings_set)
    if "GDPR1" in headings_set:
        return _check_headings_names(_headings_region_post_sep_2020, headings_set)
    if "MOGL_Safety_completed_date" in headings_set:
        return _check_headings_names(_headings_region_post_nov_2020, headings_set)

    # by default, return the newest set of columns
    return _check_headings_names(_headings_region_post_nov_2020, headings_set)


def _check_headings_names(reference: dict[str, str], supplied: set[str]) -> dict[str, str]:
    # Check that only all the expected keys are present
    if supplied == reference.keys():
        return reference

    expected = set(reference.keys())
    missing = expected.difference(supplied)
    extra = supplied.difference(expected)
    raise ValueError(f"Headings do not match. \nMissing headings: {missing}. \nExtra headings: {extra}")


# fmt: off
_canonical_post_sep_20 = [
    fields.MEMBERSHIP_NUMBER,
    fields.FORENAMES, fields.SURNAME, fields.KNOWN_AS, fields.EMAIL,
    fields.ROLE, fields.ROLE_START_DATE, fields.ROLE_END_DATE,
    fields.ROLE_STATUS, fields.REVIEW_DATE,
    fields.COUNTRY, fields.REGION,
    fields.COUNTY, fields.DISTRICT, fields.SCOUT_GROUP,
    fields.CE_CHECK, fields.APPROVAL_PANEL, fields.APPROVAL_COMMISSIONER, fields.APPROVAL_COMMITTEE, fields.REFERENCES,
    fields.MOD_01, fields.MOD_02, fields.MOD_03, fields.MOD_04,
    fields.MOD_01_EX, fields.TRUSTEE_INTRO, fields.GDPR,
    fields.WOOD_BADGE,
    fields.SAFETY, fields.SAFETY_RENEWAL, fields.SAFEGUARDING, fields.SAFEGUARDING_RENEWAL, fields.FIRST_AID, fields.FIRST_AID_RENEWAL,
]
# fmt: on

canonical_headings = _canonical_post_sep_20
