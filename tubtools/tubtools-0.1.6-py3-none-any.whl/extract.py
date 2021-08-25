import os
import tarfile
import zipfile
import io

import fleep


def extract_as_file(path, fname, fileobj):
    with open(os.path.join(path, fname), 'wb') as f:
        f.write(fileobj.read())


# https://stackoverflow.com/questions/10060069/safely-extract-zip-or-tar-using-python
resolved = lambda x: os.path.realpath(os.path.abspath(x))


def badpath(path, base):
    # joinpath will ignore base if path is absolute
    return not resolved(os.path.join(base, path)).startswith(base)


def badlink(info, base):
    # Links are interpreted relative to the directory containing the link
    tip = resolved(os.path.join(base, os.path.dirname(info.name)))
    return badpath(info.linkname, base=tip)


def safemembers(members):
    base = resolved(".")

    for finfo in members:
        if badpath(finfo.name, base):
            print(f"{finfo.name} is blocked (illegal path)")
        elif finfo.issym() and badlink(finfo, base):
            print(f"{finfo.name} is blocked: Hard link to {finfo.linkname}")
        elif finfo.islnk() and badlink(finfo, base):
            print(f"{finfo.name} is blocked: Symlink to {finfo.linkname}")
        else:
            yield finfo


def auto_extract_tar_gz(path, fileobj):
    with tarfile.open(fileobj=fileobj, mode='r:gz') as t:
        t.extractall(path=path, members=safemembers(t))
        return True


def auto_extract_zip(path, fileobj):
    with zipfile.ZipFile(fileobj) as z:
        for m in z.infolist():
            z.extract(m, path=path)


def auto_extract(path, fname, fileobj):
    try:
        if fname.endswith('.tar.gz') or fname.endswith('.tgz'):
            auto_extract_tar_gz(path, fileobj)
        elif fname.endswith('.zip'):
            auto_extract_zip(path, fileobj)
        else:
            raise ValueError(f'Unknown file extension for file {fname}')
    except tarfile.ReadError as t:
        raise ValueError('Failed to extract tarfile') from t
    except zipfile.BadZipfile as z:
        raise ValueError('Failed to extract zipfile') from z


def extract_all_submissions(path, sub, by_group=False):
    with zipfile.ZipFile(io.BytesIO(sub)) as z:
        if not by_group:
            print(f'Extracting {len(z.namelist())} submissions to {path}')
            # TODO Not fully sanitized.
            for n in z.namelist():
                student = n.split('_')[0]
                userpath = os.path.join(path, student)
                fname = os.path.basename(n)
                os.makedirs(userpath, exist_ok=True)
                with z.open(n) as s:

                    try:
                        auto_extract(userpath, fname, s)
                    except ValueError:
                        print(f'Auto-Extraction for {student} failed. Attempting fallback')

                        try:
                            s.seek(0)
                            magic_bytes = s.read(128)
                            s.seek(0)
                            info = fleep.get(magic_bytes)
                        except io.UnsupportedOperation:
                            # Workaround for Python < 3.7
                            with z.open(n) as s2:
                                magic_bytes = s2.read(128)
                                info = fleep.get(magic_bytes)

                        ext = ''
                        if 'zip' in info.extension:
                            ext += '.zip'
                        elif 'gz' in info.extension:
                            ext += '.tar.gz'  # TODO What if its just gz?
                        if ext != '':
                            fname += ext
                            print(f'Magic bytes indicate file type: {ext[1:]}')

                        try:
                            auto_extract(userpath, fname, s)
                        except ValueError:
                            print('Fallback failed. Writing submission as is.')
                            extract_as_file(userpath, fname, s)

        else:

            groups = set(n.split('-')[0] for n in z.namelist())
            print(f'Extracting {len(groups)} group submissions to {path}')
            for g in groups:

                # We assume all submissions by the same group are identical
                group_subs = list(filter(lambda s: s.startswith(g + '-'),
                                         z.namelist()))

                if len(group_subs) == 0:
                    raise ValueError('Cannot extract as group submission! Is this an individual assignment?')

                group_path = os.path.join(path, g)
                os.makedirs(group_path, exist_ok=True)
                fname = os.path.basename(group_subs[0])
                with z.open(group_subs[0]) as s:
                    try:
                        auto_extract(group_path, fname, s)
                    except ValueError as e:
                        print(f'Auto-Extraction for submission from group {g}! Attempting fallback.')

                        try:
                            s.seek(0)
                            magic_bytes = s.read(128)
                            s.seek(0)
                            info = fleep.get(magic_bytes)
                        except io.UnsupportedOperation:
                            # Workaround for Python < 3.7
                            with z.open(group_subs[0]) as s2:
                                magic_bytes = s2.read(128)
                                info = fleep.get(magic_bytes)

                        ext = ''
                        if 'zip' in info.extension:
                            ext += '.zip'
                        elif 'gz' in info.extension:
                            ext += '.tar.gz'  # TODO What if its just gz?

                        if ext != '':
                            fname += ext
                            print(f'Magic bytes indicate file type: {ext[1:]}')

                        try:
                            auto_extract(group_path, fname, s)
                        except ValueError:
                            print('Fallback failed. Writing submission as is.')
                            extract_as_file(group_path, fname, s)
