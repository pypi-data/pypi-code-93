import re


def parse_line(line):
    """parse a single line

    Args:
        line ([String]): A line from the prettytable

    Returns:
        An arr of the items in the line
    """
    arr = line.split("|")
    # Get rid of empty characters
    arr = map(str.strip, arr)
    arr = [word for word in arr if word]
    return arr


def parse_table(s):
    """Give a prettytable string, return a dict with key as the field name, and value as the corresponding item

    Args:
        s (String): A pretty table string

    Returns:
        [Array[Dict]]: An arr of dictionaries, each dictionary contain information of one row in the prettytable
    """
    # intialize
    s = s.strip()

    # Split the lines
    lines = s.split("\n")

    # Filter out the seperating lines
    pattern = re.compile("\+-+")
    filtered_lines = [s for s in lines if not re.match(pattern, s)]

    # Get the filed names
    header_line = filtered_lines[0]
    header_arr = parse_line(header_line)

    parse_result_arr = []
    # Do the same for the rest lines
    for line in filtered_lines[1:]:
        arr = parse_line(line)
        cur_dict = {}
        for index in range(len(header_arr)):
            cur_dict[header_arr[index]] = arr[index]
        parse_result_arr.append(cur_dict)

    return parse_result_arr
