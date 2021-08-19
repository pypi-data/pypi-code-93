import file_operations as file_ops

# set_bytes(src_file, offset, bytes)
# read_bytes(src_file, offset, limit)
#
# copy_file(src_file, dest_file)
# write_file(dest_file, data, mode ='w', overwrite = False)
# move_file(src_file, dest_file)
# remove_file(src_file)
#
# create_dir(dest_dir)
# copy_dir(src_dir, dest_dir, overwrite = False)
# move_dir(src_dir, dest_dir)
# remove_dir(dest_dir)
#
# buffered_reader(file_name, buffer_size, mode ='rb'):
# buffered_reader.has_next()
# buffered_reader.read()
# buffered_reader.close()

def populate_dir(dirs, dir_files, index, limit):
    data = 'a' * 10
    file_ops.create_dir(dirs[index])
    for i in range(0, limit):
        file_ops.write_file(dir_files[index][i], data, mode ='w', overwrite = True)
        data += 'a' * 10

def test_file_operations():
    N = 10
    N2 = 4
    buffer_size = 1200
    prefix = '../test_space'
    files = [f'{prefix}/f{i}' for i in range(0, N)]
    dir_files = [[f'{prefix}/d{i}/f{j}' for j in range(0, N2)] for i in range(0, N)]
    dirs = [f'{prefix}/d{i}' for i in range(0, N)]
    data = 'abc' * 4000 + 'a'
    offset, limit = 4, 10
    byte_str = ('x' * 10).encode()

    op = file_ops.write_file(files[0], data, mode ='w', overwrite = True); assert op

    # op = file_ops.set_bytes(files[0], offset, byte_str); assert op
    byte_str2 = file_ops.read_bytes(files[0], offset, limit); assert len(byte_str2) == limit
    # print(byte_str2)

    op = file_ops.copy_file(files[0], files[1]); assert op
    op = file_ops.move_file(files[0], files[2]); assert op
    op = file_ops.remove_file(files[1]); assert op

    # for i in [0, 1, 2]: file_ops.remove_dir(dirs[i])
    populate_dir(dirs, dir_files, 0, 4)

    op = file_ops.create_dir(dirs[0]); assert not op
    op = file_ops.copy_dir(dirs[0], dirs[1]); assert op
    op = file_ops.move_dir(dirs[0], dirs[2]); assert op
    op = file_ops.remove_dir(dirs[1]); assert op
    count = 0
    br = file_ops.buffered_reader(files[2], buffer_size)
    s = ''
    while br.has_next():
        s = br.read()
        # print(len(s), count, len(data) / buffer_size)
        if count < (len(data) // buffer_size): assert len(s) == buffer_size
        count += 1
    assert len(s) == len(data) % buffer_size
    br.close()
    x = len(data) // buffer_size if len(data) % buffer_size == 0 else (len(data) // buffer_size) + 1
    assert count == x

    op = file_ops.remove_file(files[2]); assert op
    op = file_ops.remove_dir(dirs[2]); assert op
    # assert False

def p1():
    # print(dir(file_ops))
    test_file_operations()
    pass

def main():
    p1()
    pass

if __name__ == '__main__':
    main()
