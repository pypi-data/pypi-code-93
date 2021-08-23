import os

from savvihub.cli.constants import WEB_HOST, PROJECT_ROOT
from savvihub.common.utils import random_string
from tests.conftest import BaseTestCase


class DatasetTest(BaseTestCase):
    def test_dataset(self):
        # Check current datasets
        result = self.runner.invoke(['dataset', 'list'])
        initial_line_count = len(result.output.split('\n'))

        # Missing argument
        result = self.runner.invoke(['dataset', 'create'], allow_fail=True)
        assert "Error: Missing argument 'DATASET_NAME'" in result.output

        dataset1_name = random_string()
        # Create dataset with invalid dataset formats
        result = self.runner.invoke(['dataset', 'create', f'{self.organization_name}/{dataset1_name}'], allow_fail=True)
        assert result.exit_code == 1
        assert 'Lower-case alphabets, digits and hyphen can be used.' in result.output

        # Create dataset with valid dataset formats
        result = self.runner.invoke(['dataset', 'create', dataset1_name])
        assert f'Dataset {dataset1_name} is created.' in result.output
        assert f'{WEB_HOST}/{self.organization_name}/datasets/{dataset1_name}' in result.output
        dataset_name = random_string()
        result = self.runner.invoke(['dataset', 'create', dataset_name])
        assert f'Dataset {dataset_name} is created.' in result.output
        assert f'{WEB_HOST}/{self.organization_name}/datasets/{dataset_name}' in result.output

        # Two datasets have been created
        result = self.runner.invoke(['dataset', 'list'])
        assert len(result.output.split('\n')) == initial_line_count + 2

        # Empty dataset
        dataset_root = f'svds://{self.organization_name}/{dataset_name}'
        result = self.runner.invoke(['dataset', 'files', 'ls', dataset_root])
        assert 'This directory is empty' in result.output

        # Upload one file
        test_files_root = os.path.join(PROJECT_ROOT, 'tests/test_files')
        self.runner.invoke(['dataset', 'files', 'cp', f'{test_files_root}/test_dir/b.txt', dataset_root])
        result = self.runner.invoke(['dataset', 'files', 'ls', dataset_root])
        assert 'b.txt' in result.output
        self.runner.invoke(['dataset', 'files', 'cp', '-r', f'{test_files_root}/test_dir/b.txt', f'{dataset_root}/c.txt'])
        result = self.runner.invoke(['dataset', 'files', 'ls', dataset_root])
        assert 'c.txt' in result.output

        # Upload a directory itself
        self.runner.invoke(['dataset', 'files', 'cp', '-r', test_files_root, dataset_root])
        result = self.runner.invoke(['dataset', 'files', 'ls', dataset_root])
        assert 'test_files' in result.output

        # Upload contents of a directory
        self.runner.invoke(['dataset', 'files', 'cp', '-r', f'{test_files_root}/', dataset_root])
        result = self.runner.invoke(['dataset', 'files', 'ls', dataset_root])
        assert 'test_dir' in result.output
        assert 'a.txt' in result.output

        # Copy one file
        self.runner.invoke(['dataset', 'files', 'cp', f'{dataset_root}/a.txt', f'{dataset_root}/copied.txt'])
        result = self.runner.invoke(['dataset', 'files', 'ls', dataset_root])
        assert 'copied.txt' in result.output

        # Copy a directory itself
        self.runner.invoke(['dataset', 'files', 'cp', '-r', f'{dataset_root}/test_dir', f'{dataset_root}/copied_dir'])
        result = self.runner.invoke(['dataset', 'files', 'ls', dataset_root])
        assert 'copied_dir' in result.output

        # Remove one file
        self.runner.invoke(['dataset', 'files', 'rm', f'{dataset_root}/copied_dir/b.txt'])
        result = self.runner.invoke(['dataset', 'files', 'ls', f'{dataset_root}/copied_dir'])
        assert 'b.txt' not in result.output
        assert 'test_dir2' in result.output

        # Copy contents of a directory
        self.runner.invoke(['dataset', 'files', 'cp', '-r', f'{dataset_root}/test_dir/', f'{dataset_root}/copied_dir'])
        result = self.runner.invoke(['dataset', 'files', 'ls', f'{dataset_root}/copied_dir'])
        assert 'b.txt' in result.output
        assert 'test_dir2' in result.output

        # Remove a directory
        self.runner.invoke(['dataset', 'files', 'rm', '-r', f'{dataset_root}/copied_dir'])
        result = self.runner.invoke(['dataset', 'files', 'ls', dataset_root])
        assert 'copied_dir' not in result.output

        # Download a file
        self.runner.invoke(['dataset', 'files', 'cp', f'{dataset_root}/a.txt', f'{test_files_root}'])
        self.runner.invoke(['dataset', 'files', 'cp', f'{dataset_root}/a.txt', f'{test_files_root}/c.txt'])
        os.remove(f'{test_files_root}/c.txt')

        # Download a directory
        self.runner.invoke(['dataset', 'files', 'cp', '-r', f'{dataset_root}/test_files', f'{test_files_root}'])
        assert os.path.exists(f'{test_files_root}/test_files')
        os.system(f'rm -r {test_files_root}/test_files')

        # Download a directory
        self.runner.invoke(['dataset', 'files', 'cp', '-r', f'{dataset_root}/test_dir/test_dir2', f'{test_files_root}'])
        assert os.path.exists(f'{test_files_root}/test_dir2')
        os.system(f'rm -r {test_files_root}/test_dir2')

        # Download contents of a directory
        self.runner.invoke(['dataset', 'files', 'cp', '-r', f'{dataset_root}/test_dir/', f'{test_files_root}'])
        os.remove(f'{test_files_root}/b.txt')
        assert os.path.exists(f'{test_files_root}/test_dir2')
        os.system(f'rm -r {test_files_root}/test_dir2')

        # Remove root
        self.runner.invoke(['dataset', 'files', 'rm', '-r', dataset_root])
        result = self.runner.invoke(['dataset', 'files', 'ls', dataset_root])
        assert 'This directory is empty' in result.output
