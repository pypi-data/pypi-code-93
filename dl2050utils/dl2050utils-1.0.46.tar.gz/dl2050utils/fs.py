import sys, os
from pathlib import Path
import zipfile
import requests
import subprocess

Path.ls = lambda x: list(x.iterdir())

def get_dir_files(path, types=None):
    return [f for f in path.glob('**/*') if f.is_file() and (types==None or f.suffix[1:] in types)]

def get_dir_dirs(path):
    return [d for d in path.glob('**/*') if d.is_dir()]

def sh_run(cmd):
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    (stdout, stderr) = proc.communicate()
    return (proc.returncode, stdout.decode("utf-8") , stderr.decode("utf-8") )

def zipdir(dir, fname):
    zf = zipfile.ZipFile(fname, 'w', zipfile.ZIP_DEFLATED)
    for root, dirs, files in os.walk(dir):
        for file in files:
            zf.write(os.path.join(root, file))

def download_url(url, dest, overwrite=False, pbar=None, show_progress=True, chunk_size=1024*1024, timeout=4, retries=5):
    "Download `url` to `dest` unless it exists and not `overwrite`."
    # wget -c <url> && tar -zxvf <fname>
    if os.path.exists(dest) and not overwrite: return
    s = requests.Session()
    s.mount('http://',requests.adapters.HTTPAdapter(max_retries=retries))
    u = s.get(url, stream=True, timeout=timeout)
    try: file_size = int(u.headers["Content-Length"])
    except: show_progress = False

    with open(dest, 'wb') as f:
        nbytes = 0
        # if show_progress: pbar = progress_bar(range(file_size), auto_update=False, leave=False, parent=pbar)
        try:
            for chunk in u.iter_content(chunk_size=chunk_size):
                nbytes += len(chunk)
                if show_progress: pbar.update(nbytes)
                f.write(chunk)
        except requests.exceptions.ConnectionError as e:
            print(f'\n Download of {url} has failed after {retries} retries.\nError: {e}')
            return False
    return True

def download(url, fname=None, ext='.tgz'):
    "Download `url` to destination `fname`."
    if fname is None:
        fname = Path(f"{url.split('/')[-1]}{ext}")
    os.makedirs(fname.parent, exist_ok=True)
    if not fname.exists():
        print(f'Downloading {url}')
        if not download_url(f'{url}{ext}', fname):
            return None
    return fname
