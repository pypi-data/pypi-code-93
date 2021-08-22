import pandas as pd

from assistants.compliance.util import fields
from assistants.compliance.util.input_data_utility import completed_to_due_vector

dt_new_mogl = pd.Timestamp(2020, 9, 15)  # September 2020 MOGL changes


def fix_some_dates(data: pd.DataFrame) -> pd.DataFrame:
    """Fix Some Dates

    Make sure if we have old M1 / M1EX then we also have Safety and Safeguarding
    Make sure M1, M1EX, Trustee Intro, GDPR, First Aid, Safety & Safeguarding are applied as appropriate

    We use pandas (vector) operations - slower but easier to understand!

    """
    data["safety_flag"] = False

    m1_m1ex_min = "min_mod_1"
    sfty_max = "max_m23_lms"

    has_auto_safety = fields.MOD_LMS in data and fields.MOD_23 in data

    data[m1_m1ex_min] = data[[fields.MOD_01, fields.MOD_01_EX]].min(axis=1)
    if has_auto_safety:
        data[sfty_max] = data[[fields.MOD_LMS, fields.MOD_23]].max(axis=1)
    g = data.groupby(fields.MEMBERSHIP_NUMBER)

    # Given M01Ex validates M01, check that both are blank
    m_01_and_m01_ex_unset = data[fields.MOD_01].isna() & data[fields.MOD_01_EX].isna()
    # Where a given role has a blank for M01 or M01Ex and that member has a valid value for that
    # training type, fill it in
    # rolling_exclude is a crude attempt at an elif/switch chain in boolean logic
    rolling_exclude = pd.Series(False, index=data.index)
    for column in (fields.MOD_01, fields.MOD_01_EX):
        earliest_training_by_member = g[column].transform("min")
        mask = m_01_and_m01_ex_unset & earliest_training_by_member.notna() & ~rolling_exclude
        data.loc[mask, column] = earliest_training_by_member

        rolling_exclude = rolling_exclude | earliest_training_by_member.notna()

        # TODO implied M01 from VBA...

    if has_auto_safety:
        # Until 2020-09-15 Safety MOGL was validated by LMS, Module 23 and Module 17. M23 and LMS are
        # not automatically applied by Compass, so we do so here if the date is later than the regular
        # Safety date.
        data["safety_flag"] = False  # Unneeded as set in parent function
        max_safety_modules = g[sfty_max].transform("max")
        data.loc[max_safety_modules > g[fields.SAFETY].transform("max"), "safety_flag"] = True
        data.loc[data["safety_flag"], fields.SAFETY] = max_safety_modules[data["safety_flag"]]

    # For Safety & Safeguarding, before 2020-09-15 these were automatically validated by Module 1
    # and Module 1EX. Automatic validation of SFTY & SAFE was only valid for the first validation
    # of M01/M01EX, so we find the oldest (min value), and a boolean mask for before/after the
    # September 2020 MOGL changes. For both SFTY & SAFE we then get the latest training date by
    # member, find the relevant date for auto-validation, and apply both to blanks
    min_m01_member = g[m1_m1ex_min].transform("min")
    pre_new_mogl = min_m01_member < dt_new_mogl
    for column, renewal, mask in (
            (fields.SAFETY, fields.SAFETY_RENEWAL, ~data["safety_flag"]),
            (fields.SAFEGUARDING, fields.SAFEGUARDING_RENEWAL, slice(None)),
    ):
        latest_training_by_member = g[column].transform("max")
        # make sure Safety / Safeguarding set (if possible)
        # if M01/M01EX is set, before the 09/20 MOGL changes, and SFTY/SAFE isn't set
        auto_validated_date = min_m01_member[pre_new_mogl & latest_training_by_member.isna()]
        # Fills blanks with auto validated dates
        latest_training_with_auto_validated = latest_training_by_member.fillna(auto_validated_date)
        # Applies max value to blanks for that member
        data.loc[mask, column] = data.loc[mask, column].fillna(latest_training_with_auto_validated)

        # Given we have changed Safety/Safeguarding dates, we need to update renewal dates
        data[renewal] = completed_to_due_vector(data[column])

    # Finds max value for each member, and applies that value to nulls for that member
    for column in (
            fields.TRUSTEE_INTRO,
            fields.GDPR,
            # "safety" above
            fields.SAFETY_RENEWAL,
            # "safeguarding" above
            fields.SAFEGUARDING_RENEWAL,
            fields.FIRST_AID,
            fields.FIRST_AID_RENEWAL,
    ):
        data[column] = data[column].fillna(g[column].transform("max"))

    # Clean up
    del data[m1_m1ex_min]
    if has_auto_safety:
        del data[sfty_max]
    return data
