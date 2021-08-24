import json

import pandas as pd
from constants import *


class Summation:
    def __init__(self, start_month: str, start_year: int, end_month: str, end_year: int, save_file: bool):
        """This class will summate the data given in a variety of different
        formats.
        :param start_month: The month where the time span begins (in 3 letter abbreviation) :type start_month: str
        :param start_year: The year where the time span begins (YYYY) :type start_year: int
        :param end_month: The month where the time span ends (in 3 letter abbreviation) :type end_month: str
        :param end_year: The year where the time span ends (YYYY) :type end_year: int
        :param save_file: A boolean that declares whether the output file should be saved or not. :type save_file: bool

        Args:
            start_month (str): The month where the time span begins (in 3 letter abbreviation)
            start_year (int): The year where the time span begins (YYYY)
            end_month (str): The month where the time span ends (in 3 letter abbreviation)
            end_year (int): The year where the time span ends (YYYY)
            save_file (bool): A boolean that declares whether the output file should be saved or not.
        """
        self.start_month = start_month
        self.start_year = start_year
        self.end_month = end_month
        self.end_year = end_year
        self.file_type_preference = OUTPUT_TYPE
        self.output_file = OUTPUT_NAME
        self.output_file_path = OUTPUT_FOLDER
        self.summation_file = SUMMATION_FILE
        self.invalid_titles = ['No Post Available', '']
        self.month_dict = {"Jan": 0, "Feb": 1, "Mar": 2, "Apr": 3, "May": 4,
                           "Jun": 5, "Jul": 6, "Aug": 7, "Sep": 8, "Oct": 9, "Nov": 10, "Dec": 11}
        self.should_save_file = save_file
        self.difference = self.difference_between_dates(
            start_month, start_year, end_month, end_year)
        self.data = self.get_data(self.output_file)
        self.formatted_dataframe = self.create_dataframe()

    @staticmethod
    def get_data(file_name: str):
        """This method gets all of the data from the JSON file and returns it as
        a list.

        Args:
            file_name (str): The path to the file
        """
        with open(file_name, 'r') as f:
            data = json.load(f)
            print(len(data))
        return data

    @staticmethod
    def get_key(val, my_dict):
        """This method returns the key from the dictionary based on the value
        passed into the method.

        Args:
            val (int): The value of the key
            my_dict (dict): The dictionary to be searched

        Returns:
            (str): Returns the string "Key doesn't exist" if the key doesn't
            exist.
        """
        for key, value in my_dict.items():
            if val == value:
                return key
        return "key doesn't exist"

    @staticmethod
    def get_title_table(post: dict) -> tuple:
        """This method returns a tuple object containing the title and the table
        from the post dictionary.

        Args:
            post (dict): The dictionary from the Output File

        Returns:
            tuple: Contains the title and the table of the post.
        """
        title = post['Title']
        table = post['Table']
        return title, table

    def difference_between_dates(self, start_month: str, start_year: int, end_month: str, end_year: int) -> int:
        """Calculate the number of months between two dates.

        Args:
            start_month (str): The start month for Summation
            start_year (int): The start year for Summation
            end_month (str): The end month for Summation
            end_year (int): The end year for Summation

        Returns:
            int: An int representing the number of months between the two dates.
        """
        return (end_year - start_year) * 12 + (self.month_dict[end_month] - self.month_dict[start_month]) + 1

    def create_dataframe(self):
        """This method dynamically creates a dataframe based on the difference
        provided :returns: The dataframe that will be used later on. :rtype:
        pd.DataFrame
        """
        if self.difference < 12:
            cols = ["Article Name", "Total"]
        else:
            cols: list = [y for y in range(self.start_year, self.end_year + 1)]
            cols.insert(0, "Article Name")
        data = {i: [] for i in cols}
        return pd.DataFrame(data)

    def get_months_total(self, row: list, table: pd.DataFrame) -> list:
        """This method calculates the total for the given time span and returns
        it as a list.

        Args:
            row (list): A list containing the title of the post
            table (pd.DataFrame): A dataframe containing the data for the given
                time span

        Returns:
            row (list): A list containing the total views for the given time
            span
        """
        table = pd.DataFrame(table)
        table_col = table.iloc[self.start_year - 2012].T
        total = sum(
            table_col.iloc[month_idx]
            for month_idx in range(
                self.month_dict[self.start_month] + 1,
                self.month_dict[self.end_month] + 2,
            )
        )

        row.append(total)
        return row

    def get_one_year_total(self, row: list, table: pd.DataFrame) -> list:
        """This method calculates the total views for one year scenarios

        Args:
            row (list): The row containing the title of the post.
            table (pd.DataFrame): The table containing the data from the Output
                File

        Returns:
            list: Contains the title name and the total views for the given time
            span.
        """
        table = pd.DataFrame(table)
        start_col = table.iloc[self.start_year - 2012].T
        if self.start_year == self.end_year:
            end_col = table.iloc[self.start_year - 2012].T
        else:
            end_col = table.iloc[self.end_year - 2012].T
        total = sum(
            start_col.iloc[month_idx]
            for month_idx in range(self.month_dict[self.start_month] + 1, 13)
        )

        if self.start_year != self.end_year:
            for month_idx in range(self.month_dict[self.end_month] + 1, 1, -1):
                total += end_col.iloc[month_idx]
        row.append(total)
        return row

    def get_multi_year_total(self, row: list, table: pd.DataFrame) -> list:
        """This method calculates the total views for multiple year scenarios

        Args:
            row (list): The row containing the title of the post.
            table (pd.DataFrame): The table containing the data from the Output
                File

        Returns:
            list: Contains the title name and the total views for the given time
            span.
        """
        total = 0
        table = pd.DataFrame(table)
        for year in range(self.start_year, self.end_year + 1):
            start_col = table.iloc[year - 2012].T
            for month_idx in range(self.month_dict[self.start_month] + 1, 13):
                total += start_col.iloc[month_idx]
            row.append(total)
        return row

    def get_irregular_time_total(self, row: list, table: pd.DataFrame) -> list:
        """This method calculates the total views for multiple year scenarios

        Args:
            row (list): The row containing the title of the post.
            table (pd.DataFrame): The table containing the data from the Output
                File

        Returns:
            list: Contains the title name and the total views for the given time
            span.
        """
        total = 0
        table = pd.DataFrame(table)
        for year in range(self.start_year, self.end_year):
            start_col = table.iloc[year - 2012].T
            if year == self.start_year:
                for month_idx in range(self.month_dict[self.start_month] + 1, 13):
                    total += start_col.iloc[month_idx]
            else:
                for month_idx in range(1, 13):
                    total += start_col.iloc[month_idx]
            row.append(total)
        end_col = table.iloc[self.end_year - 2012].T
        for month_idx in range(self.month_dict[self.end_month] + 1, 1, -1):
            total += end_col.iloc[month_idx]
        row.append(total)
        return row

    def format_data(self) -> pd.DataFrame():
        """This method formats the data into the required format for
        summation.
        """
        for post in self.data:
            title, table = self.get_title_table(post)
            if title not in self.invalid_titles:
                row_data = [title]
                if self.difference < 12:
                    row_data = self.get_months_total(row_data, table)
                elif self.difference % 12 == 0 and self.start_year == self.end_year:
                    row_data = self.get_one_year_total(row_data, table)
                elif self.difference % 12 == 0:
                    row_data = self.get_multi_year_total(row_data, table)
                elif self.difference > 12:
                    row_data = self.get_irregular_time_total(row_data, table)
                self.formatted_dataframe.loc[len(
                    self.formatted_dataframe)] = row_data
        if self.difference < 12:
            self.formatted_dataframe.sort_values(
                by=['Total'], ascending=False, inplace=True)
        else:
            self.formatted_dataframe.sort_values(
                by=[self.start_year], ascending=False, inplace=True)

    def decide_subtraction(self):
        """This method decides when to subtract the data for each of the year columns
        """
        if self.difference >= 12:
            self.subtract_column_values()

    def subtract_column_values(self):
        """This method subtracts the values from the previous year from the
        current year.
        """
        cols = list(self.formatted_dataframe.columns[1:])
        self.formatted_dataframe["{}".format(
            cols[0])] = self.formatted_dataframe[cols[0]]
        for idx in range(len(cols) - 1):
            self.formatted_dataframe["{}".format(cols[idx + 1])] = self.formatted_dataframe[cols[idx + 1]] - \
                self.formatted_dataframe[
                cols[idx]]
        self.formatted_dataframe.drop(self.formatted_dataframe.columns[1:int(
            ((-len(self.formatted_dataframe.columns))+1)/2)], axis=1, inplace=True)
        self.formatted_dataframe.reset_index(drop=True, inplace=True)

    def save_file(self) -> None:
        """This method saves the data into a file based on the file type."""
        if self.file_type_preference == "csv":
            self.summation_file += '.{}'.format(
                self.file_type_preference.lower())
            self.formatted_dataframe.to_csv(self.summation_file)
        elif self.file_type_preference == "json":
            self.summation_file += '.{}'.format(
                self.file_type_preference.lower())
            with open(self.summation_file, 'w') as f:
                json.dump(self.formatted_dataframe.to_dict(
                    orient='records'), f, indent=4)
        elif self.file_type_preference == "excel":
            self.summation_file += '.xlsx'
            self.formatted_dataframe.to_excel(self.summation_file)
        else:
            raise ValueError("Output type not supported or incorrect format.")
        print("Saved at {}".format(self.summation_file))

    def main(self):
        """This method is the main method that runs the program."""
        self.format_data()
        self.decide_subtraction()
        if self.should_save_file:
            self.save_file()


if __name__ == '__main__':
    summation = Summation('Jan', 2012, 'Dec', 2020, True)
    summation.main()
