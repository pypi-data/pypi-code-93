import csv


def get_data_from_csv(file):
    '''
    :param file:
    :return: data rows in the form of list of dict
    '''

    with open(file, 'r', encoding='utf-8') as f:
        rows = [{k: v for k, v in row.items()} for row in csv.DictReader(f, skipinitialspace=True)]
    return rows


def export_dict_rows_to_csv(file, rows, fields, mode='w'):
    '''
    export list of dicts to csv file
    :return:
    '''
    with open(file, mode, encoding='utf-8', newline='') as output_file:
        dict_writer = csv.DictWriter(output_file, fields, extrasaction='ignore')
        if mode == 'w':
            dict_writer.writeheader()
        dict_writer.writerows(rows)


def export_tuple_rows_to_csv(file, rows, fields):
    '''
    export list of tuple to csv file
    :return:
    '''
    with open(file, 'w', encoding='utf-8', newline='') as output_file:
        writer = csv.writer(output_file)
        writer.writerow(fields)
        writer.writerows(rows)
