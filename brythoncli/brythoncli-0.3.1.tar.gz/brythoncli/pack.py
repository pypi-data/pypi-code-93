import os
import ast
import time
import json


from brython import make_package, python_minifier


def excludefile(excludes, name, ext):
    if name.startswith('.') or ext != '.py':
        return True

    if name in excludes:
        return True

    return False


def excludedir(excludes, d):
    root_elts = d.split(os.sep)
    for p in root_elts:
        if len(p) > 1 and p.startswith('.'):
            return True

        if p.startswith('_'):
            return True

        if p in excludes:
            return True

    return False


def create_package(package_name, package_path, excludes=None, outpath=None,
                   suffix=".brython.js"):
    print("Generating package {}".format(package_name))
    VFS = {"$timestamp": int(1000 * time.time())}
    has_init = os.path.exists(os.path.join(package_path, "__init__.py"))
    nb = 0

    if excludes is None:
        excludes = []

    for dirpath, _, filenames in os.walk(package_path):

        if excludedir(excludes, dirpath):
            continue

        if dirpath == package_path:
            package = []
        else:
            package = dirpath[len(package_path) + 1:].split(os.sep)

        if has_init:
            package.insert(0, package_name)

        for filename in filenames:
            name, ext = os.path.splitext(filename)
            if excludefile(excludes, name, ext):
                continue

            is_package = name.endswith('__init__')
            if is_package:
                mod_name = '.'.join(package)
            else:
                mod_name = '.'.join(package + [name])

            nb += 1
            absname = os.path.join(dirpath, filename)
            with open(absname, encoding='utf-8') as f:
                data = f.read()

            data = python_minifier.minify(data, preserve_lines=True)
            path_elts = package[:]
            if os.path.basename(filename) != "__init__.py":
                path_elts.append(os.path.basename(filename)[:-3])

            with open(absname, encoding="utf-8") as f:
                tree = ast.parse(f.read())
                visitor = make_package.Visitor(package_path, package)
                visitor.visit(tree)
                imports = sorted(list(visitor.imports))

            if is_package:
                VFS[mod_name] = [ext, data, imports, 1]
            else:
                VFS[mod_name] = [ext, data, imports]

            print(
                f'Adding {mod_name} {"package" if is_package else "module"}.')

    if nb == 0:
        print("No file to create package.")
    else:
        print('{} files'.format(nb))

        outpath = os.path.join(
            outpath or os.curdir,
            package_name + suffix
        )
        with open(outpath, "w", encoding="utf-8") as out:
            out.write('__BRYTHON__.use_VFS = true;\n')
            out.write('var scripts = {}\n'.format(json.dumps(VFS)))
            out.write('__BRYTHON__.update_VFS(scripts)\n')
