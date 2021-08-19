import argparse
import functools
import signal
import subprocess
import threading
from pathlib import Path
from typing import List, Callable, Optional

from heal.util import SP_KWARGS, print_output, write, is_ko
from heal.watch import Watcher


def try_checks(checks: List[dict], update_status: Callable, delay: float = 10, first_call: bool = True) -> None:
    """
    This function will go through the given "checks" and test their condition by running them one by one.
    On failure, it will attempt to apply the corresponding fix.

    Since the fix may take a while, after a given delay the function will call itself to keep the checks running.
    Only the previous (i.e. successful) checks will be given as parameter to the recursive call.

    After the fix, the condition will be tested again and, if successful, the checks will resume.
    Should it fail an exception will be raised, interrupting any ongoing recursion.

    Along the way, the given update_status() function will be called to communicate on the healing status ("fixing", "ok" or "ko").
    In general, it only makes sense to update this status in the first call (or top call) of this recursive function.
    That's because any recursive call actually happens when the top call is already "fixing" something.
    The only exception to that is when a fix failed ("ko"), and that can happen in recursions too.

    :param checks: list of checks to be tested
    :param update_status: function that will be called to communicate on the healing status ("fixing", "ok" or "ko")
    :param delay: in case of long fix, time to wait before recursing, defaults to 10 seconds
    :param first_call: whether or not it's the first call in the recursion, defaults to True
    :raises ChildProcessError: when a fix failed and the system is unstable
    """

    for i, check in enumerate(checks):
        # testing the condition
        test = check.get("check")
        cp = subprocess.run(test, **SP_KWARGS)
        if cp.returncode == 0:
            continue  # test successful, moving to the next one

        # on failure, first we print the result and output, just in case
        check_id = "[" + str(check.get("rank")) + "]"
        print_output(test, "failed", cp.stdout.splitlines(), check_id)

        # then we try to fix the problem
        if first_call:
            update_status("fixing")
        fix = check.get("fix")
        sp = subprocess.Popen(fix, **SP_KWARGS)
        threading.Thread(target=print_output, args=(fix, "fixing", sp.stdout, check_id)).start()  # we print the output in another thread so that it doesn't block
        while True:  # this part is weird but allows to keep the checks running if the fix takes too long
            try:
                sp.wait(delay)  # if the subprocess takes more than $delay seconds, this will raise a TimeoutExpired exception
                break
            except subprocess.TimeoutExpired:  # catched here, so that we can recurse
                try_checks(checks[:i], update_status, delay, first_call=False)

        # after the fix, we test the condition once again to ensure everything's back to normal
        cp = subprocess.run(test, **SP_KWARGS)
        if cp.returncode != 0:  # failing at this point is bad: the system stays broken, the fix is lacking
            print_output(test, "failed again", cp.stdout.splitlines(), check_id)
            update_status("ko")
            raise ChildProcessError()
        print(check_id, "fix successful")

    # everything is under control
    if first_call:
        update_status("ok")


def heal(configuration_directory: Path, status_file: Path, event: threading.Event, delay: float = 10) -> None:
    """
    Starts the configuration directory's monitoring and the healing loop.

    An Event must be provided to properly interrupt the loop.
    It must be sent (set()) in another thread or by setting up the capture of a system signal such as SIGINT or SIGTERM.

    :param configuration_directory: obviously
    :param status_file: Path to the file that will store the healing status ("fixing", "ok" or "ko") and other metadata
    :param event: Event that will interrupt the healing loop
    :param delay: time to wait between two iterations of the healing loop
    """

    if is_ko(status_file):
        print("exiting: ko status found in", status_file)
        return

    if not configuration_directory.is_dir():
        print("exiting:", configuration_directory, "must exist and be a directory")
        return

    print("watching:", configuration_directory)
    watcher = Watcher(configuration_directory)

    try:
        while not event.is_set():
            watcher.refresh_active_checks_if_necessary()  # the configuration is now up-to-date
            update_status = functools.partial(write, status_file, watcher.active_modes)  # here we create a partial function to write the metadata to the status file
            try_checks(watcher.active_checks, update_status, delay)  # the actual healing happens here
            event.wait(delay)  # interruptible pause before the next iteration

        print("exiting: loop-ending signal")
    except ChildProcessError:  # raised by try_checks() is a fix failed
        print("exiting: fatal error")


def main(args: Optional[List[str]] = None) -> None:
    """
    usage: [-h] [-c <path>] [-s <path>] [-d <duration>]

    Minimalist self-healing.

    optional arguments:
      -h, --help            show this help message and exit
      -c <path>, --configuration-directory <path>
                            path to the configuration directory, defaults to /etc/heal
      -s <path>, --status-file <path>
                            path to the status file, defaults to /var/heal/status.json
      -d <duration>, --delay <duration>
                            in seconds, time between two rounds of checks, defaults to 10
    """

    argparser = argparse.ArgumentParser(description="Minimalist self-healing.")
    argparser.add_argument("-c", "--configuration-directory", type=Path, default=Path("/etc/heal"), help="path to the configuration directory, defaults to /etc/heal", metavar="<path>")
    argparser.add_argument("-s", "--status-file", type=Path, default=Path("/var/heal/status.json"), help="path to the status file, defaults to /var/heal/status.json", metavar="<path>")
    argparser.add_argument("-d", "--delay", type=float, default=10, help="in seconds, time between two rounds of checks, defaults to 10", metavar="<duration>")
    args = argparser.parse_args(args)

    # turning SIGINT and SIGTERM into an event
    event = threading.Event()
    for sig in [signal.SIGINT, signal.SIGTERM]:
        signal.signal(sig, lambda signum, frame: event.set())

    heal(args.configuration_directory, args.status_file, event, args.delay)
