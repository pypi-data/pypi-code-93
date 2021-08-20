import codecs
import datetime
import pathlib
import mimetypes
import multiprocessing
import logging
import zipfile

import multidict

try:
    import pyexiv2
except ImportError:
    pyexiv2 = None

try:
    import PIL
    import PIL.Image
except ImportError:
    PIL = None

try:
    import mutagen
except ImportError:
    mutagen = None

try:
    import pdfminer
    from pdfminer.pdfparser import PDFParser
    from pdfminer.pdfdocument import PDFDocument
except ImportError:
    pdfminer = None

from metaindex.opf import parse_opf


def to_utf8(raw):
    if isinstance(raw, str):
        return raw
    encoding = None
    skip = 1

    if raw.startswith(codecs.BOM_UTF8):
        encoding = 'utf-8'
    elif raw.startswith(codecs.BOM_UTF16_BE):
        encoding = 'utf-16-be'
    elif raw.startswith(codecs.BOM_UTF16_LE):
        encoding = 'utf-16-le'
    elif raw.startswith(codecs.BOM_UTF32_BE):
        encoding = 'utf-32-be'
    elif raw.startswith(codecs.BOM_UTF32_LE):
        encoding = 'utf-32-le'
    else:
        # just best efford
        encoding = 'utf-8'
        skip = 0

    try:
        text = str(raw, encoding=encoding).strip()
        return text[skip:]  # drop the BOM, if applicable
    except UnicodeError:
        pass
    return None


def meta_from_pyexiv2(filename):
    """Extract metadata from `filename` using pyexiv2"""
    if pyexiv2 is None:
        return {}

    logging.debug(f"[image, exiv2] processing {filename.name}")

    try:
        meta = pyexiv2.core.Image(str(filename))
    except:
        return {}

    result = multidict.MultiDict()
    try:
        result.extend(meta.read_exif())
    except:
        pass

    try:
        result.extend(meta.read_iptc())
    except:
        pass

    try:
        result.extend(meta.read_xmp())
    except:
        pass

    meta.close()
    return result


def meta_from_mutagen(filename):
    """Extract metadata from `filename` using mutagen"""
    if mutagen is None:
        return {}

    logging.debug(f"[mutagen] processing {filename.name}")

    try:
        meta = mutagen.File(filename, easy=True)
    except:
        return {}

    result = multidict.MultiDict()

    if meta is not None:
        for key in meta.keys():
            result.extend([('id3.' + key, value) for value in meta[key]])
        if hasattr(meta, 'info') and hasattr(meta.info, 'length'):
            result.add('length', meta.info.length)

    return result


def meta_from_pillow(filename):
    """Extract metadata from `filename` using pillow"""
    if PIL is None:
        return {}

    logging.debug(f"[image, pillow] processing {filename.name}")

    try:
        meta = PIL.Image.open(filename)
    except:
        return {}

    result = {}
    if meta is not None:
        result = {'resolution': "{}x{}".format(*meta.size)}
        meta.close()

    return result


PDF_METADATA = ('title', 'author', 'creator', 'producer', 'keywords',
                'manager', 'status', 'category', 'moddate', 'creationdate',
                'subject')


def meta_from_pdf(filename):
    """Extract metadata from `filename` using pdfminer"""
    if pdfminer is None:
        return {}

    logging.debug(f"[pdf] processing {filename.name}")

    try:
        fp = open(filename, 'rb')
    except OSError:
        return {}

    try:
        parser = PDFParser(fp)
        pdf = PDFDocument(parser)
    except:
        fp.close()
        return {}

    result = multidict.MultiDict()

    if len(pdf.info) > 0:
        for field in pdf.info[0].keys():
            if not isinstance(field, str):
                logging.debug(f"PDF: Unexpected type for info field key: {type(field)}")
                continue
            if field.lower() not in PDF_METADATA:
                logging.debug(f"PDF: Ignoring {field} key")
                continue

            raw = pdf.info[0][field]
            value = None

            if isinstance(raw, bytes):
                value = to_utf8(raw)
                if value is None:
                    continue
            elif isinstance(raw, str) and len(raw.strip()) > 0:
                value = raw.strip()
            else:
                continue

            if field.endswith('Date') and value.startswith(':'):
                try:
                    value = datetime.datetime.strptime(value[:15], ':%Y%m%d%H%M%S')
                except ValueError:
                    continue

            if value is not None:
                result['pdf.' + field] = value

    fp.close()
    return result


def meta_from_epub(filename):
    logging.debug(f"[epub] processing {filename.name}")

    with zipfile.ZipFile(filename) as fp:
        files = fp.namelist()
        if 'content.opf' in files:
            with fp.open('content.opf') as contentfp:
                return parse_opf(contentfp.read(), '')
    return {}


def get_metadata(filename):
    """Extract metadata from the file at `filename`"""
    assert isinstance(filename, pathlib.Path)

    stat = filename.stat()
    suffix = filename.suffix[1:]
    mimetype, _ = mimetypes.guess_type(filename, strict=False)
    info = multidict.MultiDict({'size': stat.st_size,
                                'filename': filename.name,
                                'last_accessed': datetime.datetime.fromtimestamp(stat.st_atime),
                                'last_modified': datetime.datetime.fromtimestamp(stat.st_mtime)})

    if mimetype is None:
        return info

    info['mimetype'] = mimetype

    if mimetype.startswith('image/'):
        info.extend(meta_from_pyexiv2(filename))
        info.extend(meta_from_pillow(filename))

    elif mimetype.startswith('video/'):
        info.extend(meta_from_pyexiv2(filename))
        info.extend(meta_from_mutagen(filename))

    elif mimetype.startswith('audio/'):
        info.extend(meta_from_mutagen(filename))

    elif mimetype == 'application/pdf':
        info.extend(meta_from_pdf(filename))

    elif mimetype == 'application/epub+zip':
        info.extend(meta_from_epub(filename))

    else:
        logging.info(f"Don't know how to handle mimetype: {mimetype}")

    return info


def indexer(filenames):
    """Takes a list of filenames and tries to extract the metadata for all
    
    Returns a dictionary mapping filename to a dictionary with the metadata.
    """
    result = {}

    for filename in filenames:
        if not isinstance(filename, pathlib.Path):
            filename = pathlib.Path(filename)

        if not filename.is_file():
            continue

        result[filename] = get_metadata(filename)

    return result


def find_files(paths, recursive=True):
    """Find all files in these paths"""
    if not isinstance(paths, list):
        paths = [paths]

    pathqueue = list(paths)
    filenames = []

    while len(pathqueue) > 0:
        path = pathqueue.pop(0)

        if not isinstance(path, pathlib.Path):
            path = pathlib.Path(path)

        if not path.exists():
            continue

        for item in path.iterdir():
            if item.is_dir() and recursive:
                pathqueue.append(item)
                continue

            if item.is_file():
                filenames.append(item)

    return filenames


def tuplice(item):
    return item, get_metadata(item)


def index_files(files, processes=None):
    """Run indexer on all files"""
    metadata = {}
    then = datetime.datetime.now()
    if processes == 1:
        metadata = indexer(files)
    else:
        with multiprocessing.Pool(processes) as pool:
            metadata = dict(pool.map(tuplice, files))
    logging.info(f"Processed {len(metadata)} files in {datetime.datetime.now() - then}")

    return metadata


if __name__ == '__main__':
    import sys

    logging.basicConfig(level=logging.DEBUG)

    index = index_files([pathlib.Path(i) for i in sys.argv[1:]])

