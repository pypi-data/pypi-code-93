def rand_str(N=16, char_set=None):
    import string, random
    from string import ascii_letters, digits
    if char_set is None: char_set = ascii_letters + digits

    return ''.join(random.choice(char_set) for x in range(N))

def check_versions(cef):
    import platform
    ver = cef.GetVersion()
    print("[hello_world.py] CEF Python {ver}".format(ver=ver["version"]))
    print("[hello_world.py] Chromium {ver}".format(ver=ver["chrome_version"]))
    print("[hello_world.py] CEF {ver}".format(ver=ver["cef_version"]))
    print("[hello_world.py] Python {ver} {arch}".format(
           ver=platform.python_version(),
           arch=platform.architecture()[0]))
    assert cef.__version__ >= "66.0", "CEF Python v66.0+ required to run this"

def init_dirs(path):
    import os
    static = os.path.join(path, "static")
    templates = os.path.join(path, "templates")
    os.makedirs(static, exist_ok=True)
    os.makedirs(templates, exist_ok=True)
