import pickle


def save_history(history, filename):
    """saves the History.history dictionary of a model.fit() to a pickle file

    Args:
        history (dict): History.history dictionary, output from model.fit().
        filename (str): full path and name output pickle file
    """

    with open(filename, "wb") as pfile:
        pickle.dump(history, pfile)


def load_history(filename):
    """load the history.history dictionary of a model.fit() from a pickle file

    Args:
        filename (str): full path and name output pickle file

    Returns:
        history (dict): training history
    """

    with open(filename, "rb") as pfile:
        history = pickle.load(pfile)

    return history


def save_datetime(value, filename):
    """saves the datetime to a pickle file

    Args:
        value (datetime):
        filename (str): full path and name output pickle file
    """
    with open(filename, "wb") as f:
        pickle.dump(value, f)


def load_datetime(filename):
    """load the datetime from a pickle file

    Args:
        filename (str): full path and name output pickle file

    Returns:
        value (datetime): datetime
    """
    with open(filename, "rb") as f:
        value = pickle.load(f)
    return value
