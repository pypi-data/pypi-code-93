import os
import tempfile
import textwrap

from pathlib import Path

import configuration.helpers as conf
import pytest

from seeq.base.system import human_readable_byte_count
from seeq.base import system


@pytest.mark.unit
def test_human_readable_byte_count_base_ten():
    '''
    Make sure we get the same results as SystemInfoTest#testHumanReadableByteCountBaseTen
    '''
    assert human_readable_byte_count(0, False, False) == '0 B'
    assert human_readable_byte_count(10, False, False) == '10 B'
    assert human_readable_byte_count(900, False, False) == '900 B'
    assert human_readable_byte_count(999, False, False) == '999 B'

    assert human_readable_byte_count(1000, False, False) == '1.00 KB'
    assert human_readable_byte_count(2000, False, False) == '2.00 KB'
    assert human_readable_byte_count(1000 * 1000 - 10, False, False) == '999.99 KB'

    assert human_readable_byte_count(1000 * 1000, False, False) == '1.00 MB'
    assert human_readable_byte_count(50 * 1000 * 1000, False, False) == '50.00 MB'
    assert human_readable_byte_count(1000 * 1000 * 1000 - 10000, False, False) == '999.99 MB'

    assert human_readable_byte_count(1000 * 1000 * 1000, False, False) == '1.00 GB'
    assert human_readable_byte_count(50 * 1000 * 1000 * 1000, False, False) == '50.00 GB'
    assert human_readable_byte_count(1000 * 1000 * 1000 * 1000 - 10000000, False, False) == '999.99 GB'

    assert human_readable_byte_count(1000 * 1000 * 1000 * 1000, False, False) == '1.00 TB'
    assert human_readable_byte_count(50 * 1000 * 1000 * 1000 * 1000, False, False) == '50.00 TB'
    assert human_readable_byte_count(1000 * 1000 * 1000 * 1000 * 1000 - 1e10, False, False) == '999.99 TB'

    assert human_readable_byte_count(1000 * 1000 * 1000 * 1000 * 1000, False, False) == '1.00 PB'
    assert human_readable_byte_count(50 * 1000 * 1000 * 1000 * 1000 * 1000, False, False) == '50.00 PB'
    assert human_readable_byte_count(1000 * 1000 * 1000 * 1000 * 1000 * 1000 - 1e13, False, False) == '999.99 PB'

    assert human_readable_byte_count(1000 * 1000 * 1000 * 1000 * 1000 * 1000, False, False) == '1.00 EB'
    assert human_readable_byte_count(50 * 1000 * 1000 * 1000 * 1000 * 1000 * 1000, False, False) == '50.00 EB'
    assert human_readable_byte_count(1000 * 1000 * 1000 * 1000 * 1000 * 1000 * 1000 - 1e16, False, False) == '999.99 EB'


@pytest.mark.unit
def test_calculate_default_optimal_heap_sizes():
    # cores, physical, appserver, jmvLink, postgres, netLink, renderer, reverse proxy, supervisor, os
    matrix_cols = [
        'Cpu/Count',
        'Memory/System/Total',
        'Memory/Appserver/Size',
        'Memory/JvmLink/Size',
        'Memory/Postgres/Size',
        'Memory/NetLink/Size',
        'Memory/Renderer/Size',
        'Memory/ReverseProxy/Size',
        'Memory/Supervisor/Size',
        'Memory/OperatingSystem/Size'
    ]

    test_matrix = [
        # 64-bit, 8 cpu cores for screenshot purposes
        # P  Total Appsr JvmL PG   NetL Rend Proxy Sup OS
        [8, 4000, 1000, 250, 2250, 250, 500, 100, 300, 250],
        [8, 8000, 2850, 500, 2250, 500, 1000, 100, 300, 500],
        [8, 12000, 5600, 750, 2250, 750, 1500, 100, 300, 750],
        [8, 16000, 7608, 1000, 2992, 1000, 2000, 100, 300, 1000],
        [8, 32000, 15616, 2000, 5984, 2000, 4000, 100, 300, 2000],
        [8, 64000, 35632, 4000, 11968, 4000, 4000, 100, 300, 4000],
        [8, 128000, 75664, 8000, 23936, 8000, 4000, 100, 300, 8000],
        [8, 256000, 155728, 16000, 47872, 16000, 4000, 100, 300, 16000],

        # 64-bit, 64 cpu cores for screenshot purposes
        [64, 4000, 1000, 250, 2250, 250, 500, 800, 300, 250],
        [64, 8000, 2150, 500, 2250, 500, 1000, 800, 300, 500],
        [64, 12000, 4900, 750, 2250, 750, 1500, 800, 300, 750],
        [64, 16000, 6908, 1000, 2992, 1000, 2000, 800, 300, 1000],
        [64, 32000, 14916, 2000, 5984, 2000, 4000, 800, 300, 2000],
        [64, 64000, 30932, 4000, 11968, 4000, 8000, 800, 300, 4000],
        [64, 128000, 62964, 8000, 23936, 8000, 16000, 800, 300, 8000],
        [64, 256000, 127028, 16000, 47872, 16000, 32000, 800, 300, 16000],
        [64, 512000, 287156, 32000, 95744, 32000, 32000, 800, 300, 32000],
    ]

    def get_heap_sizes(cpu, memory):
        conf.set_option('Cpu/Count', cpu, '')
        conf.set_option('Memory/System/Total', memory, '')

        return [conf.get_option(path) for path in matrix_cols]

    with conf.overriding_config({path: None for path in matrix_cols}):
        actual_matrix = [get_heap_sizes(cpu, memory) for [cpu, memory, *_] in test_matrix]

    # # Uncomment the following to help with updating the test
    # import pprint
    # print(pprint.pformat(actual_matrix))
    # assert False

    assert actual_matrix == test_matrix


