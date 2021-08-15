import os
import subprocess


def get_child_output(cmd, env=None, stderr=None):
    """
    Run a child process, and collect the generated output.

    @param cmd: Command to execute.
    @type  cmd: C{list} of C{str}

    @param env: Environment
    @type  env: C{dict}

    @param stderr: Pipe destination for stderr
    @type  stderr: file object

    @return: Generated output of the command, split on whitespace.
    @rtype:  C{list} of C{str}
    """
    return subprocess.check_output(cmd, universal_newlines=True, env=env, stderr=stderr).split()


def get_git_version():
    # method adopted shamelessly from OpenTTD's findversion.sh
    path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    env = dict(os.environ, LC_ALL="C")
    if not os.path.isdir(os.path.join(path, ".git")):
        return None

    # Refresh the index to make sure file stat info is in sync
    try:
        get_child_output(["git", "-C", path, "update-index", "--refresh"], env=env)
    except FileNotFoundError:
        # Bail early if `git` isn't available (we know `path` exists)
        print("Git checkout found but `git` isn't installed; cannot determine version.")
        return None
    except subprocess.CalledProcessError:
        # Not an issue if this fails
        pass

    # Look for modifications
    try:
        modified = len(get_child_output(["git", "-C", path, "diff-index", "HEAD"], env=env)) > 0
        isodate = get_child_output(["git", "-C", path, "show", "-s", "--pretty=%ci", "HEAD"], env=env)[0]
        # git describe output is <tag>-<commits since tag>-<hash>, and <tag> may contain '-'
        describe = get_child_output(["git", "-C", path, "describe", "--tags", "--long"], env=env)[0].rsplit("-", 2)
        tag = describe[0]
        release = describe[1] == "0"
        changeset = describe[2]
    except OSError as e:
        print("Git checkout found but cannot determine its version. Error({0}): {1}".format(e.errno, e.strerror))
        return None
    except subprocess.CalledProcessError as e:
        print("Git checkout found but cannot determine its version. Error: ", e)
        return None

    try:
        branch = get_child_output(["git", "-C", path, "symbolic-ref", "-q", "HEAD"], env=env)[0].split("/")[-1]
    except subprocess.CalledProcessError:
        # A detached head will make the command fail, but it's not critical.
        # Treat it like branch 'master'.
        branch = "master"

    # Compose the actual version string following PEP440
    version = tag.replace("-", "").lower()
    local_parts = []

    if modified or not release:
        version += ".post" + isodate.replace("-", "")
        if branch != "master":
            local_parts.append(branch.replace("-", "."))

    if not release:
        local_parts.append(changeset)

    if modified:
        local_parts.append("m")

    if local_parts:
        version += "+" + ".".join(local_parts)

    return version


def get_and_write_version():
    # If the source is in a git repository, retrieve
    #  the current version from git and update __version__.py
    version = get_git_version()
    if not version:
        return None
    try:
        path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        with open(os.path.join(path, "nml", "__version__.py"), "w") as file:
            file.write("# this file is autogenerated by setup.py\n")
            file.write('version = "{}"\n'.format(version))
        return version.split()[0]
    except IOError:
        print("Version file NOT written")
        return None
