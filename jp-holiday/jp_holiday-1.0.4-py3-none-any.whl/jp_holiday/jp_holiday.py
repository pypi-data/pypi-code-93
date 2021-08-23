import datetime
import jpholiday

def is_holiday(df, day_column_name, holiday_colum_name="holiday"):
    """
    df[day_column_name] = "YYYY.MM.DD.*"

    ex1. 2021-01-01 01:01:01
    ex2. 2021~01~01 01-01-01
    ex3. 2021 01 01 01 01
    ex4. 2021@01@01
    ex5.  2021001001 hogehoge

    return df

    """

    def convert(day):
        day_str = str(day)
        date = datetime.date(int(day_str[0:4]), int(day_str[5:7]), int(day_str[8:11]))
        return True if (date.weekday() >= 5 or jpholiday.is_holiday(date)) else False

    df_day = df[day_column_name]

    df[holiday_colum_name] = df_day.apply(convert)

    return df
