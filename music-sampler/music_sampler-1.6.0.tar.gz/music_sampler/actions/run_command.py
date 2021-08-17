import shlex, subprocess

def run(action, command="", wait=False, **kwargs):
    action.process = subprocess.Popen(command, shell=True)
    if wait:
        action.process.wait()

def description(action, command="", wait=False, **kwargs):
    formats = []
    message = "running command {}"
    formats.append(command)
    if wait:
        message += " (waiting for its execution to finish)"

    return _(message).format(*formats)
