''' Utils library '''


def read_data(input_file):
    ''' read data from a dataset'''
    # TODO: Get this from the schema!
    mapping = {
        "sepal_length": float,
        "sepal_width": float,
        "petal_length": float,
        "petal_width": float,
        "species": lambda x: x,
        "_id": int
    }
    headers = input_file.readline().strip().split(',')
    lines = input_file.readlines()
    data = []
    for index, line in enumerate(lines):
        element = {'_id': index}
        for k, v in zip(headers, line.strip().split(',')):
            element[k] = mapping[k](v.strip())
        data.append(element)
    input_file.close()
    return data


def get_columns_dictnames(config_cols):
    ''' making a dictionary out of the columns '''
    cols_dictnames = {}
    for group in config_cols:
        names = []
        cols_info = config_cols[group]
        for item in cols_info:
            a = cols_info[item]['name']
            names.append(a)
        cols_dictnames[group] = names
    return cols_dictnames
