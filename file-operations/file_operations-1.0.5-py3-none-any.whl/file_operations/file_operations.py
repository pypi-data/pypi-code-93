import os, shutil

def new_method():
    pass

def set_bytes(src_file, offset, byte_str):
    if not os.path.isfile(src_file): return False
    file_size = os.path.getsize(src_file)
    whence = 1 if file_size - offset >= offset else 2
    f = open(src_file, 'ab')
    f.seek(offset, whence)
    f.write(byte_str)
    f.close()
    return True

def read_bytes(src_file, offset, limit):
    if not os.path.isfile(src_file): return False
    file_size = os.path.getsize(src_file)
    if file_size < offset + limit: return False
    whence = 1 if file_size - offset >= offset else 2
    f = open(src_file, 'rb')
    f.seek(offset, whence)
    result = f.read(limit)
    f.close()
    return result

def copy_file(src_file, dest_file):
    if not os.path.isfile(src_file): return False
    s = open(src_file,'rb').read()
    f_out = open(dest_file, 'wb')
    f_out.write(s)
    f_out.close()
    return True

def write_file(dest_file, data, mode='w', overwrite=False):
    if not overwrite and os.path.isfile(dest_file): return False
    f = open(dest_file, mode)
    f.write(data)
    f.close()
    return True

def move_file(src_file, dest_file):
    if not os.path.isfile(src_file): return False
    os.rename(src_file, dest_file)
    return True

def remove_file(src_file):
    if not os.path.isfile(src_file): return False
    os.remove(src_file)
    return True

def create_dir(dest_dir):
    # if os.path.isdir(dest_dir): raise Exception(f'Directory: {dest_dir} already exists')
    if os.path.isdir(dest_dir): return False
    os.mkdir(dest_dir)
    return True

def copy_dir(src_dir, dest_dir, overwrite=False):
    # if not os.path.isdir(dest_dir): os.mkdir(dest_dir)
    if overwrite: shutil.rmtree(dest_dir)
    result = shutil.copytree(src_dir, dest_dir, copy_function = shutil.copy)
    return True

def move_dir(src_dir, dest_dir):
    if not os.path.isdir(src_dir): return False
    shutil.move(src_dir, dest_dir)
    return True

def remove_dir(dest_dir):
    # if not os.path.isdir(dest_dir): raise Exception(f'Directory: {dest_dir} does not exist')
    if not os.path.isdir(dest_dir): return False
    shutil.rmtree(dest_dir)
    return True

class buffered_reader:
    def __init__(self, file_name, buffer_size, mode='rb'):
        if not os.path.isfile(file_name): raise Exception(f'File: {file_name} does not exist')
        self.file_name = file_name
        self.buffer_size = buffer_size
        self.file_size = os.path.getsize(file_name)
        self.num_batches = self.file_size // self.buffer_size
        self.counter = 0
        self.fp = open(file_name, mode)
        self.y = 1 if self.file_size % self.buffer_size > 0 else 0

    def __repr__(self):
        return f'buffered_reader(file_name={self.file_name}, buffer_size={self.buffer_size})'

    def has_next(self):
        return self.counter < (self.num_batches + self.y)

    def read(self):
        if not self.has_next(): return None
        self.counter += 1
        if self.counter <= self.num_batches:
            return self.fp.read(self.buffer_size)
        return self.fp.read(self.file_size % self.buffer_size)

    def close(self):
        self.fp.close()
