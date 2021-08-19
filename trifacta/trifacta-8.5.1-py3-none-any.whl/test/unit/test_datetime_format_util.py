from trifacta.util.datetime_formatting_util import DateTimeFormattingUtil
import unittest
from trifacta.transform_functions.function_definitions import ParseDate, DateTimeFormat, ToTime, unix_time, \
    ConvertTimeZone, UnixTimeFormat, day_of_week, DateDiff, DateAdd, serial_number, eo_month, work_day_intl, net_work_day_intl
import datetime


class DateTimeUtilTestCase(unittest.TestCase):

    def test_translate_format_with_delimiter(self):
        obj = DateTimeFormattingUtil.get_instance()
        self.assertEqual(obj.translate('yyyy-MM-dd HH:mm:ss', mode='format'), '%Y-%m-%d %H:%M:%S')
        self.assertEqual(obj.translate('MMMM d, yyyy', mode='format'), '%B %-d, %Y')
        self.assertEqual(obj.translate('MM/dd/yy', mode='format'), '%m/%d/%y')
        self.assertEqual(obj.translate('M/dd/yy', mode='format'), '%m/%d/%y')
        self.assertEqual(obj.translate('dd/MM/yy', mode='format'), '%d/%m/%y')
        self.assertEqual(obj.translate('yyyy/MM/dd', mode='format'), '%Y/%m/%d')
        self.assertEqual(obj.translate('dd.MMM.yyyy', mode='format'), '%d.%b.%Y')
        self.assertEqual(obj.translate('MMM dd yyyy HH.mm.ss xxx', mode='format'), '%b %d %Y %H.%M.%S %z')
        self.assertEqual(obj.translate('MMM dd yyyy hh.mm.ss xxx', mode='format'), '%b %d %Y %I.%M.%S %z')

    def test_translate_format_without_delimiter(self):
        obj = DateTimeFormattingUtil.get_instance()
        self.assertEqual(obj.translate('yyyyMMddHHmmss', mode='format'), '%Y%m%d%H%M%S')
        self.assertEqual(obj.translate('MMMMdyyyy', mode='format'), '%B%-d%Y')
        self.assertEqual(obj.translate('MMddyy', mode='format'), '%m%d%y')
        self.assertEqual(obj.translate('Mddyy', mode='format'), '%m%d%y')
        self.assertEqual(obj.translate('ddMMyy', mode='format'), '%d%m%y')
        self.assertEqual(obj.translate('yyyyMMdd', mode='format'), '%Y%m%d')
        self.assertEqual(obj.translate('ddMMMyyyy', mode='format'), '%d%b%Y')
        self.assertEqual(obj.translate('MMMddyyyyHHmmssxxx', mode='format'), '%b%d%Y%H%M%S%z')

    def test_zero_padding_formatting(self):
        obj = DateTimeFormattingUtil.get_instance()
        date_str = '11/12/2015 06:23:12'
        f_str = 'dd/MM/yyyy HH:mm:ss'
        self.assertEqual(obj.strftime(obj.strptime(date_str, f_str), f_str), date_str)

    def test_translation_string(self):
        obj = DateTimeFormattingUtil.get_instance()
        date_str = '11/12/2015 06:23:12'
        f_str = 'dd/MM/yyyy HH:mm:ss'
        self.assertEqual(obj.strftime(obj.strptime(date_str, f_str), f_str), date_str)
        date_str = '1.12.2015 06:23 AM'
        f_str = 'd.MM.yyyy HH:mm a'
        self.assertEqual(obj.strftime(obj.strptime(date_str, f_str), f_str), date_str)

    def test_datetime_parsing(self):
        pass

    def test_datetime_formatting(self):
        pass

    def test_parse_date(self):
        parsedate1 = ParseDate('MMMM d, yyyy', 'MM/dd/yy', 'M/dd/yy', 'dd/MM/yy', 'yyyy/MM/dd', 'dd.MMM.yyyy',
                               'MMM dd yyyy HH.mm.ss xxx')
        datetimeformat1 = DateTimeFormat("yyyy-MM-dd'T'HH:mm:ss.SSS")
        datetimeformat2 = DateTimeFormat("yyyy-MM-dd'T'HH:mm:ss")
        self.assertEqual(datetimeformat2.exec(
            parsedate1.exec("April 24, 2019")), "2019-04-24T00:00:00")
        self.assertEqual(datetimeformat1.exec(
            parsedate1.exec("April 24, 2019")), "2019-04-24T00:00:00.000")
        self.assertEqual(datetimeformat1.exec(
            parsedate1.exec("May 5, 2019")), "2019-05-05T00:00:00.000")
        self.assertEqual(datetimeformat1.exec(
            parsedate1.exec("29.Feb.2016")), "2016-02-29T00:00:00.000")
        self.assertEqual(datetimeformat1.exec(
            parsedate1.exec("1/02/90")), "1990-01-02T00:00:00.000")
        self.assertEqual(datetimeformat1.exec(
            parsedate1.exec("30/01/90")), "1990-01-30T00:00:00.000")
        self.assertEqual(datetimeformat1.exec(
            parsedate1.exec("2011/01/15")), "2011-01-15T00:00:00.000")
        self.assertEqual(datetimeformat1.exec(
            parsedate1.exec("03/04/05")), "2005-03-04T00:00:00.000")
        self.assertEqual(datetimeformat1.exec(
            parsedate1.exec("Jan 14 1996 10.30.00 +00:00")), "1996-01-14T10:30:00.000")
        self.assertEqual(datetimeformat1.exec(
            parsedate1.exec("September 24, 2019")), "2019-09-24T00:00:00.000")

    def test_unix_time(self):
        totime2 = ToTime('M / d / yyyy')
        self.assertEqual(unix_time(totime2.exec("09 / 17 / 2015")), 1442448000)
        self.assertEqual(unix_time(totime2.exec("02 / 04 / 2010")), 1265241600)
        self.assertEqual(unix_time(totime2.exec("11 / 07 / 2013")), 1383782400)

    def test_convert_time_zone(self):
        convertTimeZone1 = ConvertTimeZone('UTC', 'Asia/Calcutta')
        datetimeformat1 = DateTimeFormat("yyyy-MM-dd HH:mm:ss")
        totime1 = ToTime('dd-MM-yyyy HH:mm:ss.SSS')
        self.assertEqual(datetimeformat1.exec(
            convertTimeZone1.exec(totime1.exec("21-01-2011 12:24:43.456"))), "2011-01-21 17:54:43")

    def test_day_of_week(self):
        totime2 = ToTime('M / d / yyyy')
        self.assertEqual(day_of_week(totime2.exec("01 / 21 / 2011")), 5)
        self.assertEqual(day_of_week(totime2.exec("09 / 17 / 2015")), 4)
        self.assertEqual(day_of_week(totime2.exec("11 / 07 / 2013")), 4)
        self.assertEqual(day_of_week(totime2.exec("08 / 23 / 1999")), 1)

    def test_date_add(self):
        totime2 = ToTime('M / d / yyyy')
        self.assertEqual(DateAdd('year').exec(totime2.exec("01 / 21 / 2011"), 1),
                         datetime.datetime(2012, 1, 21, 0, 0))
        self.assertEqual(DateAdd('month').exec(totime2.exec("01 / 21 / 2011"), 1),
                         datetime.datetime(2011, 2, 21, 0, 0))
        self.assertEqual(DateAdd('week').exec(totime2.exec("01 / 21 / 2011"), 1),
                         datetime.datetime(2011, 1, 28, 0, 0))
        self.assertEqual(DateAdd('day').exec(totime2.exec("01 / 21 / 2011"), 1),
                         datetime.datetime(2011, 1, 22, 0, 0))
        self.assertEqual(DateAdd('hour').exec(totime2.exec("01 / 21 / 2011"), 1),
                         datetime.datetime(2011, 1, 21, 1, 0))
        self.assertEqual(DateAdd('minute').exec(totime2.exec("01 / 21 / 2011"), 1),
                         datetime.datetime(2011, 1, 21, 0, 1))
        self.assertEqual(DateAdd('second').exec(totime2.exec("01 / 21 / 2011"), 1),
                         datetime.datetime(2011, 1, 21, 0, 0, 1))
        self.assertEqual(DateAdd('millisecond').exec(totime2.exec("01 / 21 / 2011"), 1),
                         datetime.datetime(2011, 1, 21, 0, 0, 0, 1000))

    def test_date_diff(self):
        self.assertEqual(
            DateDiff('year').exec(datetime.datetime(2011, 1, 21, 0, 0),
                                  datetime.datetime(2012, 1, 21, 0, 0)), 1)
        self.assertEqual(
            DateDiff('month').exec(datetime.datetime(2011, 1, 21, 0, 0),
                                   datetime.datetime(2011, 2, 21, 0, 0)), 1)
        self.assertEqual(
            DateDiff('week').exec(datetime.datetime(2011, 1, 21, 0, 0),
                                  datetime.datetime(2011, 1, 28, 0, 0)), 1)
        self.assertEqual(
            DateDiff('day').exec(datetime.datetime(2011, 1, 21, 0, 0),
                                 datetime.datetime(2011, 1, 22, 0, 0)), 1)
        self.assertEqual(
            DateDiff('hour').exec(datetime.datetime(2011, 1, 21, 0, 0),
                                  datetime.datetime(2011, 1, 21, 1, 0)), 1)
        self.assertEqual(
            DateDiff('minute').exec(datetime.datetime(2011, 1, 21, 0, 0),
                                    datetime.datetime(2011, 1, 21, 0, 1)), 1)
        self.assertEqual(
            DateDiff('second').exec(datetime.datetime(2021, 3, 17, 11, 21, 33, 579216),
                                    datetime.datetime(2021, 3, 17, 11, 21, 43, 46349)), 9)
        self.assertEqual(
            DateDiff('millisecond').exec(datetime.datetime(2021, 3, 17, 11, 21, 33, 579216),
                                         datetime.datetime(2021, 3, 17, 11, 21, 43, 46349)), 467)

    def test_workdayintl(self):
        holiday_list = ['2020-01-28', '2020-01-27', '2020-01-26', '2020-01-26']
        self.assertEqual(work_day_intl(datetime.datetime(2020, 1, 29),
                                          -10,
                                          '0111111',
                                          holiday_list),
                         datetime.datetime(2019, 11, 18, 0, 0))
        self.assertEqual(work_day_intl(datetime.datetime(2020, 1, 25),
                                          2,
                                          '0111111',
                                          holiday_list),
                         datetime.datetime(2020, 2, 10, 0, 0))
        self.assertEqual(work_day_intl(datetime.datetime(2020, 1, 25),
                                          2,
                                          '0000011',
                                          holiday_list),
                         datetime.datetime(2020, 1, 30, 0, 0))
        self.assertEqual(work_day_intl(datetime.datetime(2020, 1, 25),
                                          2,
                                          '0000011',
                                          holiday_list),
                         datetime.datetime(2020, 1, 30, 0, 0))
        self.assertEqual(work_day_intl(datetime.datetime(2020, 1, 1),
                                          -360,
                                          '0011000'),
                         datetime.datetime(2018, 8, 17, 0, 0))
        self.assertEqual(work_day_intl(datetime.datetime(2020, 1, 1),
                                          365,
                                          '0000000'),
                         datetime.datetime(2020, 12, 31))
        self.assertEqual(work_day_intl(datetime.datetime(2020, 1, 25),
                                          2,
                                          '0000011',
                                          holiday_list),
                         datetime.datetime(2020, 1, 30))

        pass

    def test_networkdayintl(self):
        holiday_list = ['2020-02-02', '2020-02-02', '2020-01-29', '2020-03-01', '2020-02-01']
        sample_holiday_list = ['2020-01-28', '2020-01-27', '2020-01-26', '2020-01-26']
        self.assertEqual(net_work_day_intl(
            datetime.datetime(2020, 1, 26), datetime.datetime(2020, 2, 2), '1111111', sample_holiday_list), 0)
        self.assertEqual(net_work_day_intl(
            datetime.datetime(2020, 1, 26), datetime.datetime(2020, 2, 2), '0000000'), 8)
        self.assertEqual(net_work_day_intl(
            datetime.datetime(2020, 1, 30), datetime.datetime(2020, 2, 6), '0000011', sample_holiday_list), 6)
        self.assertEqual(net_work_day_intl(
            datetime.datetime(2020, 1, 26), datetime.datetime(2020, 2, 2), '0000110'), 6)
        self.assertEqual(net_work_day_intl(
            datetime.datetime(2020, 1, 24), datetime.datetime(2020, 1, 31), '1000000'), 7)
        self.assertEqual(net_work_day_intl(
            datetime.datetime(2020, 1, 26), datetime.datetime(2020, 2, 2), '0000011', sample_holiday_list), 3)
        self.assertEqual(net_work_day_intl(
            datetime.datetime(2020, 1, 25), datetime.datetime(2020, 2, 8), '0000011'), 10)
        self.assertEqual(net_work_day_intl(
            datetime.datetime(2018, 12, 1), datetime.datetime(2020, 1, 1), '0000011'), 283)
        self.assertEqual(net_work_day_intl(
            datetime.datetime(2019, 12, 1), datetime.datetime(2020, 1, 1), '0011000'), 23)
        self.assertEqual(net_work_day_intl(
            datetime.datetime(2011, 2, 1), datetime.datetime(2020, 2, 1), '0000011'), 2349)
        self.assertEqual(net_work_day_intl(
            datetime.datetime(2020, 2, 2), datetime.datetime(2020, 1, 26)), None)
        self.assertEqual(net_work_day_intl(
            datetime.datetime(2020, 1, 26), datetime.datetime(2020, 2, 3), '0000000', holiday_list), 6)

    def test_datetime_serial_number(self):
        self.assertEqual(serial_number(datetime.datetime(2020, 2, 1)), 43862)
        self.assertEqual(serial_number(datetime.datetime(1995, 8, 24)), 34935)
        self.assertEqual(serial_number(datetime.datetime(2002, 12, 1)), 37591)
        self.assertEqual(serial_number(datetime.datetime(2020, 5, 29)), 43980)
        self.assertEqual(serial_number(datetime.datetime(1947, 8, 15)), 17394)
        self.assertEqual(serial_number(datetime.datetime(1970, 1, 1)), 25569)
        self.assertEqual(serial_number(datetime.datetime(2017, 7, 24)), 42940)
        self.assertEqual(serial_number(datetime.datetime(2013, 9, 21)), 41538)
        self.assertEqual(serial_number(datetime.datetime(1969, 4, 29)), 25322)
        self.assertEqual(serial_number(datetime.datetime(1980, 11, 10)), 29535)
        self.assertEqual(serial_number(datetime.datetime(1880, 8, 21)), None)
        self.assertEqual(serial_number(datetime.datetime(1945, 9, 2)), 16682)
        self.assertEqual(serial_number(datetime.datetime(2100, 8, 21)), 73283)
        self.assertEqual(serial_number(datetime.datetime(2900, 12, 31)), 365609)
        self.assertEqual(serial_number(datetime.datetime(1907, 12, 4, 2, 48, 21)), 2895)
        self.assertEqual(serial_number(datetime.datetime(1970, 1, 1, 0, 0, 0)), 25569)
        self.assertEqual(serial_number(datetime.datetime(1980, 11, 10, 0, 0, 12)), 29535)
        self.assertEqual(serial_number(None), None)

    def test_eo_month(self):
        self.assertEqual(eo_month(datetime.datetime(2020, 2, 1), 3), 43982)
        self.assertEqual(eo_month(datetime.datetime(2020, 1, 26), 1), 43890)
        self.assertEqual(eo_month(datetime.datetime(2019, 4, 13), 13), 43982)
        self.assertEqual(eo_month(datetime.datetime(1947, 8, 15), 200), 23497)
        self.assertEqual(eo_month(datetime.datetime(2100, 10, 3), 10000), 377721)
        self.assertEqual(eo_month(datetime.datetime(2010, 11, 14), 0), 40512)
        self.assertEqual(eo_month(datetime.datetime(1990, 12, 3), 20000), 641976)
        self.assertEqual(eo_month(datetime.datetime(1900, 1, 1), 10), 335)
        self.assertEqual(eo_month(datetime.datetime(2020, 6, 15), 0), 44012)
        self.assertEqual(eo_month(datetime.datetime(2020, 6, 15), 3), 44104)
        self.assertEqual(eo_month(datetime.datetime(2020, 6, 15), 6), 44196)
        self.assertEqual(eo_month(datetime.datetime(2020, 6, 15), 18), 44561)
        self.assertEqual(eo_month(datetime.datetime(2020, 6, 15), 1), 44043)
        self.assertEqual(eo_month(datetime.datetime(1800, 2, 21), 7), None)
        self.assertEqual(eo_month(datetime.datetime(2001, 6, 3), -6), 36891)
        self.assertEqual(eo_month(datetime.datetime(2100, 8, 21), -1000), 42855)
        self.assertEqual(eo_month(datetime.datetime(2020, 6, 15), -24), 43281)
        self.assertEqual(eo_month(datetime.datetime(2020, 6, 15), -18), 43465)
        self.assertEqual(eo_month(datetime.datetime(2020, 6, 15), -6), 43830)
        self.assertEqual(eo_month(datetime.datetime(2020, 6, 15), -3), 43921)
        self.assertEqual(eo_month(None, 4), None)

    def test_unix_time_format(self):
        epoch = 0
        time = 1420039740000
        bctime = -63500000000000

        self.assertEqual(UnixTimeFormat().exec(epoch), None)
        self.assertEqual(UnixTimeFormat().exec(None), None)

        self.assertEqual(UnixTimeFormat('yyMMdd').exec(None), None)

        # case of empty format string
        self.assertEqual(UnixTimeFormat('').exec(epoch), '700101')
        self.assertEqual(UnixTimeFormat('').exec(time), '141231')

        self.assertEqual(UnixTimeFormat('MM/dd/yyyy').exec(epoch), '01/01/1970')
        self.assertEqual(UnixTimeFormat('MM/dd/yyyy').exec(time), '12/31/2014')

        # self.assertEqual(UnixTimeFormat("'Time': MMM-dd-yyyy(G), KK:mm:ss.SSS a EEE xxx --- ").exec(epoch),
        #                  "Time: Jan-01-1970(AD), 00:00:00.000 AM Thu +00:00 --- ")
        # self.assertEqual(UnixTimeFormat("'Time': MMM-dd-yyyy(G), KK:mm:ss.SSS a EEE xxx --- ").exec(epoch),
        #                  "Time: Dec-31-2014(AD), 03:29:00.000 PM Wed +00:00 --- ")
        # self.assertEqual(UnixTimeFormat("'Time': MMM-dd-yyyy(G), KK:mm:ss.SSS a EEE xxx --- ").exec(epoch),
        #                  "Time: Oct-09-0044(BC), 07:06:40.000 AM Mon +00:00 --- ")

        # self.assertEqual(UnixTimeFormat("k 'hours', m 'minutes' 'and' s 'seconds' ---'!'").exec(time),
        #                  '15 hours, 29 minutes and 0 seconds ---!')

    if __name__ == '__main__':
        unittest.main()
