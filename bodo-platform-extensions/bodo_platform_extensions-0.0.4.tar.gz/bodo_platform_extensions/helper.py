import subprocess
import os


def get_hosts_from_machinefile(machinefile=None):
    if machinefile is None:
        machinefile = f"{os.getenv('HOME')}/machinefile"
    hosts = []
    with open(machinefile, "r") as f:
        for l in f:
            hosts.append(l.rstrip("\n").split(":")[0])
    return hosts


# TODO Replace mpiexec with subprocess.Popen
def execute_on_all_nodes(command: str, timeout=None, verbose=False):
    """
    Execute the given command on all nodes in the cluster
    via mpiexec.
    """
    args = [
        "mpiexec",
        "--machinefile",  # Use machinefile to specify the nodes
        f"{os.getenv('HOME')}/machinefile",
        "-prepend-rank",  # To make the output easier to parse through
        "-ppn",  # Run once per node
        "1",
    ]
    args += command.split()

    return execute_shell(args, timeout=timeout, verbose=verbose)


def execute_shell(cmd, timeout, verbose=False):

    if isinstance(cmd, str):
        cmd = cmd.split()

    if verbose:
        print("Command: ", " ".join(cmd))

    stdout_ = ""
    stderr_ = ""
    returncode = None
    timed_out = False

    try:
        res = subprocess.run(cmd, capture_output=True, timeout=timeout)
        stdout_ = res.stdout.decode("utf-8")
        stderr_ = res.stderr.decode("utf-8")
        returncode = res.returncode
    except subprocess.TimeoutExpired as e:
        stdout_ = e.stdout.decode("utf-8") if e.stdout else e.stdout
        stderr_ = e.stderr.decode("utf-8") if e.stderr else e.stderr
        returncode = 124  # Usual shell error code for timeouts
        timed_out = True
    # TODO Handle other types of exceptions

    return stdout_, stderr_, returncode, timed_out


def copy_file_to_all_nodes(source, dest, verbose=False, timeout=None):
    hosts = get_hosts_from_machinefile()

    num_timed_out = 0
    num_errored_out = 0

    processes = []
    for host in hosts:
        cmd = ["scp", source, f"{host}:{dest}"]
        if verbose:
            print("Running: ", " ".join(cmd))
        p = subprocess.Popen(cmd)
        processes.append(p)

    for host, p in zip(hosts, processes):
        try:
            rc = p.wait(timeout=timeout)
            if rc != 0:
                raise subprocess.CalledProcessError(rc, cmd)
        except subprocess.TimeoutExpired as e:
            num_timed_out += 1
            if verbose:
                print(f"Timed out on {host}")
        except subprocess.CalledProcessError as e:
            num_errored_out += 1
            if verbose:
                print(f"Errored out on {host}. Exit Code: {rc}")

    return num_timed_out, num_errored_out, len(hosts)
