import sys
import asyncio
from .async_processor import AsyncProcessor
from .cleanup import CleanupAsyncProcessor
from . import cmdline_args


def main():
    args = cmdline_args.get_adjusted_args()

    loop = asyncio.get_event_loop()
    processor = AsyncProcessor(
        args.process_count,
        args.shell_commands,
        log_to_file=args.log_to_file,
    )
    try:
        loop.run_until_complete(processor.start())

    except KeyboardInterrupt:
        processor.stop()
        print("multiprocess: cleaning up started processes...", file=sys.stderr)
        cleanup = CleanupAsyncProcessor(processor, loop, args.kill_signal)
        loop.run_until_complete(cleanup.start())

    finally:
        if not args.log_to_file:
            print(processor.filelogger.get_log_str())

        loop.close()
        exit(processor.returncode)
