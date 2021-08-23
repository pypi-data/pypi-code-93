import re
from unittest.mock import patch

from savvihub.cli.constants import WEB_HOST
from savvihub.common.utils import random_string
from tests.conftest import BaseTestCase


class ExperimentTest(BaseTestCase):
    def test_experiment(self):
        result = self.runner.invoke(['experiment', 'list'])
        assert f'There is no experiment in {self.project_name} project.' in result.output

        # Create a dataset
        dataset_name = random_string()
        result = self.runner.invoke(['dataset', 'create', f'{self.organization_name}/{dataset_name}'])
        assert f'Dataset {dataset_name} is created.' in result.output
        assert f'{WEB_HOST}/{self.organization_name}/datasets/{dataset_name}' in result.output

        # Run a new experiment with --git-ref
        result = self.runner.invoke(['experiment', 'run',
                                     '-c', 'test',
                                     '--start-command', 'python main.py',
                                     '-i', 'savvihub/kernels:full-cpu',
                                     '-r', 'resource-spec',
                                     '--git-ref', 'dummy-git-ref',
                                     '--dataset', f'{self.organization_name}/{dataset_name}:/input'])
        assert f'{WEB_HOST}/{self.organization_name}/{self.project_name}/experiments/1' in result.output

        result = self.runner.invoke(['experiment', 'describe', '1'])
        experiment_name = re.search('^Name: (.+)$', result.output, re.M).group(1)

        result = self.runner.invoke(['experiment', 'list'])
        assert experiment_name in result.output

        result = self.runner.invoke(['experiment', 'logs', '1'])
        assert f'{WEB_HOST}/{self.organization_name}/{self.project_name}/experiments/1/logs' in result.output

        result = self.runner.invoke(['experiment', 'output', 'ls', '1'])
        assert 'This directory is empty.' in result.output
        result = self.runner.invoke(['experiment', 'output', 'download', '1'])
        assert 'Found 0 files to download.' in result.output

        # Run a new experiment without --git-ref (git diff created)
        with patch('inquirer.prompt', return_value={'experiment': '[1] Run experiment with uncommitted and untracked changes.'}):
            # Run a new experiment without --git-ref
            result = self.runner.invoke(['experiment', 'run',
                                         '-c', 'python main.py',
                                         '-i', 'savvihub/kernels:full-cpu',
                                         '-r', 'resource-spec',
                                         '--dataset', f'{self.organization_name}/{dataset_name}:/input'])
            assert 'Generating diff patch file...' in result.output
            assert f'{WEB_HOST}/{self.organization_name}/{self.project_name}/experiments/2' in result.output
            result = self.runner.invoke(['experiment', 'describe', '2'])
            assert 'Git Diff File:' in result.output
            git_diff_file_url = re.search('URL: (.+)$', result.output, re.M).group(1)

        # Run a new experiment with --git-ref and --git-diff
        result = self.runner.invoke(['experiment', 'run',
                                     '-c', 'python main.py',
                                     '-i', 'savvihub/kernels:full-cpu',
                                     '-r', 'resource-spec',
                                     '--git-ref', 'dummy-git-ref',
                                     '--git-diff', git_diff_file_url,
                                     '--dataset', f'{self.organization_name}/{dataset_name}:/input'])
        assert 'Generating diff patch file...' in result.output
        assert f'{WEB_HOST}/{self.organization_name}/{self.project_name}/experiments/3' in result.output
        result = self.runner.invoke(['experiment', 'describe', '3'])
        assert 'Git Diff File:' in result.output

        # Run a new experiment without --git-ref but do not use diff
        with patch('inquirer.prompt', return_value={'experiment': '[3] Run experiment without any changes.'}):
            # Run a new experiment without --git-ref
            result = self.runner.invoke(['experiment', 'run',
                                         '-c', 'python main.py',
                                         '-i', 'savvihub/kernels:full-cpu',
                                         '-r', 'resource-spec',
                                         '--dataset', f'{self.organization_name}/{dataset_name}:/input'])
            assert 'Generating diff patch file...' not in result.output
            assert f'{WEB_HOST}/{self.organization_name}/{self.project_name}/experiments/4' in result.output
            result = self.runner.invoke(['experiment', 'describe', '4'])
            assert 'Git Diff File:' not in result.output

        # Try to run a new experiment without --git-ref and abort
        with patch('inquirer.prompt', return_value={'experiment': '[4] Abort.'}):
            # Run a new experiment without --git-ref
            result = self.runner.invoke(['experiment', 'run',
                                         '-c', 'python main.py',
                                         '-i', 'savvihub/kernels:full-cpu',
                                         '-r', 'resource-spec',
                                         '--dataset', f'{self.organization_name}/{dataset_name}:/input'])
            assert 'Aborted.' in result.output
