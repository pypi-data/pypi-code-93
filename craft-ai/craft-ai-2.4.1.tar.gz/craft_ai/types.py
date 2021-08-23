TYPES = {
    "continuous": "continuous",
    "enum": "enum",
    "boolean": "boolean",
    "timezone": "timezone",
    "time_of_day": "time_of_day",
    "day_of_week": "day_of_week",
    "day_of_month": "day_of_month",
    "month_of_year": "month_of_year",
}

TYPE_ANY = "any"

GENERATED_TIME_TYPES = [
    TYPES["time_of_day"],
    TYPES["day_of_week"],
    TYPES["day_of_month"],
    TYPES["month_of_year"],
]
