import datetime
from enum import Enum


class PeriodicityTypes(str, Enum):
    annual = 'Annual'
    semiannual = 'SemiAnnual'
    yearly_ending_jan = 'Yearly Ending Jan'
    yearly_ending_feb = 'Yearly Ending Feb'
    yearly_ending_mar = 'Yearly Ending Mar'
    yearly_ending_apr = 'Yearly Ending Apr'
    yearly_ending_may = 'Yearly Ending May'
    yearly_ending_jun = 'Yearly Ending Jun'
    yearly_ending_jul = 'Yearly Ending Jul'
    yearly_ending_aug = 'Yearly Ending Aug'
    yearly_ending_sep = 'Yearly Ending Sep'
    yearly_ending_oct = 'Yearly Ending Oct'
    yearly_ending_nov = 'Yearly Ending Nov'
    yearly_ending_dec = 'Yearly Ending Dec'
    quarterly = 'Quarterly'
    monthly = 'Monthly'
    weekly = 'Weekly'
    weekly_ending_monday = 'Weekly Ending Monday'
    weekly_ending_tuesday = 'Weekly Ending Tuesday'
    weekly_ending_wednesday = 'Weekly Ending Wednesday'
    weekly_ending_thursday = 'Weekly Ending Thursday'
    weekly_ending_friday = 'Weekly Ending Friday'
    weekly_ending_saturday = 'Weekly Ending Saturday'
    weekly_ending_sunday = 'Weekly Ending Sunday'
    daily = 'Daily'
    custom = 'Custom'


VALUES_UPDATE_DATE_FORMAT = '%Y-%m-%d'
DEFAULT_DATE = datetime.datetime(1900, 1, 1)

NA_FIELD = 'NA'
