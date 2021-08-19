'''Test
'''
from zipfile import ZipFile, ZipInfo, ZIP_STORED, struct, ZIP64_LIMIT, structCentralDir, stringCentralDir
import sys
from types import MethodType

_FHF_HAS_DATA_DESCRIPTOR = 0x8
dataDescriptorSignature = 0x08074b50

def _get_data_descriptor_size(self, zinfo):
    if self.mode not in ("r", "a"):
        raise RuntimeError('to read the data descriptor requires mode "r" or "a"')

    if not zinfo.flag_bits & _FHF_HAS_DATA_DESCRIPTOR:
        return 0

    original_fp = self.fp.tell()
    data_descriptor_fp = zinfo.header_offset + len(zinfo.FileHeader()) + zinfo.compress_size
    self.fp.seek(data_descriptor_fp)
    
    sig_or_not_bin = self.fp.read(4)
    sig_or_not = struct.unpack('<L', sig_or_not_bin)
    self.fp.seek(original_fp)
    
    if sig_or_not == dataDescriptorSignature:
        return 16
    else:
        return 12

def remove(self, member):
    """Remove a file from the archive. Only works if the ZipFile was opened
    with mode 'a'."""

    if "a" not in self.mode:
        raise RuntimeError('remove() requires mode "a"')
    if not self.fp:
        raise RuntimeError(
                "Attempt to modify ZIP archive that was already closed")
    
    # Make sure we have an info object
    if isinstance(member, ZipInfo):
        # 'member' is already an info object
        zinfo = member
    else:
        # Get info object for member
        zinfo = self.getinfo(member)

    # To remove the member we need its size and location in the archive
    fname = zinfo.filename
    fileofs = zinfo.header_offset
    zlen = len(zinfo.FileHeader()) + zinfo.compress_size + self._get_data_descriptor_size(zinfo)

    # Modify all the relevant file pointers
    for info in self.infolist():
        if info.header_offset > fileofs:
            info.header_offset = info.header_offset - zlen

    # Remove the zipped data
    self.fp.seek(fileofs + zlen)
    data_after = self.fp.read()
    self.fp.seek(fileofs)
    self.fp.write(data_after)
    new_start_dir = self.start_dir - zlen
    self.fp.seek(new_start_dir)
    self.fp.truncate()

    # Fix class members with state
    self.start_dir = new_start_dir
    self._didModify = True
    self.filelist.remove(zinfo)
    del self.NameToInfo[fname]

def _central_dir_header(self, zinfo):
    dt = zinfo.date_time
    dosdate = (dt[0] - 1980) << 9 | dt[1] << 5 | dt[2]
    dostime = dt[3] << 11 | dt[4] << 5 | (dt[5] // 2)
    extra = []
    if zinfo.file_size > ZIP64_LIMIT \
            or zinfo.compress_size > ZIP64_LIMIT:
        extra.append(zinfo.file_size)
        extra.append(zinfo.compress_size)
        file_size = 0xffffffff
        compress_size = 0xffffffff
    else:
        file_size = zinfo.file_size
        compress_size = zinfo.compress_size

    if zinfo.header_offset > ZIP64_LIMIT:
        extra.append(zinfo.header_offset)
        header_offset = 0xffffffff
    else:
        header_offset = zinfo.header_offset

    extra_data = zinfo.extra
    if extra:
        # Append a ZIP64 field to the extra's
        extra_data = struct.pack(
                '<HH' + 'Q'*len(extra),
                1, 8*len(extra), *extra) + extra_data

        extract_version = max(45, zinfo.extract_version)
        create_version = max(45, zinfo.create_version)
    else:
        extract_version = zinfo.extract_version
        create_version = zinfo.create_version

    try:
        filename, flag_bits = zinfo._encodeFilenameFlags()
        centdir = struct.pack(structCentralDir,
            stringCentralDir, create_version,
            zinfo.create_system, extract_version, zinfo.reserved,
            flag_bits, zinfo.compress_type, dostime, dosdate,
            zinfo.CRC, compress_size, file_size,
            len(filename), len(extra_data), len(zinfo.comment),
            0, zinfo.internal_attr, zinfo.external_attr,
            header_offset)
    except DeprecationWarning:
        print((structCentralDir, stringCentralDir, create_version,
            zinfo.create_system, extract_version, zinfo.reserved,
            zinfo.flag_bits, zinfo.compress_type, dostime, dosdate,
            zinfo.CRC, compress_size, file_size,
            len(zinfo.filename), len(extra_data), len(zinfo.comment),
            0, zinfo.internal_attr, zinfo.external_attr,
            header_offset), file=sys.stderr)
        raise

    return centdir + filename + extra_data + zinfo.comment


def new_zipfile(file
        , mode = "r"
        , compression = ZIP_STORED
        , allowZip64 = True
        , compresslevel = None
    ) -> ZipFile:
    zip_obj = ZipFile(file
        , mode = mode
        , compression = compression
        , allowZip64 = allowZip64
        , compresslevel = compresslevel
    )
    if not hasattr(ZipFile, "remove"):
        zip_obj._get_data_descriptor_size = MethodType(_get_data_descriptor_size, zip_obj)
        zip_obj.remove = MethodType(remove, zip_obj)
        zip_obj._central_dir_header = MethodType(_central_dir_header, zip_obj)

    return zip_obj
