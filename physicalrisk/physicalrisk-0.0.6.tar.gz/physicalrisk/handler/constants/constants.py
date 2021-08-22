from datetime import datetime

# for plotters
PLOT = False
FIGSIZE = (12, 9)

# for date
FIRST_HISTORICAL_FLOOD_DATE = datetime(1961, 1, 1)
MIN_DATE = datetime(1961, 1, 1)
MAX_DATE = datetime(2018, 12, 31)
FUTURE_MONTH = 0  # January
DAYS_ROLLBACK = 40  # total days are 41, 40+start_date

# for location:
BOUNDS_LONDON = [[-1, 51], [1, 52]]  # greater London
BOUNDS_UK = [[-8.4, 49.8], [1.9, 58.8]]  # UK incl. Northern Ireland

# for raster
RESOLUTION = 2.5
RADIUS = 1
