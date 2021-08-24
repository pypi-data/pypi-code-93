

def get_column_dtype(event, steps_manager):
    """
    Sends back the dtype of the column
    """
    sheet_index = event['sheet_index']
    column_header = event['column_header']

    series = steps_manager.dfs[sheet_index][column_header]

    return str(series.dtype)