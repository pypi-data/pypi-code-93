#/usr/bin/python3

import os
import subprocess
import sys
import threading
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileModifiedEvent

class MarkdownWatcher:

    def __init__(self, src_file, *pandoc_args):
        self._kill = False
        if not os.path.isfile(src_file):
            raise FileNotFoundError("The file {} does not appear to exist.".format(src_file))
        file_dir = os.path.dirname(os.path.abspath(src_file))
        self.observer = Observer()
        self.handler = PandocRenderHandler(src_file, *pandoc_args)
        self.observer.schedule(self.handler, file_dir)

    def run(self):
        self.observer.start()
        try:
            while True:
                if self._kill:
                    self.observer.stop()
                    break
                time.sleep(0.1)
        except KeyboardInterrupt:
            self.observer.stop()
        self.observer.join()

    def stop(self):
        self._kill = True

class PandocRenderHandler(FileSystemEventHandler):

    DEFAULT_OUTFILE = 'out.pdf'

    def __init__(self, src_file, *pandoc_args):
        super(PandocRenderHandler, self).__init__()
        self._pandoc_thread_timer = None
        self.src_file = os.path.abspath(src_file)
        if pandoc_args:
            self.pandoc_cmd = ('pandoc', self.src_file) + pandoc_args
        else:
            self.pandoc_cmd = ('pandoc', self.src_file, '-o', PandocRenderHandler.DEFAULT_OUTFILE)

    def pandoc_render(self):
        print("Running: {}".format(" ".join(self.pandoc_cmd)))
        process = subprocess.run(
            self.pandoc_cmd,
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
            universal_newlines=True
        )
        if process.returncode:
            print("WARNING: the following error was encoured from pandoc:")
            print(process.stderr)
        self._pandoc_thread_timer = None

    def start_render_timer(self):
        self._pandoc_thread_timer = threading.Timer(0.25, self.pandoc_render)
        self._pandoc_thread_timer.start()

    def restart_render_timer(self):
        if self._pandoc_thread_timer:
            self._pandoc_thread_timer.cancel()
        self.start_render_timer()

    def on_modified(self, event):
        if isinstance(event, FileModifiedEvent) and event.src_path == self.src_file:
            if self._pandoc_thread_timer:
                self.restart_render_timer()
            else:
                self.start_render_timer()

def usage():
    print("Usage: live-pandoc <source_file> <pandoc_command>")
    print("  live-pandoc is designed to be used identically to pandoc.")
    print()
    print("  Once started live-pandoc will watch for changes to the source file, and")
    print("  run the given pandoc command anytime a change occurs.")
    print()
    print("  The following example: 'live-pandoc README.md -o README.pdf'")
    print("  will watch README.md for changes and run 'pandoc README.md -o README.pdf' when changes occur.")

def main():
    if len(sys.argv) == 1:
        print("Error: No arguments given.")
        print()
        usage()
        sys.exit(1)
    elif len(sys.argv) == 2:
        file = sys.argv[1]
        if file in ('-h', '--help', 'help'):
            usage()
            sys.exit(0)
        pandoc_args = ()
    else:
        file = sys.argv[1]
        pandoc_args = sys.argv[2:]

    watcher = MarkdownWatcher(file, *pandoc_args)
    watcher.run()

if __name__ == '__main__':
   main()
