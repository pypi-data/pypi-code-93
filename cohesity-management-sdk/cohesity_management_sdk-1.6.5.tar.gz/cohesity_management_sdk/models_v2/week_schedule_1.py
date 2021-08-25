# -*- coding: utf-8 -*-


class WeekSchedule1(object):

    """Implementation of the 'Week Schedule1' model.

    Specifies settings that define a schedule for a Protection Group runs to
    start on certain days of week.

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

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "frequency":'frequency',
        "day_of_week":'dayOfWeek'
    }

    def __init__(self,
                 frequency=None,
                 day_of_week=None):
        """Constructor for the WeekSchedule1 class"""

        # Initialize members of the class
        self.frequency = frequency
        self.day_of_week = day_of_week


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

        # Return an object of this model
        return cls(frequency,
                   day_of_week)


