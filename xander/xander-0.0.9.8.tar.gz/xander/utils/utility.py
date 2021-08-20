import os
from datetime import datetime


def now(fmt='%Y-%m-%d %H:%M:%S'):
    """
    Return the current timestamp formatted with a specific format.

    @return: now datetime string
    """

    return datetime.now().strftime(fmt)


def get_slug(name):
    """
    Get the name e returns the slug.

    @param name: object name string
    @return: slug string
    """

    return name.lower().replace(' ', '_')


def get_parameters(storage_manager, parameters):
    """
    Get the input dictionary and take a particular action for each type of input.
    @param storage_manager: manager of the storage, used to handle the load and save of the files
    @param parameters: input dictionary that contains the list of input to be returned in a proper way
    @return: returns the list of input opportunely processed
    """

    # Initialize the list of parameters
    params_list = []

    # For each parameter provided by the user, the component puts in the params list or load it from the
    # storage
    for param in parameters:

        # Type of the input
        type = param['type']

        # Value of the input
        value = param['value']

        # Additional parameters expressed by the user
        additional_params = param['params'] if 'params' in param else {}

        try:
            # File case
            if type == 'file':

                # If the path is expressed as a list, it is converted into a string
                if isinstance(value, list):
                    value = os.path.join(*value)

                params_list.append(storage_manager.get_file(filename=value, params=additional_params))

            # Folder case
            elif type == 'folder':

                params_list.append(storage_manager.get_folder_files(folder_name=value, params=additional_params))

            # Query case
            elif type == 'query':

                params_list.append(storage_manager.fetch_query(query=value, params=additional_params))

            # All other cases: for example a string or and integer value
            else:
                params_list.append(value)

        # Exception in the case of file not found error
        except FileNotFoundError as e:
            raise Exception(
                f"Failed to load parameter with type '{type}' - '{value}'. Exception message: File not found in the "
                f"specified path.")

        # Generic exception: in the future more specific cases could be handled
        except Exception as e:
            raise Exception(f"Failed to load parameter with type '{type}' - '{value}'. Exception message: {e}")

    # Return the list of parameters
    return params_list
