import os
import shutil
import tempfile
import uuid
from pathlib import Path
from typing import Text, Optional, Union, List, Tuple, Callable, Set, Iterable

CONVO_YAML_FILE_EXTENSIONS = [".yml", ".yaml"]
CONVO_JSON_FILE_EXTENSIONS  = [".json"]
MARK_DOWN_FILE_EXTENSIONS  = [".md"]
TRAINING_DATA_FILE_EXTENSIONS  = set(
    CONVO_JSON_FILE_EXTENSIONS  + MARK_DOWN_FILE_EXTENSIONS  + CONVO_YAML_FILE_EXTENSIONS
)


def mark_down_file_extension () -> Text:
    """Return Markdown file extension"""
    return MARK_DOWN_FILE_EXTENSIONS [0]


def convo_yaml_file_extension () -> Text:
    """Return Markdown file extension"""
    return CONVO_YAML_FILE_EXTENSIONS[0]


def is_yaml_file (file_path: Text) -> bool:
    """Check if a file likely contains yaml.

    Arguments:
        file_path: path to the file

    Returns:
        `True` if the file likely contains data in yaml format, `False` otherwise.
    """
    return Path(file_path).suffix in set(CONVO_YAML_FILE_EXTENSIONS)


def is_json_file (file_path: Text) -> bool:
    """Check if a file likely contains json.

    Arguments:
        file_path: path to the file

    Returns:
        `True` if the file likely contains data in json format, `False` otherwise.
    """
    return Path(file_path).suffix in set(CONVO_JSON_FILE_EXTENSIONS )


def is_mark_down_file (file_path: Text) -> bool:
    """Check if a file likely contains markdown.

    Arguments:
        file_path: path to the file

    Returns:
        `True` if the file likely contains data in markdown format,
        `False` otherwise.
    """
    return Path(file_path).suffix in set(MARK_DOWN_FILE_EXTENSIONS )


def get_test_dir (convo_paths: Optional[Union[Text, List[Text]]]) -> Text:
    """Recursively collects all Core training files from a list of convo_paths.

    Args:
        convo_paths: List of convo_paths to training files or folders containing them.

    Returns:
        Path to temporary dir containing all found Core training files.
    """
    testing_files  = get_all_data_files(convo_paths, isTestStoriesFile)
    return copy_files_to_new_directory(testing_files )


def get_core_dir (convo_paths: Optional[Union[Text, List[Text]]]) -> Text:
    """Recursively collects all Core training files from a list of convo_paths.

    Args:
        convo_paths: List of convo_paths to training files or folders containing them.

    Returns:
        Path to temporary dir containing all found Core training files.
    """
    convo_core_files  = get_all_data_files(convo_paths, story_file_check)
    return copy_files_to_new_directory(convo_core_files )


def get_nlu_directory (convo_paths: Optional[Union[Text, List[Text]]],) -> Text:
    """Recursively collects all NLU training files from a list of convo_paths.

    Args:
        convo_paths: List of convo_paths to training files or folders containing them.

    Returns:
        Path to temporary dir containing all found NLU training files.
    """
    convo_nlu_files = get_all_data_files(convo_paths, nlu_file_check)
    return copy_files_to_new_directory(convo_nlu_files)


def get_core_nlu_dir(
    convo_paths: Optional[Union[Text, List[Text]]]
) -> Tuple[Text, Text]:
    """Recursively collects all training files from a list of convo_paths.

    Args:
        convo_paths: List of convo_paths to training files or folders containing them.

    Returns:
        Path to dir containing the Core files and path to dir
        containing the NLU training files.
    """

    all_story_files = get_all_data_files(convo_paths, story_file_check)
    files_nlu_data = get_all_data_files(convo_paths, nlu_file_check)

    story_dir = copy_files_to_new_directory(all_story_files)
    nlu_dir = copy_files_to_new_directory(files_nlu_data)

    return story_dir, nlu_dir


