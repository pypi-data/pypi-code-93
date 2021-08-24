"""Auto Mouse clickpy Script. Make it look like your still online with Python Automation."""

from typing import Optional

# mypy doesn't like pyautogui, and I can't find its py.types
import pyautogui  # type: ignore
import typer

from .click_strategy import BasicClickStrategy, SupportsClick

# Disable FailSafeException when mouse is in screen corners.
# I don't need a failsafe for this script.
pyautogui.FAILSAFE = False


def auto_click(
    click_strategy: SupportsClick,
) -> None:
    """
    Call `__click__` method of the object passed in.

    Args:
    click_strategy (SupportsClick): Should be a ClickStrategy object.

    Raises:
    TypeError: Error raised if click_strategy is not a structural subtype of SupportClicks,
    """
    if not isinstance(click_strategy, SupportsClick):
        raise TypeError(
            f"Argument passed in of type {type(click_strategy)} does not implement"
            f" {SupportsClick.__name__}"
        )
    click_strategy.__click__()


app = typer.Typer()


@app.command()
def main(
    debug: Optional[bool] = typer.Option(None, "--debug", "-d"),
    fast_click: Optional[bool] = typer.Option(None, "--fast-click", "-f"),
) -> int:
    """Auto Mouse clickpy Script. Make it look like your still online with Python Automation."""
    print("Running clickpy. Enter ctrl+c to stop.")

    sleep_time = 0.5 if fast_click else None

    if debug and fast_click:
        print("fast_click flag passed in. Using thread.sleep(1), instead of a random interval.")

    click_strategy = BasicClickStrategy(sleep_time=sleep_time, print_debug=debug)

    while True:
        try:
            auto_click(click_strategy)
        except KeyboardInterrupt:
            msg = (
                "KeyboardInterrupt thrown and caught. Exiting script" if debug else "Back to work!"
            )
            print(f"\n{msg}")
            break

    return 0


if __name__ == "__main__":
    raise SystemExit(app())  # pragma: no cover
