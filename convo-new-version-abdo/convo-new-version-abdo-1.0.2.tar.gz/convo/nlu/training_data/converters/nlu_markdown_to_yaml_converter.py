from pathlib import Path
from typing import Dict, Text, Any

from convo.shared.utils.cli import printing_success
from convo.nlu.utils.pattern_utils import read_lookup_table_file
from convo.shared.nlu.training_data.formats import MarkdownReviewer
from convo.shared.nlu.training_data.formats.convo_yaml import ConvoYAMLAuthor
from convo.shared.nlu.training_data.training_data import TrainingDataSet
from convo.utils.converter import TrainingDataSetModifier


class NLUMarkdown_To_YamlConverter(TrainingDataSetModifier):
    @classmethod
    def filtered(cls, source_path: Path) -> bool:
        """Checks if the given training data file contains NLU data in `Markdown` format
        and can be converted to `YAML`.

        Args:
            source_path: Path to the training data file.

        Returns:
            `True` if the given file can be converted, `False` otherwise
        """
        return MarkdownReviewer.markdown_nlu_file_check(source_path)

    @classmethod
    async def Convert_and_Writing(cls, source_path: Path, output_path: Path) -> None:
        """Converts the given training data file and saves it to the output dir.

        Args:
            source_path: Path to the training data file.
            output_path: Path to the output dir.
        """
        outcome_nlu_path = cls.generating_path_for_converted_training_data_file(
            source_path, output_path
        )

        yaml_train_data = MarkdownReviewer().reading(source_path)
        ConvoYAMLAuthor().dump(outcome_nlu_path, yaml_train_data)

        for lookup_table in yaml_train_data.lookup_tables:
            cls.writing_nlu_lookup_table_yaml(lookup_table, output_path)

        printing_success(f"Converted NLU file: '{source_path}' >> '{outcome_nlu_path}'.")

    @classmethod
    def writing_nlu_lookup_table_yaml(
        cls, lookup_table: Dict[Text, Any], output_dir_path: Path
    ) -> None:
        """Converts and writes lookup tables examples from `txt` to `YAML` format.

        Args:
            lookup_table: Lookup tables items.
            output_dir_path: Path to the target output dir.
        """
        file_lookup_table = lookup_table.get("elements")
        if not file_lookup_table or not isinstance(file_lookup_table, str):
            return

        exp_from_file = read_lookup_table_file(file_lookup_table)
        trgt_file_name = cls.generating_path_for_converted_training_data_file(
            Path(file_lookup_table), output_dir_path
        )
        name_entities = Path(file_lookup_table).stem

        ConvoYAMLAuthor().dump(
            trgt_file_name,
            TrainingDataSet(
                lookup_tables=[{"name": name_entities, "elements": exp_from_file}]
            ),
        )
