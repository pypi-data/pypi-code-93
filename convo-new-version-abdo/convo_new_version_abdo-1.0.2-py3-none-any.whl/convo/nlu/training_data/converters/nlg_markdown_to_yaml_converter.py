from pathlib import Path

from convo.shared.utils.cli import printing_success
from convo.shared.nlu.training_data.formats import NLGMarkdownReviewer
from convo.shared.nlu.training_data.formats.convo_yaml import ConvoYAMLAuthor
from convo.utils.converter import TrainingDataSetModifier


class NLGMarkdown_To_YamlConverter(TrainingDataSetModifier):
    @classmethod
    def filtered(cls, source_path: Path) -> bool:
        """Checks if the given training data file contains NLG data in `Markdown` format
        and can be converted to `YAML`.

        Args:
            source_path: Path to the training data file.

        Returns:
            `True` if the given file can be converted, `False` otherwise
        """
        return NLGMarkdownReviewer.markdown_nlg_file_check(source_path)

    @classmethod
    async def Convert_and_Writing(cls, source_path: Path, output_path: Path) -> None:
        """Converts the given training data file and saves it to the output dir.

        Args:
            source_path: Path to the training data file.
            output_path: Path to the output dir.
        """
        Reader_ = NLGMarkdownReviewer()
        Writer_ = ConvoYAMLAuthor()

        turnout_nlg_path = cls.generating_path_for_converted_training_data_file(
            source_path, output_path
        )

        yaml_train_data = Reader_.reading(source_path)
        Writer_.dump(turnout_nlg_path, yaml_train_data)

        printing_success(f"Converted NLG file: '{source_path}' >> '{turnout_nlg_path}'.")
