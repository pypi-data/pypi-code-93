from time import time

from Assets.Summation.summation import Summation


class SummationMain:
    def __init__(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date
        self.difference = self.difference_between_dates(
            self.start_date, self.end_date)
        self.month_dict = {"Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5,
                           "Jun": 6, "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12}

    @staticmethod
    def get_key(val, my_dict):
        """This method returns the key from the dictionary based on the value passed into the method.

        Args:
            val (int): The value of the key
            my_dict (dict): The dictionary to be searched

        Returns:
            (str): Returns the string "Key doesn't exist" if the key doesn't exist.
        """
        for key, value in my_dict.items():
            if val == value:
                return key
        return "key doesn't exist"

    @staticmethod
    def difference_between_dates(start_date, end_date) -> int:
        """Calculate the number of months between two dates.

        Args:
            start_date: A datetime.date object.
            end_date: A datetime.date object.

        Returns:
            An int representing the number of months between the two dates.
        """
        return (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)

    def main(self):
        """Main method.
        """
        program_start_time = time()
        summation_inst = Summation(self.get_key(self.start_date.month, self.month_dict), self.start_date.year,
                                   self.get_key(self.end_date.month, self.month_dict), self.end_date.year, True)
        summation_inst.main()
        program_end_time = time()
        print("Summation program took {} seconds to execute.".format(
            program_end_time - program_start_time))


if __name__ == '__main__':
    from dateutil import parser

    start_time = time()
    summation_main_inst = SummationMain(parser.parse(
        "04/01/2012"), parser.parse("06/30/2020"))
    summation_main_inst.main()
    end_time = time()
    print("Summation program took {} seconds to execute.".format(
        end_time - start_time))
