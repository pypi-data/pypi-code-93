import pandas as pd


def kronos_propositions_missing_categories(kronos_propositions_df: pd.DataFrame):
    category_complete = kronos_propositions_df.groupby("category").apply(
        lambda group: group["kronos_selected"].any()  # or group["selected"].any()
    )
    if False in category_complete.values:
        return category_complete.value_counts()[False]
    return 0


def add_missing_categories(kronos_propositions_with_ocp_df: pd.DataFrame):
    cq_fullness = kronos_propositions_with_ocp_df.groupby(by=["kronos_proposition_id"]).apply(
        kronos_propositions_missing_categories
    )

    kronos_propositions_with_ocp_df = pd.merge(
        kronos_propositions_with_ocp_df,
        cq_fullness.to_frame(name="missing_categories"),
        left_on="kronos_proposition_id",
        right_index=True,
    )
    kronos_propositions_with_ocp_df["full"] = kronos_propositions_with_ocp_df["missing_categories"].apply(
        lambda x: x == 0
    )
    kronos_propositions_with_ocp_df.loc[:, "proposition_id"] = kronos_propositions_with_ocp_df["proposition_id"].apply(
        lambda x: int(x) if not pd.isna(x) else x
    )
    return kronos_propositions_with_ocp_df
