from dataclasses import dataclass, field
import json
import os
import sys
import time

from .attack import Attack
from .dataset_args import DatasetArgs
from .model_args import ModelArgs

ATTACK_RECIPE_NAMES = {"test","test"}
BLACK_BOX_TRANSFORMATION_CLASS_NAMES = {"test":"test"}
WHITE_BOX_TRANSFORMATION_CLASS_NAMES = {"test":"test"}
CONSTRAINT_CLASS_NAMES = {"test":"test"}

@dataclass
class AttackArgs:
    # num_examples: int = 10
    # num_successful_examples: int = None
    # num_examples_offset: int = 0
    # attack_n: bool = False
    # shuffle: bool = False

    def __post_init__(self):
        if self.num_successful_examples:
            self.num_examples = None

    @classmethod
    def _add_parser_args(cls, parser):
        """Add listed args to command line parser."""
        default_obj = cls()
        print(default_obj)
        num_ex_group = parser.add_mutually_exclusive_group(required=False)
        num_ex_group.add_argument(
            "--num",
            "-n",
            type=int,
            default=default_obj.num_examples,
            help="The number of examples to process, -1 for entire dataset.",
        )

@dataclass
class _CommandLineAttackArgs:
    model: str = "model"

    @classmethod
    def _add_parser_args(cls, parser):
        """Add listed args to command line parser."""
        default_obj = cls()
        print(default_obj)

        transformation_names = set(BLACK_BOX_TRANSFORMATION_CLASS_NAMES.keys()) | set(
            WHITE_BOX_TRANSFORMATION_CLASS_NAMES.keys()
        )
        parser.add_argument(
            "--model",
            type=str,
            required=False,
            default=default_obj.model,
            help='The transformation to apply. Usage: "--transformation {transformation}:{arg_1}={value_1},{arg_3}={value_3}". Choices: '
            + str(transformation_names),
        )

@dataclass
class CommandLineAttackArgs(AttackArgs, _CommandLineAttackArgs, DatasetArgs, ModelArgs):
    @classmethod
    def _add_parser_args(cls, parser):
        """Add listed args to command line parser."""
        parser = ModelArgs._add_parser_args(parser)
        parser = DatasetArgs._add_parser_args(parser)
        parser = _CommandLineAttackArgs._add_parser_args(parser)
        parser = AttackArgs._add_parser_args(parser)
        return parser