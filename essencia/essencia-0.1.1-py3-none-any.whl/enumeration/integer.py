'''Integer type enumerations'''

from essencia.enumeration.abstract import BaseIntEnum

# __all__=[
#     'PaymentStatus',
#     'Cost',
#     'Response',
#     'Tolerability',
#     'Valence',
#     'Arousal',
#     'Intensity',
#     'Week'
# ]


class PaymentStatus(BaseIntEnum):
    Debit = -1
    Finished = 0
    Credit = 1

class Cost(BaseIntEnum):
    VeryLow = -2
    Low = -1
    Undefined = 0
    High = 1
    VeryHigh = 2

class Response(BaseIntEnum):
    VeryLow = -2
    Low = -1
    Undefined = 0
    High = 1
    VeryHigh = 2

class Tolerability(BaseIntEnum):
    VeryLow = -2
    Low = -1
    Undefined = 0
    High = 1
    VeryHigh = 2

class Valence(BaseIntEnum):
    VeryNegative = -2
    Negative = -1
    Neutral = 0
    Positive = 1
    VeryPositive = 2

class Arousal(BaseIntEnum):
    VeryReduced = -2
    Reduced = -1
    Neutral = 0
    Increased = 1
    VeryIncreased = 2

class Intensity(BaseIntEnum):
    Absent = 0
    Minimal = 1
    Mild = 2
    Moderate = 3
    Severe = 4
    Extreme = 5

class Week(BaseIntEnum):
    Zero = 0
    One = 1
    Two = 2
    Three = 3
    Four = 4
    Five = 5
    Six = 6
    Seven = 7
    Eight = 8
    Nine = 9
    Ten = 10
    Eleven = 11
    Twelve = 12

