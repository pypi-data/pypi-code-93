from dataclasses import dataclass
import random

random.seed(0)

import pandas as pd


@dataclass
class BlockVariableValue:
    variable: str
    block: int
    variable_type: str
    value: float

    def to_df(self):
        df = pd.DataFrame()


def choose_uniformly_float(start, end):
    return random.uniform(start, end)


def choose_uniformly_int(start, end):
    return random.randrange(start, end, 1)


def choose_variable_to_update(optim_input_df):
    # unique variables to optimize
    variables = optim_input_df['variable'].unique()

    # randomly select variable to update
    variable = random.choice(variables)

    # randomly select block
    # - find slice of the optim dataframe for the variable
    sub_optim_input_df = optim_input_df[optim_input_df['variable'] == variable].reset_index(drop=True)
    # - randomly select index from the slice
    selected_index = random.choice(sub_optim_input_df.index)
    # - take block index from the selected index
    selected_block = sub_optim_input_df.loc[selected_index, 'bcs']

    # randomly select value
    # - take variable range
    choice_range = sub_optim_input_df.loc[selected_index, ['xl', 'xu']].values
    # - take variable type
    variable_type = sub_optim_input_df.loc[selected_index, 'variable_type']
    if variable_type == 'int':
        value = choose_uniformly_int(*choice_range)
    else:
        value = round(choose_uniformly_float(*choice_range), 4)

    return BlockVariableValue(block=selected_block, variable=variable, variable_type=variable_type, value=value)
