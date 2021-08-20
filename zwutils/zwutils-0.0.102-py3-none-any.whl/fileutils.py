import os
import sys
import codecs
import json
import csv
import hashlib
import subprocess
from pathlib import Path

def rmfile(pth, ignore_miss=False):
    if os.path.isfile(str(pth)):
        os.remove(str(pth))
    elif not ignore_miss:
        print('[FILEUTILS][WARN] %s file not found'%pth)

def writefile(path, txt, enc='utf-8'):
    if not isinstance(txt, str):
        txt = str(txt)
    if not Path(path).parent.exists():
        Path(path).parent.mkdir(parents=True, exist_ok=True)
    with codecs.open(str(path), 'w', enc) as fp:
        fp.write(txt)
        fp.flush()

def readfile(path, enc='utf-8', default=None):
    rtn = None
    if not Path(path).exists() and default is not None:
        return default
    with codecs.open(str(path), 'r', enc) as fp:
        rtn = fp.read()
    if rtn.startswith('\ufeff'):# BOM
        rtn = rtn[1:]
    return rtn

def writebin(path, dat):
    if not Path(path).parent.exists():
        Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(str(path), 'wb') as fp:
        fp.write(dat)
        fp.flush()

def readbin(path, default=None):
    rtn = None
    if not Path(path).exists() and default is not None:
        return default
    with open(str(path), 'rb') as fp:
        rtn = fp.read()
    return rtn

def writejson(path, o, enc='utf-8'):
    if not Path(path).parent.exists():
        Path(path).parent.mkdir(parents=True, exist_ok=True)
    with codecs.open(str(path), 'w', enc) as fp:
        json.dump(o, fp, ensure_ascii=False)

def readjson(path, enc='utf-8', default=None):
    rtn = None
    if not Path(path).exists() and default is not None:
        return default
    with codecs.open(str(path), 'r',enc) as fp:
        rtn = json.load(fp)
    return rtn

def writecsv(path, array2d, delimiter=',', enc='utf-8'):
    if not Path(path).parent.exists():
        Path(path).parent.mkdir(parents=True, exist_ok=True)
    with codecs.open(str(path), 'w', enc) as fp:
        writer = csv.writer(fp, delimiter=delimiter)
        writer.writerows(array2d)

def readcsv(path, enc='utf-8', default=None):
    rtn = None
    if not Path(path).exists() and default is not None:
        return default
    with codecs.open(str(path), 'r', enc) as fp:
        reader = csv.reader(fp)
        rtn = list(reader)
    return rtn

def file_encode_convert(src, dst, src_encode='utf-8', dst_encode='gbk'):
    src_encode = src_encode.lower()
    dst_encode = dst_encode.lower()
    with codecs.open(src, 'r', src_encode) as fp:
        new_content = fp.read()
    with codecs.open(src, 'w', dst_encode) as fp:
        fp.write(new_content)
        fp.flush()

def md5(fp):
    hash_md5 = hashlib.md5()
    with open(fp, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def zip(srcpth, destpth=None, pwd=None, pth7z=None):
    """Use 7z.exe or zip command to zip file or dir
    :param srcpth: ./dir/file => file in zip, dir/file => dir/file in zip
    :param destpth: zip in srcpth if None
    :param pwd: no password if not set
    :param pth7z: 7z.exe in ./bin in win by default, zip command in linux

    """
    iswin = True if sys.platform == 'win32' else False
    spath = Path(srcpth)
    sname = '%s.zip'%spath.stem if spath.is_file() else '%s.zip'%spath.name
    destpth = destpth or str(spath.parent / sname)
    cmd = pth7z or ( './bin/7z.exe' if iswin else 'zip' )
    cmds = [str(cmd)]
    if iswin:
        cmds.extend(['a', '-r', '-y'])
        if pwd:
            cmds.append('-p%s'%pwd)
    else:
        cmds.extend(['-q', '-r'])
        if pwd:
            cmds.append('-P %s'%pwd)
    cmds.extend([destpth, srcpth])
    subprocess.run(cmds)
    destfile = Path(destpth)
    return destfile.exists()

def unzip(srcpth, destpth=None, pwd=None, pth7z=None):
    iswin = True if sys.platform == 'win32' else False
    cmd = pth7z or ( './bin/7z.exe' if iswin else 'unzip' )    
    cmds = [str(cmd)]
    if iswin:
        cmds.extend(['x', srcpth, '-y', '-aoa', '-o%s'%destpth])
        if pwd:
            cmds.append('-p%s'%pwd)
    else:
        cmds.extend([srcpth, '-d', destpth])
        if pwd:
            cmds.append('-P %s'%pwd)
    subprocess.run(cmds)
    destfile = Path(destpth)
    return destfile.exists()

# def tar(pth, outpath=None, flag='w:gz'):
#     p = Path(pth)
#     outext = '.' + flag.split(':')[1] if len(flag.split(':'))==2 else '.gz'
#     outp = outpath or p.parent / (p.stem + outext)
#     # with open(pth, 'rb') as read, lzma.open(str(outp), 'wb') as write:
#     #     shutil.copyfileobj(read, write)
#     with tarfile.open(str(outp), flag) as tar:
#         tar.add(pth)

# def tardir(pth, outpath=None, flag='w:gz', exclude=None):
#     '''exclude: glob-style
#     '''
#     p = Path(pth)
#     outext = '.' + flag.split(':')[1] if len(flag.split(':'))==2 else '.gz'
#     out = outpath or p.parent / (p.stem + outext)
#     with tarfile.open(str(out), flag) as tar:
#         for root, dirs, files in os.walk(pth):
#             for f in files:
#                 fp = os.path.join(root, f)
#                 zp = os.path.relpath(fp, os.path.join(pth, '..'))
#                 if exclude and Path(fp).match(exclude):
#                     continue
#                 tar.add(fp, zp)

# def unzip(pth, outdir=None, pwd=None):
#     p = Path(pth)
#     out = Path(outdir) or p.parent
#     out.mkdir(parents=True, exist_ok=True)
#     with zipfile.ZipFile(pth) as zf:
#         zf.extractall(str(out))

# def zipdir(pth, outpath=None, exclude=None):
#     '''exclude: glob-style
#     '''
#     p = Path(pth)
#     out= Path(outpath) if outpath else p.parent / (p.stem + '.zip')
#     with zipfile.ZipFile(str(out), 'w', zipfile.ZIP_DEFLATED) as zipf:
#         for root, dirs, files in os.walk(pth):
#             for f in files:
#                 fp = os.path.join(root, f)
#                 zp = os.path.relpath(fp, os.path.join(pth, '..'))
#                 if exclude and Path(fp).match(exclude):
#                     continue
#                 zipf.write(fp, zp)