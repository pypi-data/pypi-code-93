from functools import reduce

import pandas as pd

from banner.utils.const import NW_VOLTAGE, NW_CURRENT, NW_TEMP, NW_AUX_CHANNEL, NW_STEP_RANGE, NW_TIMESTAMP, NW_DATESTAMP, NW_CHANNEL_GROUP

def calc_neware_cols(data: pd.DataFrame):
    data[NW_VOLTAGE] = data[NW_VOLTAGE].apply(lambda obj: obj / 10000)
    data[NW_CURRENT] = data.apply(lambda row: round(row[NW_CURRENT] * __current_coeff(row[NW_STEP_RANGE]), 4), axis=1)
    
    if NW_TEMP in data:
        data[NW_TEMP] = data[NW_TEMP].apply(lambda obj: obj / 10)
    
        if NW_AUX_CHANNEL in data:
            data = __group_by_auxchl(data)
        
    return data

def __current_coeff(cur_range):
    return 0.00001 * 10**min(4, len(str(cur_range))) * (0.1 if cur_range < 0 else 1)
    
def __group_by_auxchl(data):
    merge_columns = [column for column in list(data.columns) if column not in [NW_TEMP, NW_AUX_CHANNEL]]
    
    # groupby -> to list & rename NW_AUX_CHANNEL
    group_as_list = [
        df.loc[
            :, df.columns != NW_AUX_CHANNEL
        ].rename(columns={NW_TEMP: f'{NW_CHANNEL_GROUP}{group}'})
        for group, df in data.groupby([NW_AUX_CHANNEL])
    ]
    
    # Merge 
    merged_data = reduce(lambda left,right: pd.merge(left, right, on=merge_columns, how='left'), group_as_list)

    return merged_data