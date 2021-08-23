from eggdriver.resources import installFromRequests, sysCommand

def build():
    installFromRequests(["setuptools", "twine", "build"], False)
    sysCommand("-m build --sdist")
    sysCommand("-m build --wheel")
    sysCommand("-m twine check dist/*")
    sysCommand("-m twine upload dist/*")