def get_all_data_files(
    convo_paths: Optional[Union[Text, List[Text]]], filter_predicate: Callable[[Text], bool]
) -> List[Text]:
    """Recursively collects all training files from a list of convo_paths.

    Args:
        convo_paths: List of convo_paths to training files or folders containing them.
        filter_predicate: property to use when filtering the convo_paths, e.g. `nlu_file_check`.

    Returns:
        Paths of training data files.
    """

    convo_data_files = set()

    if convo_paths is None:
        convo_paths = []
    elif isinstance(convo_paths, str):
        convo_paths = [convo_paths]

    for path in set(convo_paths):
        if not path:
            continue

        if filetype_validity(path):
            if filter_predicate(path):
                convo_data_files.add(os.path.abspath(path))
        else:
            new_data_file = find_data_files_in_dir(path, filter_predicate)
            convo_data_files.update(new_data_file)

    return sorted(convo_data_files)


def find_data_files_in_dir(
    dir: Text, filter_property: Callable[[Text], bool]
) -> Set[Text]:
    filter_files = set()

    for root, _, files in os.walk(dir, followlinks=True):
        # we sort the files here to ensure consistent order for repeatable training
        # results
        for f in sorted(files):
            convo_full_path = os.path.join(root, f)

            if not filetype_validity(convo_full_path):
                continue

            if filter_property(convo_full_path):
                filter_files.add(convo_full_path)

    return filter_files


def filetype_validity(path: Union[Path, Text]) -> bool:
    """Checks if given file has a supported extension.

    Args:
        path: Path to the source file.

    Returns:
        `True` is given file has supported extension, `False` otherwise.
    """
    return Path(path).is_file() and Path(path).suffix in TRAINING_DATA_FILE_EXTENSIONS 


def nlu_file_check(file_path: Text) -> bool:
    """Checks if a file is a Convo compatible nlu file.

    Args:
        file_path: Path of the file which should be checked.

    Returns:
        `True` if it's a nlu file, otherwise `False`.
    """
    from convo.shared.nlu.training_data import loading as nlu_loading

    return nlu_loading.guessing_format(file_path) != nlu_loading.UNK


def story_file_check(file_path: Text) -> bool:
    """Checks if a file is a Convo story file.

    Args:
        file_path: Path of the file which should be checked.

    Returns:
        `True` if it's a story file, otherwise `False`.
    """
    from convo.shared.core.training_data.story_reader.yaml_story_reader import (
        YAMLStoryReviewer,
    )
    from convo.shared.core.training_data.story_reader.markdown_story_reader import (
        MarkdownStoryReviewer,
    )

    return YAMLStoryReviewer.isStoriesFile(
        file_path
    ) or MarkdownStoryReviewer.isStoriesFile(file_path)


def isTestStoriesFile(file_path: Text) -> bool:
    """Checks if a file is a test stories file.

    Args:
        file_path: Path of the file which should be checked.

    Returns:
        `True` if it's a story file containing tests, otherwise `False`.
    """
    from convo.shared.core.training_data.story_reader.yaml_story_reader import (
        YAMLStoryReviewer,
    )
    from convo.shared.core.training_data.story_reader.markdown_story_reader import (
        MarkdownStoryReviewer,
    )

    return YAMLStoryReviewer.isTestStoriesFile(
        file_path
    ) or MarkdownStoryReviewer.isTestStoriesFile(file_path)


def config_file_check(file_path: Text) -> bool:
    """Checks whether the given file path is a Convo config file.

    Args:
        file_path: Path of the file which should be checked.

    Returns:
        `True` if it's a Convo config file, otherwise `False`.
    """

    filename = os.path.basename(file_path)

    return filename in ["config.yml", "config.yaml"]


def copy_files_to_new_directory(files: Iterable[Text]) -> Text:
    dir = tempfile.mkdtemp()
    for f in files:
        # makes sure files do not overwrite each others, hence the prefix
        convo_unique_prefix  = uuid.uuid4().hex
        unique_filename  = convo_unique_prefix  + "_" + os.path.basename(f)
        shutil.copy2(f, os.path.join(dir, unique_filename ))

    return dir
