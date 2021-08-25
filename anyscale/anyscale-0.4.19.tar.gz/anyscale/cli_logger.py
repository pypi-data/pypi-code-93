import os
import sys
import time

import colorama  # type: ignore


class _CliLogger:
    def __init__(self) -> None:
        self.t0 = time.time()

    def zero_time(self) -> None:
        self.t0 = time.time()

    def info(self, *msg: str) -> None:
        print(
            "{}{}(anyscale +{}){} ".format(
                colorama.Style.BRIGHT,
                colorama.Fore.CYAN,
                self._time_string(),
                colorama.Style.RESET_ALL,
            ),
            end="",
        )
        print(*msg)

    def debug(self, *msg: str) -> None:
        if os.environ.get("ANYSCALE_DEBUG") == "1":
            print(
                "{}{}(anyscale +{}){} ".format(
                    colorama.Style.DIM,
                    colorama.Fore.CYAN,
                    self._time_string(),
                    colorama.Style.RESET_ALL,
                ),
                end="",
            )
            print(*msg)

    def warning(self, *msg: str) -> None:
        print(
            "{}{}(anyscale +{}){} ".format(
                colorama.Style.NORMAL,
                colorama.Fore.YELLOW,
                self._time_string(),
                colorama.Style.RESET_ALL,
            ),
            end="",
            file=sys.stderr,
        )
        print(*msg, file=sys.stderr)

    def _time_string(self) -> str:
        delta = time.time() - self.t0
        hours = 0
        minutes = 0
        while delta > 3600:
            hours += 1
            delta -= 3600
        while delta > 60:
            minutes += 1
            delta -= 60
        output = ""
        if hours:
            output += "{}h".format(hours)
        if minutes:
            output += "{}m".format(minutes)
        output += "{}s".format(round(delta, 1))
        return output
