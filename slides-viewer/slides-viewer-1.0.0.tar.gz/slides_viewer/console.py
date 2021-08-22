from logging import INFO, WARN, FileHandler, Formatter, StreamHandler, getLogger

from slides_viewer.args import parse_args
from slides_viewer.player.Application import Application
from slides_viewer.playlist.PlaylistJSON import PlaylistJSON


def main() -> int:
    setupLogger()

    args = parse_args()
    if args is None:
        return 1

    playlistPath, extraArgs = args

    playlist = PlaylistJSON.readFromFile(playlistPath)
    if playlist is None:
        return 1

    return Application(playlist, extraArgs).exec_()


def setupLogger() -> None:
    logger = getLogger()
    logger.setLevel(INFO)

    fmt = "[{asctime} - {levelname}] {filename} - {message}"
    formatter = Formatter(fmt, style="{", datefmt="%H:%M:%S")

    fileHandler = FileHandler("log.txt")
    fileHandler.setFormatter(formatter)
    fileHandler.setLevel(INFO)
    logger.addHandler(fileHandler)

    consoleHandler = StreamHandler()
    consoleHandler.setFormatter(formatter)
    consoleHandler.setLevel(WARN)
    logger.addHandler(consoleHandler)
