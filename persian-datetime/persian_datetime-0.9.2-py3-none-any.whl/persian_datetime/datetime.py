import datetime
from enum import Enum

from rest_framework import serializers


class Jalali:
	def __init__(self, datetime_value: datetime.datetime):
		self.datetime_value = datetime_value

	class WeekDays(Enum):
		Saturday = 'شنبه',
		Sunday = 'یکشنبه',
		Monday = 'دوشنبه',
		Tuesday = 'سه شنبه',
		Wednesday = 'چهارشنبه',
		Thursday = 'پنجشنبه',
		Friday = 'جمعه',


	class JalaliSerializer(serializers.BaseSerializer):
		def to_representation(self, instance):
			return {
				'date': instance.datetime_value.strftime("%Y-%m-%d"),
				'jalali_date': instance.gregorian_to_jalali(return_str=True),
				'jalali_day': instance.jalali_weekday,
			}

	@property
	def jalali_weekday(self):
		return Jalali.WeekDays[self.datetime_value.strftime('%A')].value[0]

	def gregorian_to_jalali(self, return_str=False, splitter='/'):
		gy, gm, gd = self.datetime_value.year, self.datetime_value.month, self.datetime_value.day

		g_d_m = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]
		if gy > 1600:
			jy = 979
			gy -= 1600
		else:
			jy = 0
			gy -= 621
		if gm > 2:
			gy2 = gy + 1
		else:
			gy2 = gy
		days = (365 * gy) + (int((gy2 + 3) / 4)) - (int((gy2 + 99) / 100)) + (int((gy2 + 399) / 400)) - 80 + gd + g_d_m[
			gm - 1]
		jy += 33 * (int(days / 12053))
		days %= 12053
		jy += 4 * (int(days / 1461))
		days %= 1461
		if days > 365:
			jy += int((days - 1) / 365)
			days = (days - 1) % 365
		if days < 186:
			jm = 1 + int(days / 31)
			jd = 1 + (days % 31)
		else:
			jm = 7 + int((days - 186) / 30)
			jd = 1 + ((days - 186) % 30)
		if return_str:
			return f'{jy}{splitter}{jm:02d}{splitter}{jd:02d}'
		return jy, jm, jd

	def date_diff_to_str_persian(self):
		"""
		mohasebeye ekhtelafe zamanie hal ba datetime_value va khorooji ba matne farsi
		:return:
		"""
		delta = datetime.datetime.now() - self.datetime_value
		if delta.days <= 0:
			if delta.seconds // 3600 >= 1:
				return f'{delta.seconds // 3600} ساعت قبل'
			else:
				return 'لحظاتی قبل'
		elif delta.days // 365 >= 1:
			return f'{delta.days // 365} سال قبل'
		elif delta.days // 30 >= 1:
			return f'{delta.days // 30} ماه قبل'
		else:
			return f'{delta.days} روز قبل'

	def first_day_of_jalali_week(self) -> datetime.date:
		jy, jm, jd = self.gregorian_to_jalali()
		return Jalali.first_daY_of_jalali_week(jalali_year=jy, jalali_month=jm, jalali_day=jd)

	def last_day_of_jalali_week(self) -> datetime.date:
		jy, jm, jd = self.gregorian_to_jalali()
		return Jalali.last_daY_of_jalali_week(jalali_year=jy, jalali_month=jm, jalali_day=jd)

	@staticmethod
	def jalali_to_gregorian(jy=0, jm=0, jd=0, return_datetime=False, jalali_date: str = None, splitter='/') -> datetime.date:
		if jalali_date is not None:
			jy, jm, jd = map(int, jalali_date.split(splitter))

		if jy > 979:
			gy = 1600
			jy -= 979
		else:
			gy = 621
		if jm < 7:
			days = (jm - 1) * 31
		else:
			days = ((jm - 7) * 30) + 186
		days += (365 * jy) + ((int(jy / 33)) * 8) + (int(((jy % 33) + 3) / 4)) + 78 + jd
		gy += 400 * (int(days / 146097))
		days %= 146097
		if days > 36524:
			gy += 100 * (int(--days / 36524))
			days %= 36524
			if days >= 365:
				days += 1
		gy += 4 * (int(days / 1461))
		days %= 1461
		if days > 365:
			gy += int((days - 1) / 365)
			days = (days - 1) % 365
		gd = days + 1
		if (gy % 4 == 0 and gy % 100 != 0) or (gy % 400 == 0):
			kab = 29
		else:
			kab = 28
		sal_a = [0, 31, kab, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
		gm = 0
		while gm < 13:
			v = sal_a[gm]
			if gd <= v:
				break
			gd -= v
			gm += 1

		if return_datetime:
			return datetime.date(gy, gm, gd)
		return gy, gm, gd

	@staticmethod
	def is_kabise(jalali_year: int) -> bool:
		"""
		check kardane boodane sale kabise

		:param jalali_year: sal be shamsi ex : 1398
		:return: kabise ast -> True , kabise nist -> False
		"""
		d = (jalali_year + 621) % 4
		if d == 0:
			return True
		return False

	@staticmethod
	def number_of_days_of_jalali_month(jalali_year: int, jalali_month: int):
		if 1 <= jalali_month <= 6:
			return 31
		if 7 <= jalali_month <= 11:
			return 30
		if jalali_month == 12:
			if Jalali.is_kabise(jalali_year=jalali_year):
				return 30
			else:
				return 29
		return False

	@staticmethod
	def first_day_of_jalali_month(jalali_year: int, jalali_month: int) -> datetime.date:
		"""
		:param jalali_year: year in jalali => 1398
		:param jalali_month: month in jalali -> 5
		:return: gregorian date for first day of a specific jalali month
		"""
		return Jalali.jalali_to_gregorian(jy=jalali_year, jm=jalali_month, jd=1, return_datetime=True)

	@staticmethod
	def last_day_of_jalali_month(jalali_year: int, jalali_month: int) -> datetime.date:
		"""
		:param jalali_year: year in jalali => 1398
		:param jalali_month: month in jalali -> 5
		:return: gregorian date for last day of a specific jalali month
		"""
		return Jalali.jalali_to_gregorian(jy=jalali_year, jm=jalali_month,
		                                  jd=Jalali.number_of_days_of_jalali_month(jalali_year=jalali_year,
		                                                                           jalali_month=jalali_month),
		                                  return_datetime=True)

	@staticmethod
	def first_day_of_this_jalali_month() -> datetime.date:
		jy, jm, jd = Jalali(datetime_value=datetime.datetime.today()).gregorian_to_jalali()
		return Jalali.first_day_of_jalali_month(jalali_year=jy, jalali_month=jm)

	@staticmethod
	def last_day_of_this_jalali_month() -> datetime.date:
		jy, jm, jd = Jalali(datetime_value=datetime.datetime.today()).gregorian_to_jalali()
		return Jalali.last_day_of_jalali_month(jalali_year=jy, jalali_month=jm)

	@staticmethod
	def first_daY_of_jalali_week(jalali_year: int, jalali_month: int, jalali_day: int) -> datetime.date:
		"""
		:param jalali_year: year in jalali => 1398
		:param jalali_month: month in jalali -> 5
		:param jalali_month: day in jalali -> 3 (shanbe : 1, jome : 7)
		:return: gregorian date for first day of a specific jalali week
		"""
		gregorian_date = Jalali.jalali_to_gregorian(jy=jalali_year, jm=jalali_month, jd=jalali_day, return_datetime=True)
		if gregorian_date.isoweekday() == 6:
			return gregorian_date
		if gregorian_date.isoweekday() == 7:
			return gregorian_date - datetime.timedelta(days=1)
		return gregorian_date - datetime.timedelta(days=gregorian_date.isoweekday()+1)

	@staticmethod
	def last_daY_of_jalali_week(jalali_year: int, jalali_month: int, jalali_day: int) -> datetime.date:
		"""
		:param jalali_year: year in jalali => 1398
		:param jalali_month: month in jalali -> 5
		:param jalali_month: day in jalali -> 3 (shanbe : 1, jome : 7)
		:return: gregorian date for last day of a specific jalali week
		"""
		gregorian_date = Jalali.jalali_to_gregorian(jy=jalali_year, jm=jalali_month, jd=jalali_day, return_datetime=True)
		if gregorian_date.isoweekday() == 6:
			return gregorian_date + datetime.timedelta(days=6)
		if gregorian_date.isoweekday() == 7:
			return gregorian_date + datetime.timedelta(days=5)
		return gregorian_date + datetime.timedelta(days=5-gregorian_date.isoweekday())

	@staticmethod
	def first_day_of_this_jalali_week() -> datetime.date:
		jy, jm, jd = Jalali(datetime_value=datetime.datetime.today()).gregorian_to_jalali()
		return Jalali.first_daY_of_jalali_week(jalali_year=jy, jalali_month=jm, jalali_day=jd)

	@staticmethod
	def last_day_of_this_jalali_week() -> datetime.date:
		jy, jm, jd = Jalali(datetime_value=datetime.datetime.today()).gregorian_to_jalali()
		return Jalali.last_daY_of_jalali_week(jalali_year=jy, jalali_month=jm, jalali_day=jd)
