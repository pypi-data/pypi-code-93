#!/usr/bin/env python3


# import click
#
# @click.command()
# @click.option('--count', default=1, help='Number of greetings.')
# @click.option('--name', prompt='Your name',
#               help='The person to greet.')
# def hello(count, name):
#     """Simple program that greets NAME for a total of COUNT times."""
#     for x in range(count):
#         click.echo(f"Hello {name}!")

try:
    import ujson as json
except ImportError:
    import json

import sys
import termcolor
from retriever_research.config import LogIds, LogLevels
from retriever_research import messages

FILTERED_OUT = [
    LogIds.FILE_CHUNKER_RECEIVED_MESSAGE,
    LogIds.FILE_CHUNKER_SENT_MESSAGE,
    LogIds.ACTOR_WATCHER_UPDATE,
]

def main():
    for line in sys.stdin:
        j = json.loads(line.strip())
        l = messages.LogMessage.from_json(j)

        if l.log_id is not None and l.log_id in FILTERED_OUT:
            continue
        level = "INFOV" if l.level == LogLevels.INFO_VERBOSE else l.level
        s = f'{level} - {l.timestamp.strftime("%H:%M:%S.%f")} - {l.actor} - {l.log}'
        if l.level == LogLevels.ERROR:
            s = termcolor.colored(s, 'red')
        elif l.level == LogLevels.WARN:
            s = termcolor.colored(s, 'yellow')
        elif l.level in [LogLevels.INFO, LogLevels.INFO_VERBOSE]:
            s = termcolor.colored(s, 'blue')
        # elif l.level == LogLevels.TRACE:
        #     s = termcolor.colored(s, 'magenta')
        print(s)


if __name__ == '__main__':
    main()