""" This module parses datapoints from an different file types """

import csv
import openpyxl
from weaviate_etl.utilities import get_reference_class_name_from_field


###################################################################################################
## These functions are used by both the excel parser and the csv parser
###################################################################################################


def _initialize_result(model: dict) -> dict:
    """
    Creates a default datapoint entry

    Parameters
    ----------
    model: dict
        A dict that contains the data model of the data that will be parsed

    Returns
    ------
    dict
        The dict containing the default (empty) result of parsing
    """

    # Initialize the return value
    result = {}
    result['datapoints'] = []
    result['count'] = 0
    result['entities'] = {}

    # Collect all entities from the data configuration
    for dataclass in model['classes']:
        for col in dataclass['columns']:
            if col['entity']:
                classname = get_reference_class_name_from_field(col['name'])
                result['entities'][classname] = []

    return result


def _create_default_entry(classname: str, row: int) -> dict:
    """
    Creates a default datapoint entry

    Parameters
    ----------
    classname: str
        A string that indicates the classname of the datapoint
    row: int
        The row number for this line of data

    Returns
    ------
    dict
        The dict containing the default entry
    """

    # initialize the return value
    entry = {}

    # store the class name of this entry
    entry['classname'] = classname

    # store the row number of this data point
    entry['row'] = row

    # set the batch number for this item will be set at import if batching is used
    entry['batchNumber'] = 1

    return entry


###################################################################################################
## These functions are for the excel parser
###################################################################################################


def _parse_data_line_excel(data: dict, sheet: openpyxl.worksheet, row: int, dataclass: dict) -> dict:
    """
    parses a single line of data from the excel file.

    Parameters
    ----------
    data: dict
        A dict that contains the data that has already been parsed
    sheet: openpyxl.worksheet
        The sheet from the excel file that contains the date line we are parsing
    row: int
        The row number for this line of data
    dataclass: dict
        A dict that contains the values for this line of data

    Returns
    ------
    dict
        The dict containing the data point for this line
    """

    #pylint: disable=too-many-branches
    #pylint: disable=too-many-statements

    # initialize the return value
    entry = _create_default_entry(dataclass['classname'], row)

    # for each column in the data, read the appropriate value from the excel sheet
    for col in dataclass['columns']:

        # cast the value read from the excel sheet to the appropriate type
        if col['type'] == 'int':
            if sheet.cell(row=row, column=col['number']).value is not None:
                value = int(sheet.cell(row=row, column=col['number']).value)
            else:
                value = 0

        elif col['type'] == 'string':
            if sheet.cell(row=row, column=col['number']).value is not None:
                value = str(sheet.cell(row=row, column=col['number']).value)
            else:
                value = ""

        elif col['type'] == 'text':
            if sheet.cell(row=row, column=col['number']).value is not None:
                value = str(sheet.cell(row=row, column=col['number']).value)
            else:
                value = ""

        elif col['type'] == 'date':
            if sheet.cell(row=row, column=col['number']).value is not None:
                value = str(sheet.cell(row=row, column=col['number']).value)
            else:
                value = ""

        elif col['type'] == 'geoCoordinates':
            if sheet.cell(row=row, column=col['number']).value is not None:
                value = str(sheet.cell(row=row, column=col['number']).value)
            else:
                value = ""

        elif col['type'] == 'phoneNumber':
            if sheet.cell(row=row, column=col['number']).value is not None:
                value = str(sheet.cell(row=row, column=col['number']).value)
            else:
                value = ""

        elif col['type'] == 'number':
            if sheet.cell(row=row, column=col['number']).value is not None:
                value = float(sheet.cell(row=row, column=col['number']).value)
            else:
                value = ""

        elif col['type'] == 'boolean':
            if sheet.cell(row=row, column=col['number']).value is not None:
                value = bool(sheet.cell(row=row, column=col['number']).value)
            else:
                value = False

        elif col['type'] == 'json':
            if sheet.cell(row=row, column=col['number']).value is not None:
                value = str(sheet.cell(row=row, column=col['number']).value)
            else:
                value = ""

        # Store the value of the property with the data entry point
        entry[col['name']] = value

        # for each entity check if the value is already in the list of values for this entity
        if col['entity']:
            classname = get_reference_class_name_from_field(col['name'])
            if value not in data['entities'][classname]:
                data['entities'][classname].append(value)

    return entry


