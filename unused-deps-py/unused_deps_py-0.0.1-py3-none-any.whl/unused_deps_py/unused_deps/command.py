import logging
import subprocess


def run(command, *, timeout=600, cwd=None, log_error=True):
    try:
        logging.debug(f"running {command} cwd={cwd}")
        result = subprocess.run(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
            cwd=cwd,
        )
    except subprocess.TimeoutExpired as e:
        logging.error(f"Command {command} timed out!")
        result = e
        result.returncode = -1

    lines = []
    if result.stdout:
        lines.extend(_lines("STDOUT", result.stdout))
    if result.stderr:
        lines.extend(_lines("STDERR", result.stderr))
    result.full_output = "\n".join(lines)

    if result.returncode != 0:
        if log_error:
            logging.error(
                f"Command {command} cwd={cwd} failed!\n" f"{result.full_output}"
            )
    logging.debug(result.full_output)

    return result


def output(command, *, timeout=600, cwd=None, log_error=True):
    result = run(command, timeout=timeout, cwd=cwd, log_error=log_error)
    if result and result.stdout:
        return result.stdout.decode("utf-8")
    return ""


def success(command, *, timeout=600, cwd=None, log_error=False):
    result = run(command, timeout=timeout, cwd=cwd, log_error=log_error)
    return result is not None and result.returncode == 0


def _lines(prefix, out):
    out = out.decode("utf-8")
    return [f" {prefix}> " + line for line in out.splitlines()]
