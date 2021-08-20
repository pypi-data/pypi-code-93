from os import path


def version_add(version1, step=10):
    version2 = version1[0] * step * step + version1[1] * step + version1[2] + 1

    version1[2] = version2 % step
    version1[1] = int(version2 / step) % step
    version1[0] = int(version2 / step / step)

    return version1


def get_version(argv, version_path, step=10):
    if path.exists(version_path):
        with open(version_path, 'r') as f:
            version1 = [int(i) for i in f.read().split('.')]
    else:
        version1 = [0, 0, 1]

    if len(argv) >= 2 and argv[1] == 'build':
        version1 = version_add(version1, step)

    version3 = '{}.{}.{}'.format(*version1)
    with open(version_path, 'w') as f:
        f.write(version3)
    return version3
