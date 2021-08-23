# -*- coding: utf-8 -*-

import copy
import sys

import six
from mock import PropertyMock, patch

from utils import CommandTestCase


def thread_pool_map(func, iterable):
    return [func(item) for item in iterable]


class TestWatchModuleBuilds(CommandTestCase):
    """Test Commands.module_watch_build"""

    require_test_repos = False

    def setUp(self):
        super(TestWatchModuleBuilds, self).setUp()
        self.cmd = self.make_commands(path='/path/to/repo')

        self.p_ThreadPool = patch('pyrpkg.ThreadPool')
        self.mock_ThreadPool = self.p_ThreadPool.start()
        self.mock_ThreadPool.return_value.map = thread_pool_map

        self.p_kojiweburl = patch('pyrpkg.Commands.kojiweburl',
                                  new_callable=PropertyMock,
                                  return_value='http://koji.example.com/')
        self.p_kojiweburl.start()

        self.p_sleep = patch('time.sleep')
        self.p_sleep.start()

    def tearDown(self):
        self.p_sleep.stop()
        self.p_kojiweburl.stop()
        self.p_ThreadPool.stop()
        super(TestWatchModuleBuilds, self).tearDown()

    @patch('pyrpkg.Commands.module_get_build')
    @patch('pyrpkg.Commands.load_kojisession')
    def watch_builds(self, fake_builds_info, watch_ids, expected_output,
                     load_kojisession, module_get_build):
        def side_effect(build_id):
            br_list = fake_builds_info[build_id]
            if br_list[0] < len(br_list) - 1:
                br_list[0] += 1
            # If a module build reaches the last state, either ready or
            # failed, when any time to query this module, this last state
            # build will be returned.
            #
            # Note that: watch method modifies got build info mapping. So,
            # return a copy to ensure fake data is not modified.
            return copy.deepcopy(br_list[br_list[0]])

        module_get_build.side_effect = side_effect

        with patch.object(self.cmd, 'module_api_url', new='http://mbs/'):
            with patch('sys.stdout', new=six.moves.StringIO()):
                self.cmd.module_watch_build(watch_ids)

                output = sys.stdout.getvalue()
                self.assertEqual(expected_output, output)

    def test_all_builds_done_already(self):
        fake_builds_info = {
            1: [0, {
                'id': 1, 'name': 'modulea', 'stream': 'master',
                'version': '1', 'context': '1234',
                'state': 5, 'state_name': 'ready',
                'koji_tag': 'module-moduleb-master-v-c1',
                'tasks': {
                    'rpms': {
                        'pkg': {
                            'nvr': 'pkg-1.0-1.fc28',
                            'task_id': 1000,
                            'state': 1,
                        }
                    }
                }
            }],
            2: [0, {
                'id': 2, 'name': 'moduleb', 'stream': '6',
                'version': '1', 'context': '3456',
                'state': 5, 'state_name': 'ready',
                'koji_tag': 'module-moduleb-6-v-c2',
                'tasks': {
                    'rpms': {
                        'pkg2': {
                            'nvr': 'pkg2-1.0-1.fc28',
                            'task_id': 1001,
                            'state': 1,
                        }
                    }
                }
            }],
            3: [0, {
                'id': 3, 'name': 'modulec', 'stream': 'master',
                'version': '1', 'context': '6789',
                'state': 4, 'state_name': 'failed',
                'state_reason': 'Component build failed.',
                'koji_tag': 'module-moduleb-master-v-c3',
                'tasks': {
                    'rpms': {
                        'pkg3': {
                            'nvr': 'pkg3-1.0-1.fc28',
                            'task_id': 1002,
                            'state': 3,
                        }
                    }
                }
            }],
        }

        expected_output = '''\
[Build #1] modulea-master-1-1234 is in "ready" state.
  Koji tag: module-moduleb-master-v-c1
  Link: http://mbs/module-builds/1
  Components: 1 done, 0 failed
[Build #2] moduleb-6-1-3456 is in "ready" state.
  Koji tag: module-moduleb-6-v-c2
  Link: http://mbs/module-builds/2
  Components: 1 done, 0 failed
[Build #3] modulec-master-1-6789 is in "failed" state.
  Koji tag: module-moduleb-master-v-c3
  Link: http://mbs/module-builds/3
  Components: 0 done, 1 failed
  Reason: Component build failed.
'''
        self.watch_builds(fake_builds_info,
                          list(fake_builds_info.keys()),
                          expected_output)

    def test_watch_common_process(self):
        fake_builds_info = {
            # Module#1: init -> wait -> build -> done -> ready
            1: [
                0,
                {
                    'id': 1, 'name': 'modulea', 'stream': 'master',
                    'version': '1', 'context': 'c1',
                    'state': 0, 'state_name': 'init',
                    'koji_tag': 'module-modulea-master-1-c1',
                    'tasks': {}
                },
                {
                    'id': 1, 'name': 'modulea', 'stream': 'master',
                    'version': '1', 'context': 'c1',
                    'state': 1, 'state_name': 'wait',
                    'koji_tag': 'module-modulea-master-1-c1',
                    'tasks': {
                        'rpms': {
                            'pkg': {'nvr': None, 'task_id': 1000, 'state': None}
                        }
                    }
                },
                {
                    'id': 1, 'name': 'modulea', 'stream': 'master',
                    'version': '1', 'context': 'c1',
                    'state': 2, 'state_name': 'build',
                    'koji_tag': 'module-modulea-master-1-c1',
                    'tasks': {
                        'rpms': {
                            'pkg': {'nvr': None, 'task_id': 1000, 'state': 0},
                        }
                    }
                },
                {
                    'id': 1, 'name': 'modulea', 'stream': 'master',
                    'version': '1', 'context': 'c1',
                    'state': 3, 'state_name': 'done',
                    'koji_tag': 'module-modulea-master-1-c1',
                    'tasks': {
                        'rpms': {
                            'pkg': {
                                'nvr': 'pkg-1.0-1.fc28',
                                'task_id': 1000,
                                'state': 1,
                            }
                        }
                    }
                },
                {
                    'id': 1, 'name': 'modulea', 'stream': 'master',
                    'version': '1', 'context': 'c1',
                    'state': 5, 'state_name': 'ready',
                    'koji_tag': 'module-modulea-master-1-c1',
                    'tasks': {
                        'rpms': {
                            'pkg': {
                                'nvr': 'pkg-1.0-1.fc28',
                                'task_id': 1000,
                                'state': 1,
                            }
                        }
                    }
                },
            ],
            # Module#2: wait -> failed
            2: [
                0,
                {
                    'id': 2, 'name': 'moduleb', 'stream': '6',
                    'version': '1', 'context': 'c2',
                    'state': 1, 'state_name': 'wait',
                    'koji_tag': 'module-moduleb-6-1-c2',
                    'tasks': {
                        'rpms': {
                            'pkg2': {'nvr': None, 'task_id': 2000, 'state': None}
                        }
                    }
                },
                {
                    'id': 2, 'name': 'moduleb', 'stream': '6',
                    'version': '1', 'context': 'c2',
                    'state': 4, 'state_name': 'failed',
                    'state_reason': 'Build failed.',
                    'koji_tag': 'module-moduleb-6-1-c2',
                    'tasks': {
                        'rpms': {
                            'pkg2': {
                                'nvr': 'pkg2-1.0-1.fc28',
                                'task_id': 2000,
                                'state': 3,
                            }
                        }
                    }
                },
            ],
            # Module#3: build -> build (some build doesn't finish yet) -> failed
            # With some failed component build.
            3: [
                0,
                {
                    'id': 3, 'name': 'perl', 'stream': '5.24',
                    'version': '1', 'context': 'c3',
                    'state': 2, 'state_name': 'build',
                    'koji_tag': 'module-perl-5.24-1-c3',
                    'tasks': {
                        'rpms': {
                            'perl': {'nvr': None, 'task_id': 1000, 'state': 0},
                            'perl-CPAN': {'nvr': None, 'task_id': 1000, 'state': 0},
                        }
                    }
                },
                {
                    'id': 3, 'name': 'perl', 'stream': '5.24',
                    'version': '1', 'context': 'c3',
                    'state': 2, 'state_name': 'build',
                    'koji_tag': 'module-perl-5.24-1-c3',
                    'tasks': {
                        'rpms': {
                            'perl': {'nvr': None, 'task_id': 1000, 'state': 0},
                            'perl-CPAN': {
                                'nvr': 'perl-CPAN-2.16-1.module_1688+afbe1536',
                                'task_id': 1000,
                                'state': 3
                            },
                        }
                    }
                },
                {
                    'id': 3, 'name': 'perl', 'stream': '5.24',
                    'version': '1', 'context': 'c3',
                    'state': 2, 'state_name': 'failed',
                    'state_reason': 'Component build failed.',
                    'koji_tag': 'module-perl-5.24-1-c3',
                    'tasks': {
                        'rpms': {
                            'perl': {
                                'nvr': 'perl-5.24.4-397.module_1688+afbe1536',
                                'task_id': 1000,
                                'state': 1
                            },
                            'perl-CPAN': {
                                'nvr': 'perl-CPAN-2.16-1.module_1688+afbe1536',
                                'task_id': 1000,
                                'state': 3
                            },
                        }
                    }
                },
            ],
        }

        expected_output = '''\
[Build #1] modulea-master-1-c1 is in "init" state.
  Koji tag: module-modulea-master-1-c1
  Link: http://mbs/module-builds/1
[Build #2] moduleb-6-1-c2 is in "wait" state.
  Koji tag: module-moduleb-6-1-c2
  Link: http://mbs/module-builds/2
  Components: 1
[Build #3] perl-5.24-1-c3 is in "build" state.
  Koji tag: module-perl-5.24-1-c3
  Link: http://mbs/module-builds/3
  Components: [0%]: 2 in building, 0 done, 0 failed
    Building:
      - perl
        http://koji.example.com/taskinfo?taskID=1000
      - perl-CPAN
        http://koji.example.com/taskinfo?taskID=1000
[Build #1] modulea-master-1-c1 is in "wait" state.
  Components: 1
[Build #2] moduleb-6-1-c2 is in "failed" state.
  Components: 0 done, 1 failed
  Reason: Build failed.
[Build #3] perl-5.24-1-c3 is in "build" state.
  Components: [50%]: 1 in building, 0 done, 1 failed
    Building:
      - perl
        http://koji.example.com/taskinfo?taskID=1000
    Failed:
      - perl-CPAN-2.16-1.module_1688+afbe1536
        http://koji.example.com/taskinfo?taskID=1000
[Build #1] modulea-master-1-c1 is in "build" state.
  Components: [0%]: 1 in building, 0 done, 0 failed
    Building:
      - pkg
        http://koji.example.com/taskinfo?taskID=1000
[Build #3] perl-5.24-1-c3 is in "failed" state.
  Components: 1 done, 1 failed
  Reason: Component build failed.
[Build #1] modulea-master-1-c1 is in "done" state.
  Components: 1 done, 0 failed
[Build #1] modulea-master-1-c1 is in "ready" state.
  Components: 1 done, 0 failed
'''
        self.watch_builds(fake_builds_info,
                          list(fake_builds_info.keys()),
                          expected_output)

    def test_no_building_task_if_module_build_is_in_build_state(self):
        fake_builds_info = {
            1: [
                0,
                {
                    'id': 1, 'name': 'perl', 'stream': '5.24',
                    'version': '1', 'context': 'c3',
                    'state': 1, 'state_name': 'wait',
                    'koji_tag': 'module-perl-5.24-1-c3',
                    'tasks': {
                        'rpms': {
                            'perl': {'nvr': None, 'task_id': None, 'state': None},
                            'perl-CPAN': {'nvr': None, 'task_id': None, 'state': None},
                        }
                    }
                },
                {
                    'id': 1, 'name': 'perl', 'stream': '5.24',
                    'version': '1', 'context': 'c3',
                    'state': 2, 'state_name': 'build',
                    'koji_tag': 'module-perl-5.24-1-c3',
                    'tasks': {
                        'rpms': {
                            'perl': {'nvr': None, 'task_id': 1000, 'state': 0},
                            'perl-CPAN': {'nvr': None, 'task_id': 1001, 'state': 0},
                        }
                    }
                },
                {
                    'id': 1, 'name': 'perl', 'stream': '5.24',
                    'version': '1', 'context': 'c3',
                    'state': 2, 'state_name': 'build',
                    'koji_tag': 'module-perl-5.24-1-c3',
                    'tasks': {
                        'rpms': {
                            'perl': {
                                'nvr': 'perl-5.24.4-397.module_1688+afbe1536',
                                'task_id': 1000,
                                'state': 1,
                            },
                            'perl-CPAN': {
                                'nvr': 'perl-CPAN-2.16-1.module_1688+afbe1536',
                                'task_id': 1001,
                                'state': 3,
                            },
                        }
                    }
                },
                {
                    'id': 1, 'name': 'perl', 'stream': '5.24',
                    'version': '1', 'context': 'c3',
                    'state': 4, 'state_name': 'failed',
                    'state_reason': 'Component build failed.',
                    'koji_tag': 'module-perl-5.24-1-c3',
                    'tasks': {
                        'rpms': {
                            'perl': {
                                'nvr': 'perl-5.24.4-397.module_1688+afbe1536',
                                'task_id': 1000,
                                'state': 1,
                            },
                            'perl-CPAN': {
                                'nvr': 'perl-CPAN-2.16-1.module_1688+afbe1536',
                                'task_id': 1001,
                                'state': 3,
                            },
                        }
                    }
                },
            ]
        }

        expected_output = '''\
[Build #1] perl-5.24-1-c3 is in "wait" state.
  Koji tag: module-perl-5.24-1-c3
  Link: http://mbs/module-builds/1
  Components: 2
[Build #1] perl-5.24-1-c3 is in "build" state.
  Components: [0%]: 2 in building, 0 done, 0 failed
    Building:
      - perl
        http://koji.example.com/taskinfo?taskID=1000
      - perl-CPAN
        http://koji.example.com/taskinfo?taskID=1001
[Build #1] perl-5.24-1-c3 is in "build" state.
  Components: [100%]: 0 in building, 1 done, 1 failed
    No building task.
    Failed:
      - perl-CPAN-2.16-1.module_1688+afbe1536
        http://koji.example.com/taskinfo?taskID=1001
[Build #1] perl-5.24-1-c3 is in "failed" state.
  Components: 1 done, 1 failed
  Reason: Component build failed.
'''
        self.watch_builds(fake_builds_info,
                          list(fake_builds_info.keys()),
                          expected_output)
