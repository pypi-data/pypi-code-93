def log_to_dataframe(dataframe, index, log_dict):
    """
    Logs data to dataframe.

    :param dataframe: Dataframe to log to.
    :param index: The indices to log to.
    :param log_dict: The dictionary containing data to log
    :return: updated dataframe.
    """
    for key in list(log_dict.keys()):
        if key not in dataframe.columns:
            dataframe[key] = ""
            dataframe[key].astype("object")
        dataframe.loc[index, key] = log_dict[key]
    return dataframe
