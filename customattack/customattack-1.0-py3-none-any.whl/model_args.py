from dataclasses import dataclass
import json
import os
HUGGINGFACE_MODELS = {"test":"test"}
CUSTOMATTACK_MODELS = {"test":"test"}
@dataclass
class ModelArgs:
    """Arguments for loading base/pretrained or trained models."""

    model: str = None
    model_from_file: str = None
    model_from_huggingface: str = None

    @classmethod
    def _add_parser_args(cls, parser):
        """Adds model-related arguments to an argparser."""
        model_group = parser.add_mutually_exclusive_group()

        model_names = list(HUGGINGFACE_MODELS.keys()) + list(CUSTOMATTACK_MODELS.keys())
        model_group.add_argument(
            "--model",
            type=str,
            required=False,
            default=None,
            help="Name of or path to a pre-trained TextAttack model to load. Choices: "
            + str(model_names),
        )
        model_group.add_argument(
            "--model-from-file",
            type=str,
            required=False,
            help="File of model and tokenizer to import.",
        )
        model_group.add_argument(
            "--model-from-huggingface",
            type=str,
            required=False,
            help="Name of or path of pre-trained HuggingFace model to load.",
        )

        return parser