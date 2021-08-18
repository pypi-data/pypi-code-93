class HeaderKeyExtractError(Exception):
    def __init__(self, index, extract_list, var_name):
        super(HeaderKeyExtractError, self).__init__(
            f"\n\tTried to extract index {index} from list {extract_list} of length {len(extract_list)} for {var_name}")


class InvalidKeyExtract(Exception):
    def __init__(self, key, var_name):
        super(InvalidKeyExtract, self).__init__(
            f"\n\tFailed to find {key} for {var_name}")


class EntryLengthInvalid(Exception):
    def __init__(self, field_names, values):
        super(EntryLengthInvalid, self).__init__(
            f"\n\tLength of extracted {len(values)} lines is {values} but {len(field_names)} exist:"
            f"\n\t{field_names}")


class ForestPlotInvalidAttributes(Exception):
    def __init__(self, column_attributes, forest_columns):
        super(ForestPlotInvalidAttributes, self).__init__(
            f"\n\tFailed to find all of {forest_columns} in {column_attributes}")