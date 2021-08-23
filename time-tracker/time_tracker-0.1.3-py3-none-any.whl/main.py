from time_tracker.log import Logger
import time
import datetime
import typer
import os
from enum import Enum
import logging


class SessionType(str, Enum):
    workTime = 1
    breakTime = 2
    bigBreakTime = 3
    exit = 0


class Mode(str, Enum):
    manual = "manual"
    pomodoro = "pomodoro"


app = typer.Typer()


@app.callback()
def callback():
    """
    Time tracker cli
    """


def checkNextTurn(
    workDuration: int, breakDuration: int, bigBreakDuration: int, countSession: int
):
    """Run Session in manual mode"""

    description = f"""
    What's next?
    1 for work - {workDuration} minutes
    2 for small break - {breakDuration} minutes
    3 for big break - {bigBreakDuration} minutes
    0 to exit
    """
    option: str = typer.prompt(description, type=SessionType)

    if option == SessionType.workTime:
        runSession(workDuration, False, option)
    elif option == SessionType.breakTime:
        runSession(breakDuration, False, option)
    elif option == SessionType.bigBreakTime:
        runSession(bigBreakDuration, False, option)
    else:
        print("Have a good time off!")
        exit()


def runSession(time: int, shouldPrompt: bool, sessionType: SessionType):
    """Run individual session (supports work or break sessions)"""

    if sessionType == sessionType.workTime:
        workDescription: str = typer.prompt("What do you plan to do?")

        logging.info(
            f"Started work sessions with {time} minutes. TODO: {workDescription}"
        )
        countdown(time)
        notify("Session finished", "Ready for next?")
    else:
        logging.info(f"Started break session with {time} minutes.")
        countdown(time)
        notify("Session finished", "Ready for next?")

    if shouldPrompt:
        nextSession = typer.confirm("Go to next session it?")
        if not nextSession:
            typer.echo("Stop session")
            raise typer.Abort()


def countdown(workMinutes: int):
    workSeconds = workMinutes * 60
    while workSeconds > 0:
        typer.clear()
        typer.echo(datetime.timedelta(seconds=workSeconds), nl=True)
        time.sleep(1)
        workSeconds = workSeconds - 1

    print("Finished session!")


def notify(title, text):
    os.system(
        f"""
              osascript -e 'say \"Finished!\"';
              osascript -e 'display notification "{text}" with title "{title}"'
              """
    )


@app.command()
def log(
    last_log: bool = typer.Option(False, "--last", "-l", help="Open last log file"),
    output: bool = typer.Option(
        False, "--output", "-o", help="Return log file content to terminal"
    ),
):
    Logger.get_logs(last_log, output)


@app.command()
def track(
    workDuration: int = typer.Option(
        25, "--workDuration", "-w", help="Set work time (minutes)"
    ),
    breakDuration: int = typer.Option(
        5, "--breakDuration", "-b", help="Set break time (minutes)"
    ),
    bigBreakDuration: int = typer.Option(
        30, "--bigBreakDuration", "-B", help="Set break time (minutes)"
    ),
    mode: Mode = typer.Option(
        Mode.pomodoro,
        "--mode",
        "-m",
        help="Set pomodoro mode. This will change the flow of work to 4 work sessions with small breaks and finish with a big Break",
    ),
    prompt: bool = typer.Option(
        True, "--prompt", "-p", help="Set if it should prompt to go for next session"
    ),
):
    """Run depending on mode"""

    countSession = 1

    if mode == Mode.manual:
        while True:
            countSession = countSession + 1
            checkNextTurn(workDuration, breakDuration, bigBreakDuration, countSession)
    elif mode == Mode.pomodoro:
        while True:
            runSession(workDuration, prompt, SessionType.workTime)
            runSession(breakDuration, prompt, SessionType.breakTime)
            runSession(workDuration, prompt, SessionType.workTime)
            runSession(breakDuration, prompt, SessionType.breakTime)
            runSession(workDuration, prompt, SessionType.workTime)
            runSession(breakDuration, prompt, SessionType.breakTime)
            runSession(workDuration, prompt, SessionType.workTime)
            runSession(bigBreakDuration, prompt, SessionType.bigBreakTime)


if __name__ == "__main__":
    Logger()
    app()
