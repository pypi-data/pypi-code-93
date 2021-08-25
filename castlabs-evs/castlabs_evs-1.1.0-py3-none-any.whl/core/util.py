# Copyright 2020, castLabs GmbH

from .error import UnsupportedError, InvalidDataError

from sys import maxsize

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.hashes import Hash, SHA512, SHA1

from macholib import MachO, mach_o

################################################################################

def detect_bin(fh):
  h = fh.peek(512)
  if h[:8] == b'\xcf\xfa\xed\xfe\x07\x00\x00\x01':
    return ('macho', 'darwin', 'x64')
  elif h[:8] == b'\xcf\xfa\xed\xfe\x0C\x00\x00\x01':
    return ('macho', 'darwin', 'arm64')
  elif h[:4] == b'\xca\xfe\xba\xbe':
    return ('macho', 'darwin', 'fat')
  elif h[:2] == b'MZ':
    o = int.from_bytes(h[60:64], byteorder='little')
    if o < len(h):
      s = h[o:o + 6]
      if s == b'\x50\x45\x00\x00\x64\x86':
        return ('pe', 'win32', 'x64')
      elif s == b'\x50\x45\x00\x00\x4c\x01':
        return ('pe', 'win32', 'ia32')
  raise UnsupportedError('Binary type or archtecture not supported')

################################################################################

DEFAULT_HASH_BLOCK = 2 * 1024 * 1024

################################################################################

def hash_macho_wv0(fh, hash_block=DEFAULT_HASH_BLOCK):
  headers = MachO.MachO(fh.name).headers
  hasher = Hash(SHA512(), default_backend())
  for header in headers:
    fh.seek(header.offset, 0)
    start, end = maxsize, 0
    for (lc, segment, sections) in header.commands:
      # The minimum section offset of all load commands is the start of VMP signing part
      if (lc.cmd in (mach_o.LC_SEGMENT_64, mach_o.LC_SEGMENT) and
        segment.segname.startswith(mach_o.SEG_TEXT.encode('utf-8'))):
        for section in sections:
          start = min(start, section.offset)
      # Expect the String Table is at the end of unsigned binary followed by the code
      # signature, so the end of String Table is the end of VMP signing part
      if (mach_o.LC_SYMTAB == lc.cmd):
        end = segment.stroff + segment.strsize
    if (start >= end):
      raise InvalidDataError('Failed to assemble VMP/Mach-O signing body: %d-%d' % (start, end))
    fh.seek(start, 1)
    while start < end:
      data = fh.read(min(end - start, hash_block))
      start += len(data)
      hasher.update(data)
  fh.seek(0, 0)
  return hasher.finalize()

def hash_macho_fat_wv0(fh, hash_block=DEFAULT_HASH_BLOCK):
  headers = MachO.MachO(fh.name).headers
  hashes = []
  for header in headers:
    fh.seek(header.offset, 0)
    start, end = maxsize, 0
    for (lc, segment, sections) in header.commands:
      # The minimum section offset of all load commands is the start of VMP signing part
      if (lc.cmd in (mach_o.LC_SEGMENT_64, mach_o.LC_SEGMENT) and
        segment.segname.startswith(mach_o.SEG_TEXT.encode('utf-8'))):
        for section in sections:
          start = min(start, section.offset)
      # Expect the String Table is at the end of unsigned binary followed by the code
      # signature, so the end of String Table is the end of VMP signing part
      if (mach_o.LC_SYMTAB == lc.cmd):
        end = segment.stroff + segment.strsize
    if (start >= end):
      raise InvalidDataError('Failed to assemble VMP/Mach-O signing body: %d-%d' % (start, end))
    fh.seek(start, 1)
    hasher = Hash(SHA512(), default_backend())
    while start < end:
      data = fh.read(min(end - start, hash_block))
      start += len(data)
      hasher.update(data)
    hashes.append(hasher.finalize())
  fh.seek(0, 0)
  return hashes

def hash_pe_wv0(fh, hash_block=DEFAULT_HASH_BLOCK):
  hasher = Hash(SHA512(), default_backend())
  while True:
    data = fh.read(hash_block)
    if not data: break
    hasher.update(data)
  fh.seek(0, 0)
  return hasher.finalize()

################################################################################
