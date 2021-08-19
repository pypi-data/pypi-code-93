from datetime import datetime, timedelta

BUFFER_DURATION_IN_MINUTES = 10


def get_buffered_timestamp(timestamp: str, buffer_duration=BUFFER_DURATION_IN_MINUTES):
    """
    Adds ten minutes buffer to given start date

    :param timestamp: start date
    :param buffer_duration: buffer duration in minutes
    :return: buffered start date
    """
    start = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S") - timedelta(
        minutes=buffer_duration,
    )
    return start.strftime("%Y-%m-%d %H:%M:%S")
