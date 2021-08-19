import pandas as pd


def download_data(data_source):
    # downloads data from the data_source
    # for now let's assume that it is FTP and it is a csv file
    df = pd.read_csv(data_source)

    # TODO: move these type of transformations to the workflow
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df
