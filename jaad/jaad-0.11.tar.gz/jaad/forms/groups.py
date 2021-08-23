def describe_sub_group(sub_group):
    description = ""

    if len(sub_group) == 1:
        description += "'" + sub_group[0] + "'"
    else:
        description += "[" + "' and '".join(sub_group) + "]"

    return description


def describe_group(group):
    return ", ".join(describe_sub_group(sub_group) for sub_group in group)


def link_message_to_group(message, group):
    return {field: [message] for sub_group in group for field in sub_group}


def check_sub_group(defined_fields, sub_group):
    sub_group_error = {}

    if len(defined_fields) != len(sub_group):
        error_message = (
            "You cannot use '"
            + "' and '".join(defined_fields)
            + "' without defining '"
            + "' and '".join(
                [field for field in sub_group if field not in defined_fields]
            )
            + "'"
        )
        sub_group_error.update({field: error_message for field in sub_group})

    return sub_group_error


def get_number_of_sub_group_defined(data, optional_group):
    sub_groups_errors = {}
    number_of_group_defined = 0
    for sub_group in optional_group:
        defined_fields = [
            field for field in sub_group if field in data and data[field] is not None
        ]
        if len(defined_fields) > 0:
            number_of_group_defined += 1
            sub_group_errors = check_sub_group(defined_fields, sub_group)
            sub_groups_errors.update(sub_group_errors)
    return number_of_group_defined, sub_groups_errors


def validate_group_of_field(group, data, min_defined=None, max_defined=None):
    """
    Validate than in data, at least min_defined keys among group are defined and at most max_defined.
    If min_defined is None, there is no lower limit
    If max_defined is None, there is no upper limit
    :type group: list of group, each group is a list of keys (string) in dict that must be defined in data
    :type data: dict
    :type min_defined: Optional[int]
    :type max_defined: Optional[int]
    :returns: dict of list of error for each field
    """
    group_errors = {}

    (number_of_sub_group_defined, sub_groups_errors) = get_number_of_sub_group_defined(
        data, group
    )
    group_errors.update(sub_groups_errors)

    if max_defined is not None and number_of_sub_group_defined > max_defined:
        error_message = (
            "At most {} of those fields or groups of fields can be defined: {}"
        ).format("one" if max_defined == 1 else max_defined, describe_group(group))
        group_errors.update(link_message_to_group(error_message, group))

    if min_defined is not None and number_of_sub_group_defined < min_defined:
        error_message = (
            "At least {} of those fields or groups of fields must be defined: {}"
        ).format("one" if min_defined == 1 else min_defined, describe_group(group))
        group_errors.update(link_message_to_group(error_message, group))

    return group_errors
