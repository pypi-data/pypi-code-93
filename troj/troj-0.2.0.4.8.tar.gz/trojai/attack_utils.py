import random
import torchvision.ops


def random_parameters(param_dict, num_iters=1):
    """
    A function which takes in a dictionary of parameter names as keys and lists of possible parameter values corresponding to
    each key. Computes some number of random sets of parameters and returns them as a list of dictionaries.

    :param param_dict: A dictionary containing the names of the input parameters to the art adversary as keys, where the
    dictionary values are lists containg the possible values for the corresponding key.
    :param num_iters: Number of parameter sets to generate.

    :return: A list of dictionaries where keys are arguments for model functions and values are the values for those
    arguments.

    """
    train_params_dicts = []
    for _ in range(num_iters):
        param_names = list(param_dict.keys())
        param_vals = list(param_dict.values())
        rand_params = [random.choice(params) for params in param_vals]
        rand_dict = dict(zip(param_names, rand_params))
        train_params_dicts.append(rand_dict)
    return train_params_dicts


def log_to_dataframe(dataframe, index, log_dict):
    '''
    Logs data to dataframe.

    :param dataframe: Dataframe to log to.
    :param index: The indices to log to.
    :param log_dict: The dictionary containing data to log
    :return: updated dataframe.
    '''
    for key in list(log_dict.keys()):
        if key not in dataframe.columns:
            dataframe[key] = ""
            dataframe[key].astype("object")
        dataframe.loc[index, key] = log_dict[key]
    return dataframe
