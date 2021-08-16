import pandas
from copy import deepcopy

def concat_variables(list_of_variables, title_function=lambda v: v.name):
    
    list_of_variables = deepcopy(list_of_variables)
    list_of_dfs_to_concat = []

    for v in list_of_variables:

        v_df = v.value.rename(columns={"value": title_function(v)})

        list_of_dfs_to_concat.append(v_df)

    result = pandas.concat(list_of_dfs_to_concat, axis=1)

    return result