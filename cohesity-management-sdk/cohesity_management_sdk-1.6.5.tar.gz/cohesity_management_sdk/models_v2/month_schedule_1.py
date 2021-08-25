# -*- coding: utf-8 -*-


class MonthSchedule1(object):

    """Implementation of the 'Month Schedule1' model.

    Specifies settings that define a schedule for a Protection Group runs to
    on specific week and specific days of that week.

    Attributes:
        frequency (long|int): Specifies a factor to multiply the unit by, to
            determine the backup schedule. <br> Example: If 'frequency' set to
            2 and the unit is 'Hours', then Snapshots are backed up every 2
            hours. If selected unit is 'Weeks' or 'Months' then frequency will
            only be applied if policy type is DMaas.
        day_of_week (list of DayOfWeekEnum): Specifies a list of days of the
            week when to start Protection Group Runs. <br> Example: To run a
            Protection Group on every Monday and Tuesday, set the schedule
            with following values: <br>  unit: 'Weeks' <br>  dayOfWeek:
            ['Monday','Tuesday']
        week_of_month (WeekOfMonthEnum): Specifies the week of the month (such
            as 'Third') in a Monthly Schedule specified by unit field as
            'Months'. <br>This field is used in combination with 'dayOfWeek'
            to define the day in the month to start the Protection Group Run.
            <br> Example: if 'weekOfMonth' is set to 'Third' and day is set to
            'Monday', a backup is performed on the third Monday of every
            month.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "frequency":'frequency',
        "day_of_week":'dayOfWeek',
        "week_of_month":'weekOfMonth'
    }

    def __init__(self,
                 frequency=None,
                 day_of_week=None,
                 week_of_month=None):
        """Constructor for the MonthSchedule1 class"""

        # Initialize members of the class
        self.frequency = frequency
        self.day_of_week = day_of_week
        self.week_of_month = week_of_month


    @classmethod
    def from_dictionary(cls,
                        dictionary):
        """Creates an instance of this model from a dictionary

        Args:
            dictionary (dictionary): A dictionary representation of the object as
            obtained from the deserialization of the server's response. The keys
            MUST match property names in the API description.

        Returns:
            object: An instance of this structure class.

        """
        if dictionary is None:
            return None

        # Extract variables from the dictionary
        frequency = dictionary.get('frequency')
        day_of_week = dictionary.get('dayOfWeek')
        week_of_month = dictionary.get('weekOfMonth')

        # Return an object of this model
        return cls(frequency,
                   day_of_week,
                   week_of_month)


