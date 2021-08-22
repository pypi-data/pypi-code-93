import pandas as pd


def back_project(data: pd.DataFrame):
    # fmt: off
    date_cols = [
        'Role_Start_Date', 'Role_End_Date', 'review_date',
        'Essential_Info', 'Essential_Info_Exec1', 'PersonalLearningPlan', 'Tools4Role', 'Tools_for_Role_Section_Leaders', 'GDPR1', 'Trustee_Introduction',
        'WoodBadgeReceived',
        'OngoingSafetyTraining', 'MOGL_Safety_renewal', 'OngoingSafeguardingTraining', 'MOGL_Safeguarding_renewal', 'FirstAidTraining', 'MOGL_First_Aid_renewal'
    ]  # TODO date cols list
    # fmt: on
    data[date_cols] = data[date_cols].astype("datetime64[ns]")
    for c in date_cols:
        data.loc[data[c] >= pd.Timestamp("2020-10-19"), c] = pd.NA
