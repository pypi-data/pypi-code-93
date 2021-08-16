from typing import Optional, NoReturn
import random, string, time

def string_an(len: int) -> str:
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=len))

def sleep(
    min_s: float,
    max_s: Optional[float] = None,
    max_deviation_perc: Optional[float] = None
) -> NoReturn:
    multi = 1000.0
    sleep_s = min_s

    if max_s is not None and max_s > 0:
        if max_s < min_s:
            _min_s = min_s
            min_s = max_s
            max_s = min_s

        sleep_s = float(random.randint(int(min_s*multi), int(max_s*multi)))/multi

    if max_deviation_perc is not None and max_deviation_perc > 0:
        deviation_perc = random.randint(int(-1*max_deviation_perc*multi), int(max_deviation_perc*multi))/multi

        sleep_s += sleep_s*deviation_perc/100

    time.sleep(sleep_s)