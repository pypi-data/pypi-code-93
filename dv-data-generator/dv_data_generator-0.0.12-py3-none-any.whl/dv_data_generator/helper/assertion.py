def is_list_of_string(input_list):
    return all(isinstance(s, str) for s in input_list)
