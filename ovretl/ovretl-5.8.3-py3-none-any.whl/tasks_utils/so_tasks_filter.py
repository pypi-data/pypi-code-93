import pandas as pd


def so_tasks_filter(tasks_df: pd.DataFrame) -> pd.DataFrame:
    so_tasks_df = tasks_df.loc[tasks_df["so_id"].notnull(), :]
    return so_tasks_df
