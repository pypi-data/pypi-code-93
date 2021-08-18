from pathlib import Path

import convo.shared.constants
from convo.shared.core.training_data.story_reader.markdown_story_reader import (
    MarkdownStoryReviewer,
)
from convo.shared.core.training_data.story_writer.yaml_story_writer import (
    YAMLStoryAuthor,
)
from convo.shared.utils.cli import printing_success, printing_warning
from convo.utils.converter import TrainingDataSetModifier


class StoryMarkdownToYamlConverter(TrainingDataSetModifier):
    @classmethod
    def filter(cls, source_path: Path) -> bool:
        """Checks if the given training data file contains Core data in `Markdown`
        format and can be converted to `YAML`.

        Args:
            source_path: Path to the training data file.

        Returns:
            `True` if the given file can be converted, `False` otherwise
        """
        return MarkdownStoryReviewer.isStoriesFile(
            source_path
        ) or MarkdownStoryReviewer.isTestStoriesFile(source_path)

    @classmethod
    async def change_and_write(cls, source_path: Path, output_path: Path) -> None:
        """Converts the given training data file and saves it to the output dir.

        Args:
            source_path: Path to the training data file.
            output_path: Path to the output dir.
        """
        from convo.shared.core.training_data.story_reader.yaml_story_reader import (
            KEY_CURRENT_ACTIVE_VALUE,
        )

        # check if source file is test stories file
        if MarkdownStoryReviewer.isTestStoriesFile(source_path):
            get_reader = MarkdownStoryReviewer(is_used_for_conversion=True, use_e2e=True)
            output_core_path_flow = cls._create_path_for_converted_test_data_set_file(
                source_path, output_path
            )
        else:
            get_reader = MarkdownStoryReviewer(is_used_for_conversion=True)
            output_core_path_flow = cls.generating_path_for_converted_training_data_file(
                source_path, output_path
            )

        get_steps = get_reader.readFromFile(source_path)

        if YAMLStoryAuthor.story_contain_loops(get_steps):
            printing_warning(
                f"Training data file '{source_path}' contains forms. "
                f"Any 'form' events will be converted to '{KEY_CURRENT_ACTIVE_VALUE}' events. "
                f"Please note that in order for these stories to work you still "
                f"need the 'FormPolicy' to be active. However the 'FormPolicy' is "
                f"deprecated, please consider switching to the new 'RulePolicy', "
                f"for which you can find the documentation here: "
                f"{convo.shared.constants.RULES_DOCUMENTS_URL}."
            )

        author = YAMLStoryAuthor()
        author.dump(
            output_core_path_flow,
            get_steps,
            is_test_story=MarkdownStoryReviewer.isTestStoriesFile(source_path),
        )

        printing_success(f"Converted Core file: '{source_path}' >> '{output_core_path_flow}'.")

    @classmethod
    def _create_path_for_converted_test_data_set_file(
        cls, source_file_path: Path, output_directory: Path
    ) -> Path:
        """Generates path for a test data file converted to YAML format.

        Args:
            source_file_path: Path to the original file.
            output_directory: Path to the target dir.

        Returns:
            Path to the target converted training data file.
        """
        if cls._have_test_prefix(source_file_path):
            return (
                output_directory
                / f"{source_file_path.stem}{cls.convert_file_suffix()}"
            )
        return (
            output_directory / f"{convo.shared.constants.TEST_STORIES_FILES_PREFIX}"
            f"{source_file_path.stem}{cls.convert_file_suffix()}"
        )

    @classmethod
    def _have_test_prefix(cls, source_file_path: Path) -> bool:
        """Checks if test data file has test prefix.

        Args:
            source_file_path: Path to the original file.

        Returns:
            `True` if the filename starts with the prefix, `False` otherwise.
        """
        return Path(source_file_path).name.startswith(
            convo.shared.constants.TEST_STORIES_FILES_PREFIX
        )
