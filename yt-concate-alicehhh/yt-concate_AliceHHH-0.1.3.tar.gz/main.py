import sys
import getopt
import logging

from yt_concate.utils import Utils

from yt_concate.pipeline.steps.preflight import Preflight
from yt_concate.pipeline.steps.get_video_list import GetVideoList
from yt_concate.pipeline.steps.initialize_yt import InitializeYT
from yt_concate.pipeline.steps.download_captions import DownloadCaptions
from yt_concate.pipeline.steps.read_caption import ReadCaption
from yt_concate.pipeline.steps.search import Search
from yt_concate.pipeline.steps.download_videos import DownloadVideos
from yt_concate.pipeline.steps.edit_video import EditVideo
from yt_concate.pipeline.steps.postflight import Postflight

from yt_concate.pipeline.pipeline import Pipeline


def config_logger(level):
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    file_handler = logging.FileHandler("logging.txt")
    stream_handler = logging.StreamHandler()

    file_formatting = logging.Formatter("%(levelname)s : %(asctime)s : %(module)s : %(message)s")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(file_formatting)

    stream_formatting = logging.Formatter("%(levelname)s : %(message)s")
    stream_handler.setLevel(level)
    stream_handler.setFormatter(stream_formatting)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    return logger


def print_usage():
    print("python3 main.py OPTIONS")
    print("OPTIONS")
    print("{:>6} {:<16} {}".format("-c", "--channel_id", "Channel id of the youtube channel to download."))
    print("{:>6} {:<16} {}".format("-s", "--search_word", "The word be searched in captions."))
    print("{:>6} {:<16} {}".format("-l", "--limit", "Amount of the clips be put in the output videos. Default: 20"))
    print("{:>6} {:<16} {}".format("", "--cleanup", "Captions and videos downloaded in run would be deleted."))
    print("{:>6} {:<16} {}".format("", "--fast", "If the file exists, skip downloading."))
    print("{:>6} {:<16} {}".format("", "--level", "Logging level to print on the screen("
                                                  "debug/info/warning/error/critical). Default: info"))
    print("{:>6} {:<16} {}".format("", "--thread", "Amount of threads when multi-threading. Default: 2"))


def command_setup(inputs):
    short_opts = "hc:s:l:"
    long_opts = "help channel_id= search_word= limit= cleanup fast level= thread=".split()

    try:
        opts, args = getopt.getopt(sys.argv[1:], short_opts, long_opts)
    except getopt.GetoptError:
        print_usage()
        sys.exit(2)

    for opt, arg in opts:
        if opt == "-h":
            print_usage()
            sys.exit(0)
        elif opt in ("-c", "--channel_id"):
            inputs["channel_id"] = arg
        elif opt in ("-s", "--search_word"):
            inputs["search_word"] = arg
        elif opt in ("-l", "--limit"):
            inputs["limit"] = int(arg)
        elif opt == "--cleanup":
            inputs["cleanup"] = True
        elif opt == "--fast":
            inputs["fast"] = True
        elif opt == "--level":
            if arg == "debug":
                inputs["level"] = logging.DEBUG
            elif arg == "info":
                inputs["level"] = logging.INFO
            elif arg == "warning":
                inputs["level"] = logging.WARNING
            elif arg == "error":
                inputs["level"] = logging.ERROR
            elif arg == "critical":
                inputs["level"] = logging.CRITICAL
            else:
                print_usage()
                sys.exit(2)
        elif opt == "--thread":
            inputs["thread"] = int(arg)

    if not inputs["channel_id"] or not inputs["search_word"]:
        print_usage()
        sys.exit(2)


def main():
    inputs = {
        "channel_id": "UCnBmw2l9H5APqatWDqmdubw",
        "search_word": "like",
        "limit": 20,
        "cleanup": False,
        "fast": False,
        "level": logging.INFO,
        "thread": 2,
    }

    command_setup(inputs)

    steps = [
        Preflight(),
        GetVideoList(),
        InitializeYT(),
        DownloadCaptions(),
        ReadCaption(),
        Search(),
        DownloadVideos(),
        EditVideo(),
        Postflight(),
    ]

    log = config_logger(inputs["level"])
    utils = Utils()
    p = Pipeline(steps)
    p.run(inputs, utils, log)


if __name__ == "__main__":
    main()
