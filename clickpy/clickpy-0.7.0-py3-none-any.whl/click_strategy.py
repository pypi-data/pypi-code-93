"""All Clicking Strategies should be placed in this folder."""

from dataclasses import dataclass
from random import randint
from time import sleep
from typing import Callable, Optional, Protocol, runtime_checkable

import pyautogui  # type: ignore
import typer


@runtime_checkable
class SupportsClick(Protocol):  # pylint: disable=R0903
    """
    Definition of SupportsClick Protocol.

    Any object with a `__click__()` method can be considered a structural sub-type of
    SupportsClick.
    """

    def __click__(self) -> None:
        """
        Protocol method for the auto_click function.

        Any ClickStrategy class should implement a '__click__' method.
        """


@dataclass
class BasicClickStrategy:
    """The first, very basic clicking strategy I came up with.

    Before clicking, __click__ will tell the current thread to sleep.
    If self.sleep_time has a value, it will use that as the thread sleep time.
    Else, it will generate a random number between 1 and 180 (3 minutes).
    """

    min_sleep_bound: int = 1
    max_sleep_bound: int = 180
    sleep_time: Optional[float] = None
    print_debug: Optional[bool] = None
    echo: Callable[[object], None] = typer.echo

    def __click__(self) -> None:
        """
        Protocol method for SupportsClick.

        Process:
        1. Either use the sleep_time passed into the ctr, or get a random int
        between min_sleep_time and max_sleep_time.
        2. Pause the current thread with above int (in seconds).
        3. call pyautogui.click()
        Optional: print statements if print_debug = True.
        """
        timer = (
            self.sleep_time
            if self.sleep_time
            else float(randint(self.min_sleep_bound, self.max_sleep_bound))
        )

        if self.print_debug and not self.sleep_time:
            self.echo(f"Random thread sleep for {timer} seconds.")

        if self.print_debug:
            self.echo("Thread sleeping now...")

        sleep(timer)

        pyautogui.click()

        if self.print_debug:
            self.echo("... Clicked")
