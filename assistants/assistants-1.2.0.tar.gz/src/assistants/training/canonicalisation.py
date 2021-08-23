from __future__ import annotations

from typing import Any, TYPE_CHECKING

from assistants.training import fields as fields_training

if TYPE_CHECKING:
    from collections.abc import Iterable


# ========================================================================================
#
#  check the headings meet our minimum requirement
#  and set up the columns
#
# ========================================================================================
Headings = {
    "contact_number": fields_training.CONTACT_NUMBER,

    "forenames": fields_training.FORENAMES,
    "surname": fields_training.SURNAME,
    "preferred_forename": fields_training.PREFERRED,

    "email": fields_training.EMAIL,

    "role": fields_training.ROLE,
    "role_start_date": fields_training.ROLE_START_DATE,
    "role_status": fields_training.ROLE_STATUS,
    "review_date": fields_training.REVIEW_DATE,

    "wood_badge_date": fields_training.WOOD_BADGE_DATE,

    "country": fields_training.COUNTRY,
    "region": fields_training.REGION,
    "county": fields_training.COUNTY,
    "county_section": fields_training.COUNTY_SECTION,
    "district": fields_training.DISTRICT,
    "district_section": fields_training.DISTRICT_SECTION,
    "scout_group": fields_training.SCOUT_GROUP,
    "scout_group_section": fields_training.SCOUT_GROUP_SECTION,

    "module_name": fields_training.MODULE,
    "module_validated_date": fields_training.VALIDATED_DATE,

    "validated_by": fields_training.VALIDATED_BY,
    "validated_by_name": fields_training.VALIDATED_BY_NAME,
    "learning_method_description": fields_training.LEARNING_METHOD,
    "learning_method_date": fields_training.LEARNING_METHOD_DATE,
    "validation_criteria": fields_training.VALIDATION_CRITERIA,
    "validation_criteria_date": fields_training.VALIDATION_CRITERIA_DATE,
    "validator_name": fields_training.VALIDATOR_NAME,

    "training_adviser_number": fields_training.TRAINING_ADVISER,
    "training_adviser_name": fields_training.TRAINING_ADVISER_NAME,
}


HeadingsRegionPreFeb2021 = {
    # remember the columns
    "contact_number": fields_training.CONTACT_NUMBER,

    "forenames": fields_training.FORENAMES,
    "surname": fields_training.SURNAME,
    "preferred_forename": fields_training.PREFERRED,

    "Email": fields_training.EMAIL,

    "MRole": fields_training.ROLE,
    "RoleStatus": fields_training.ROLE_STATUS,
    "Role_Start_Date": fields_training.ROLE_START_DATE,
    "review_date": fields_training.REVIEW_DATE,

    "wood_received": fields_training.WOOD_BADGE_DATE,

    "Region": fields_training.REGION,
    "County": fields_training.COUNTY,
    "County_Section": fields_training.COUNTY_SECTION,
    "District": fields_training.DISTRICT,
    "District_Section": fields_training.DISTRICT_SECTION,
    "Scout_Group": fields_training.SCOUT_GROUP,
    "Scout_Group_Section": fields_training.SCOUT_GROUP_SECTION,

    "module_name": fields_training.MODULE,
    "module_validated_date": fields_training.VALIDATED_DATE,

    "validated_by": fields_training.VALIDATED_BY,
    "Validatedbyname": fields_training.VALIDATED_BY_NAME,
    "learning_method_description": fields_training.LEARNING_METHOD,
    "learningmethod_actual_completion": fields_training.LEARNING_METHOD_DATE,
    "Validation_criteria": fields_training.VALIDATION_CRITERIA,
    "VCactual_completion": fields_training.VALIDATION_CRITERIA_DATE,
    "VMname": fields_training.VALIDATOR_NAME,

    "training_advisor_number": fields_training.TRAINING_ADVISER,
    "trainingadvisorname": fields_training.TRAINING_ADVISER_NAME,
}


def map_input_fields(headings: Iterable[str]) -> Any:
    headings_set = set(headings)  # speed up

    if "MRole" in headings_set:
        if headings_set == HeadingsRegionPreFeb2021.keys():
            return HeadingsRegionPreFeb2021
    if "country" in headings_set:
        if headings_set == HeadingsRegionPreFeb2021.keys():
            return Headings
    raise ValueError("No map matches passed headings!")
