from datetime import timedelta


def get_elapsed_time(start, end):
    """Get elapsed time in a human readable format."""
    td: timedelta = start - end
    return str(timedelta(seconds=td.seconds))