@pytest.mark.unit
def test_replace_in_file():
    with tempfile.TemporaryDirectory() as temp:
        service_file = os.path.join(temp, f'bogus.service')
        if not os.path.exists(service_file):
            with open(service_file, 'w') as f:
                f.write(textwrap.dedent(f"""
                    [Service]
                    Type=simple
                    User=mark
                    ExecStart=/opt/seeq/seeq start --from-service
                    ExecStop=/opt/seeq/seeq stop
                    Restart=on-failure

                    [Install]
                    WantedBy=multi-user.target
                """))

        system.replace_in_file(service_file, [
            (r'User=.*', 'User=alan'),
            (r'ExecStart=.*', 'ExecStart=/stuff/seeq start --from-service'),
            (r'ExecStop=.*', 'ExecStop=/stuff/seeq stop')
        ])

        with open(service_file, 'r') as f:
            content = f.read()
            assert 'User=alan' in content
            assert 'ExecStart=/stuff/seeq start --from-service' in content
            assert 'ExecStop=/stuff/seeq stop' in content


@pytest.mark.unit
def test_copy_tree_exclude_folder_relative_path():
    # It was discovered in CRAB-20621 that robocopy's /XD flag to exclude directories wasn't working for relative
    # paths to subdirectories. This tests system#copy_tree to be compatible with non-Windows systems.
    # See https://superuser.com/a/690842 and follow-up comments
    with tempfile.TemporaryDirectory() as src:
        tree = TestDirectoryTree(src)
        with tempfile.TemporaryDirectory() as dest:
            system.copytree(src, dest, exclude=tree.exclude)

            all_root_contents = os.listdir(dest)
            # Destination should only have KeepParent and KeepMe.txt
            assert len(all_root_contents) == 2
            assert str(tree.keep_parent_dir_relative) in all_root_contents
            assert tree.root_keep_file_name in all_root_contents

            # Destination should have only KeepParent/KeepMe subdir
            all_subdirs = os.listdir(dest / tree.keep_parent_dir_relative)
            assert len(all_subdirs) == 1
            assert tree.keep_subdir_name in all_subdirs


class TestDirectoryTree():
    def __init__(self, root):
        self.root = root
        self.keep_parent_dir_relative = Path('KeepParent')
        self.keep_subdir_name = 'KeepMe'
        self.exclude_subdir_name = 'ExcludeMe'
        self.exclude_parent_dir_relative = Path('ExcludeParent')

        self.root_keep_file_name = 'KeepMe.txt'
        self.root_exclude_file_name = 'ExcludeMe.txt'

        self.keep_subdir_relative = self.keep_parent_dir_relative / self.keep_subdir_name
        self.exclude_subdir_relative = self.keep_parent_dir_relative / self.exclude_subdir_name

        self.exclude = [str(self.exclude_parent_dir_relative), str(self.exclude_subdir_relative),
                        self.root_exclude_file_name]

        self._create_tree()

    def _create_tree(self):
        # tmpDir
        # |
        # ---- KeepMe.txt
        # -----ExcludeMe.txt
        # ---- ExcludeParent
        # ---- KeepParent
        #          |
        #          ----- KeepMe
        #          |
        #          ----- ExcludeMe
        os.makedirs(self.root / self.keep_subdir_relative)
        os.makedirs(self.root / self.exclude_parent_dir_relative)
        os.makedirs(self.root / self.exclude_subdir_relative)

        open(Path(self.root) / self.root_keep_file_name, 'a').close()
        open(Path(self.root) / self.root_exclude_file_name, 'a').close()


def main(cpu_count, total_memory_mb):
    memory_configurations = [
        'Cpu/Count',
        'Memory/System/Total',
        'Memory/Appserver/Size',
        'Memory/JvmLink/Size',
        'Memory/Postgres/Size',
        '   Database/Postgres/SharedBuffers',
        '   Database/Postgres/EffectiveCacheSize',
        '   Database/Postgres/WorkMem',
        '   Database/Postgres/MaintenanceWorkMem',
        'Memory/NetLink/Size',
        'Memory/Renderer/Size',
        'Memory/ReverseProxy/Size',
        'Memory/Supervisor/Size',
        'Memory/OperatingSystem/Size'
    ]
    conf.set_option('Cpu/Count', cpu_count, '')
    conf.set_option('Memory/System/Total', total_memory_mb, '')
    print()
    for path in memory_configurations:
        print("%s%s" % (path.ljust(40, ' '), str(conf.get_option(path.lstrip())).rjust(8, ' ')))

    conf.unset_option('Cpu/Count')
    conf.unset_option('Memory/System/Total')


if __name__ == "__main__":
    main(64, 32768)
