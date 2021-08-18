from pathlib import Path
from typing import Text


class TrainingDataSetModifier:
    """Interface for any training data format conversion."""

    @classmethod
    def filter(cls, source_path: Path) -> bool:
        """Checks if the concrete implementation of TrainingDataSetModifier can convert
        training data file.

        Args:
            source_path: Path to the training data file.

        Returns:
            `True` if the given file can be converted, `False` otherwise
        """
        raise NotImplementedError

    @classmethod
    async def converting_and_writing(cls, source_path: Path, output_path: Path) -> None:
        """Converts the given training data file and saves it to the output dir.

        Args:
            source_path: Path to the training data file.
            output_path: Path to the output dir.
        """
        raise NotImplementedError

    @classmethod
    def generating_path_for_converted_training_data_file(
        cls, source_file_path: Path, output_directory: Path
    ) -> Path:
        """Generates path for a training data file converted to YAML format.

        Args:
            source_file_path: Path to the original file.
            output_directory: Path to the target dir.

        Returns:
            Path to the target converted training data file.
        """
        return (
            output_directory / f"{source_file_path.stem}{cls.convert_file_suffix()}"
        )

    @classmethod
    def convert_file_suffix(cls) -> Text:
        """Returns suffix that should be appended to the converted
        training data file."""
        return "_converted.yml"
