import warnings

import pandas as pd
from tqdm.auto import tqdm

from trifacta.tfobjects.wrangle_flow import WrangleFlow
from trifacta.util import tfrequests
from trifacta.util.tfAPIs import create_flow

warnings.simplefilter('always', FutureWarning)


def wrangle_existing(flow_id):
    progress_bar = tqdm(total=100)
    if progress_bar:
        progress_bar.update(0)

    if progress_bar:
        progress_bar.set_description("Fetching flow metadata")

    flowName = tfrequests.get(f"/v4/flows/{flow_id}").json()['name']
    if progress_bar:
        progress_bar.update(50)

    wf = WrangleFlow(flow_id, flowName)
    progress_bar.set_description("Wrangle flow fetched")
    if progress_bar:
        progress_bar.update(50)
    progress_bar.close()
    return wf


def wrangle(*dfs, flow_name='Python Flow'):
    __check_dataset_input(*dfs)
    progress_bar = tqdm(total=100)
    progress_bar.set_description(f"Creating flow : {flow_name}")
    flowId, flowName = create_flow(flow_name)
    progress_bar.update(25)

    progress_bar.set_description(f"Instantiating Wrangle Flow ")
    wrangle_flow = WrangleFlow(flowId, flowName)
    progress_bar.update(25)

    progress_bar.set_description(f"Uploading datasets")
    wrangle_flow.add_datasets(*dfs, progress_bar=progress_bar)
    progress_bar.set_description(f"Finished")
    progress_bar.n = 100
    progress_bar.refresh()

    return wrangle_flow


def __check_dataset_input(*dfs):
    for df in dfs:
        if not isinstance(df, pd.DataFrame) and not isinstance(df, tuple):
            raise TypeError("non-Dataframe objects included in list of items to wrangle")
        elif isinstance(df, tuple):
            if len(df) != 2:
                raise TypeError("Size of tuple should be exact two")
            elif not ((isinstance(df[0], str) and isinstance(df[1], pd.DataFrame)) or (
                    isinstance(df[1], str) and isinstance(df[0], pd.DataFrame))):
                raise TypeError("Invalid tuple format")
