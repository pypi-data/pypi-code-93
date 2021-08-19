from influxdb_client import InfluxDBClient
import pandas
from .credentials import Credentials


def write_pandas_df(df: pandas.DataFrame, cred: Credentials, measurement_name: str):
    with InfluxDBClient(url=cred.URL, token=cred.TOKEN, org=cred.ORG) as client:
        with client.write_api() as write_client:
            write_client.write(
                bucket=cred.BUCKET,
                org=cred.ORG,
                record=df,
                data_frame_measurement_name=measurement_name,
            )
