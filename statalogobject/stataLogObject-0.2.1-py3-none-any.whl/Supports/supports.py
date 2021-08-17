from string import ascii_letters
import re


forest_attr = ['var_name', 'coefficient', 'lb_95', 'ub_95']
forest_header = ["Phenotype", "Coefficient", "Lower Bound", "Upper Bound"]
FOREST_DICT = {attr: header for attr, header in zip(forest_attr, forest_header)}


def clean_line(line):
    """
    Strip line of new line element then return, replacing negative floats without a 0, -.{value} with -0.{value}

    :param line: Line in the log file
    :type line: str
    """
    subbed = "".join([re.sub("\n", "", value) for value in line])
    return [f"-0.{v[2:]}" if v[0:2] == "-." else v for v in subbed.split(" ") if len(v) > 0]


def extract_values(line, skip=True):
    """Extract numerical values from a line"""

    values = [split_line.strip(ascii_letters).replace(",", "") for split_line in line.split()]

    values_return = []
    for v in values:
        try:
            values_return.append(float(v))
        except ValueError:
            if skip:
                pass
            else:
                values_return.append("MISSING")

    return values_return


def clean_value(value):
    """
    Clean the value of any newline expressions and then convert it to a float

    :param value: A string representation of a value from the body of the table
    :type value: str

    :return: A float representation of a value from the body of the table
    :rtype: float

    :raises ValueError: If converting to float is not possible
    """
    # Remove new line expressions
    value = re.sub("\n", "", value)

    # Change any numeric commas to periods
    value = re.sub(",", "", value)

    # Negative zero starting floats without a zero will not convert
    if value[0:2] == "-.":
        return float(f"-0.{value[2:]}")
    else:
        try:
            return float(value)
        except ValueError:
            return str(value)


def methods_in_line(var_name, cf, lb, ub, rd=2):
    """
    Construct an in line methods line from a forest plot formatted line

    :param var_name: var name
    :param cf: coefficient
    :param lb: lower bound
    :param ub: upper bound
    :param rd: How many decimal places you want to round to
    :return: A string representation of this line
    """
    return f"{var_name}\t(RD={round(float(cf), rd)}, 95%CI: {conf_interval(lb, ub, rd)})\n"


def conf_interval(lb_95, ub_95, rounding=4):
    """Set the confidence interval as a string of str((Min_CI; Max_CI)), where the CI's can be rounded"""
    return f"{round(lb_95, rounding)}; {round(ub_95, rounding)}"