def parse_excel(model: dict, sheet: openpyxl.worksheet) -> dict:
    """
    parses the data from file indicated by path and that fits the argument model

    Parameters
    ----------
    model: dict
        A dict that contains the data model
    sheet: openpyxl.worksheet
        A worksheet that contains the data to be parsed according to the argument model

    Returns
    ------
    dict
        The dict describing the Weaviate schema
    """

    # Initialize the return value
    data = _initialize_result(model)

    # process the data line by line
    end = False
    row = 2
    while not end:
        source = sheet.cell(row=row, column=1).value
        if source is None:
            end = True
        else:
            for dataclass in model['classes']:
                point = _parse_data_line_excel(data, sheet, row, dataclass)
                if point is not None:
                    data['datapoints'].append(point)
                    data['count'] += 1
            row += 1

    return data


###################################################################################################
## These functions are for the csv parser
###################################################################################################


def _parse_data_line_csv(data: dict, line: list, row: int, dataclass: dict) -> dict:
    """
    parses a single line of data from the csv file.

    Parameters
    ----------
    data: dict
        A dict that contains the data that has already been parsed
    line: list
        A list that contains the values for this line of data
    row: int
        The row number for this line of data
    dataclass: dict
        A dict that contains the values for this line of data

    Returns
    ------
    dict
        The dict containing the data point for this line
    """

    #pylint: disable=too-many-branches
    #pylint: disable=too-many-statements

    # initialize the return value
    entry = _create_default_entry(dataclass['classname'], row)

    # for each column in the data, read the appropriate value from the excel sheet
    for col in dataclass['columns']:

        # cast the value read from the excel sheet to the appropriate type
        column = col['number'] - 1
        if col['type'] == 'int':
            if line[column] is not None:
                value = int(line[column])
            else:
                value = 0

        elif col['type'] == 'string':
            if line[column] is not None:
                value = str(line[column])
            else:
                value = ""

        elif col['type'] == 'text':
            if line[column] is not None:
                value = str(line[column])
            else:
                value = ""

        elif col['type'] == 'date':
            if line[column] is not None:
                value = str(line[column])
            else:
                value = ""

        elif col['type'] == 'geoCoordinates':
            if line[column] is not None:
                value = str(line[column])
            else:
                value = ""

        elif col['type'] == 'phoneNumber':
            if line[column] is not None:
                value = str(line[column])
            else:
                value = ""

        elif col['type'] == 'number':
            if line[column] is not None:
                value = float(line[column])
            else:
                value = ""

        elif col['type'] == 'boolean':
            if line[column] is not None:
                value = bool(line[column])
            else:
                value = False

        # Store the value of the property with the data entry point
        entry[col['name']] = value

        # for each entity check if the value is already in the list of values for this entity
        if col['entity']:
            classname = get_reference_class_name_from_field(col['name'])
            if value not in data['entities'][classname]:
                data['entities'][classname].append(value)

    return entry


def parse_csv(model: dict, reader: csv.reader) -> dict:
    """
    parses the data from file indicated by path and that fits the argument model

    Parameters
    ----------
    model: dict
        A dict that contains the data model
    reader: csv.reader
        The csv reader that contains the data to be parsed

    Returns
    ------
    dict
        The dict containing the data
    """

    # Initialize the return value
    data = _initialize_result(model)

    # process the data line by line
    row = 0
    for line in reader:
        if row == 0:
            row += 1
        else:
            for dataclass in model['classes']:
                point = _parse_data_line_csv(data, line, row, dataclass)
                if point is not None:
                    data['datapoints'].append(point)
                    data['count'] += 1
            row += 1

    return data
