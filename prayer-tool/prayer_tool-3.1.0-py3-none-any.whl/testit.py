from prayer_tool import prayer_times
import datetime

#Declaring an instance
instance = prayer_times.PrayerTimes(city="Paris")

#The datetime objects we need
start = datetime.datetime(year = 2021, month = 8, day = 23)
end = datetime.datetime(year = 2021, month = 8, day = 26)

#Call the function and save the result
result = instance.get_date(start, end)

for item in result:
    print(item.__str__() + "\n")

