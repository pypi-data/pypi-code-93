import os
from distutils.dir_util import copy_tree
from typing import List

from magnumapi.optimization.OptimizationNotebookConfig import OptimizationNotebookConfig


class DirectoryManager:

    @staticmethod
    def check_if_file_exists(file_path: str):

        if not os.path.isfile(file_path):
            raise FileNotFoundError('The file %s does not exist!' % file_path)

    @staticmethod
    def create_directory_if_nonexistent(output_dir):
        is_dir = os.path.isdir(output_dir)
        if not is_dir:
            os.mkdir(output_dir)

    @staticmethod
    def find_output_subdirectory_name(output_dir):
        current_output_folder = '1'
        int_folder_names = [int(name) for name in os.listdir(output_dir) if name.isnumeric()]
        if int_folder_names:
            max_folder_name = max(int_folder_names)
            current_output_folder = str(max_folder_name + 1)

        return current_output_folder

    @classmethod
    def create_output_subdirectory(cls, output_dir, subdirectory_name):
        output_subdirectory_dir = os.path.join(output_dir, subdirectory_name)
        cls.create_directory_if_nonexistent(output_subdirectory_dir)

    @classmethod
    def copy_notebook_folders(cls, input_folder,
                              notebook_configs: List[OptimizationNotebookConfig],
                              output_subdirectory_dir):
        for notebook_config in notebook_configs:
            notebook_folder = notebook_config.notebook_folder
            input_notebook_folder_dir = os.path.join(input_folder, notebook_folder)
            output_notebook_subdirectory_dir = os.path.join(output_subdirectory_dir, notebook_folder)
            cls.create_directory_if_nonexistent(output_notebook_subdirectory_dir)
            copy_tree(input_notebook_folder_dir, output_notebook_subdirectory_dir)

    @classmethod
    def copy_model_input(cls, input_folder_path, input_folder_name, output_subdirectory_dir):
        ref_input_folder = os.path.join(input_folder_path, input_folder_name)
        new_input_folder = os.path.join(output_subdirectory_dir, input_folder_name)

        cls.create_directory_if_nonexistent(new_input_folder)
        copy_tree(ref_input_folder, new_input_folder)
