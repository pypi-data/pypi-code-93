from dataclasses import dataclass, field
import json
import os
import sys
import time

import customattack
from customattack.shared.utils import ARGS_SPLIT_TOKEN, load_module_from_file

from .attack import Attack
from .dataset_args import DatasetArgs
from .model_args import ModelArgs

ATTACK_RECIPE_NAMES = {"test", "test"}
BLACK_BOX_TRANSFORMATION_CLASS_NAMES = {"test": "test"}
WHITE_BOX_TRANSFORMATION_CLASS_NAMES = {"test": "test"}
CONSTRAINT_CLASS_NAMES = {"test": "test"}


@dataclass
class AttackArgs:
    num_examples: int = 10
    num_successful_examples: int = None
    random_seed: int = 765  # equivalent to sum((ord(c) for c in "TEXTATTACK"))
    log_to_txt: str = None
    log_to_csv: str = None
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
        num_ex_group = parser.add_mutually_exclusive_group(required=False)
        num_ex_group.add_argument(
            "--num_examples",
            "-n",
            type=int,
            default=default_obj.num_examples,
            help="The number of examples to process, -1 for entire dataset.",
        )
        return parser

    @classmethod
    def create_loggers_from_args(cls, args):
        assert isinstance(
            args, cls
        ), f"Expect args to be of type `{type(cls)}`, but got type `{type(args)}`."

        # Create logger
        attack_log_manager = customattack.loggers.AttackLogManager()

        # Get current time for file naming
        timestamp = time.strftime("%Y-%m-%d-%H-%M")

        # if '--log-to-txt' specified with arguments
        if args.log_to_txt is not None:
            if args.log_to_txt.lower().endswith(".txt"):
                txt_file_path = args.log_to_txt
            else:
                txt_file_path = os.path.join(args.log_to_txt, f"{timestamp}-log.txt")

            dir_path = os.path.dirname(txt_file_path)
            dir_path = dir_path if dir_path else "."
            if not os.path.exists(dir_path):
                os.makedirs(os.path.dirname(txt_file_path))

            color_method = "file"
            attack_log_manager.add_output_file(txt_file_path, color_method)

        # if '--log-to-csv' specified with arguments
        if args.log_to_csv is not None:
            if args.log_to_csv.lower().endswith(".csv"):
                csv_file_path = args.log_to_csv
            else:
                csv_file_path = os.path.join(args.log_to_csv, f"{timestamp}-log.csv")

            dir_path = os.path.dirname(csv_file_path)
            dir_path = dir_path if dir_path else "."
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)

            color_method = (
                None if args.csv_coloring_style == "plain" else args.csv_coloring_style
            )
            attack_log_manager.add_output_csv(csv_file_path, color_method)

        # # Visdom
        # if args.log_to_visdom is not None:
        #     attack_log_manager.enable_visdom(**args.log_to_visdom)
        #
        # # Weights & Biases
        # if args.log_to_wandb is not None:
        #     attack_log_manager.enable_wandb(args.log_to_wandb)
        #
        # # Stdout
        # if not args.disable_stdout and not sys.stdout.isatty():
        #     attack_log_manager.disable_color()
        # elif not args.disable_stdout:
        #     attack_log_manager.enable_stdout()

        return attack_log_manager

@dataclass
class _CommandLineAttackArgs:
    model: str = "model"
    interactive: bool = False

    @classmethod
    def _add_parser_args(cls, parser):
        """Add listed args to command line parser."""
        default_obj = cls()

        # transformation_names = set(BLACK_BOX_TRANSFORMATION_CLASS_NAMES.keys()) | set(
        #     WHITE_BOX_TRANSFORMATION_CLASS_NAMES.keys()
        # )
        parser.add_argument(
            "--interactive",
            action="store_true",
            default=default_obj.interactive,
            help="Whether to run attacks interactively.",
        )
        return parser

    @classmethod
    def _create_attack_from_args(cls, args, model_wrapper):
        """Given ``CommandLineArgs`` and ``ModelWrapper``, return specified
        ``Attack`` object."""

        assert isinstance(
            args, cls
        ), f"Expect args to be of type `{type(cls)}`, but got type `{type(args)}`."

        # if args.attack_recipe:
        #     if ARGS_SPLIT_TOKEN in args.attack_recipe:
        #         recipe_name, params = args.attack_recipe.split(ARGS_SPLIT_TOKEN)
        #         if recipe_name not in ATTACK_RECIPE_NAMES:
        #             raise ValueError(f"Error: unsupported recipe {recipe_name}")
        #         recipe = eval(
        #             f"{ATTACK_RECIPE_NAMES[recipe_name]}.build(model_wrapper, {params})"
        #         )
        #     elif args.attack_recipe in ATTACK_RECIPE_NAMES:
        #         recipe = eval(
        #             f"{ATTACK_RECIPE_NAMES[args.attack_recipe]}.build(model_wrapper)"
        #         )
        #     else:
        #         raise ValueError(f"Invalid recipe {args.attack_recipe}")
        #     if args.query_budget:
        #         recipe.goal_function.query_budget = args.query_budget
        #     recipe.goal_function.model_cache_size = args.model_cache_size
        #     recipe.constraint_cache_size = args.constraint_cache_size
        #     return recipe
        # elif args.attack_from_file:
        #     if ARGS_SPLIT_TOKEN in args.attack_from_file:
        #         attack_file, attack_name = args.attack_from_file.split(ARGS_SPLIT_TOKEN)
        #     else:
        #         attack_file, attack_name = args.attack_from_file, "attack"
        #     attack_module = load_module_from_file(attack_file)
        #     if not hasattr(attack_module, attack_name):
        #         raise ValueError(
        #             f"Loaded `{attack_file}` but could not find `{attack_name}`."
        #         )
        #     attack_func = getattr(attack_module, attack_name)
        #     return attack_func(model_wrapper)
        # else:
        #     goal_function = cls._create_goal_function_from_args(args, model_wrapper)
        #     transformation = cls._create_transformation_from_args(args, model_wrapper)
        #     constraints = cls._create_constraints_from_args(args)
        #     if ARGS_SPLIT_TOKEN in args.search_method:
        #         search_name, params = args.search_method.split(ARGS_SPLIT_TOKEN)
        #         if search_name not in SEARCH_METHOD_CLASS_NAMES:
        #             raise ValueError(f"Error: unsupported search {search_name}")
        #         search_method = eval(
        #             f"{SEARCH_METHOD_CLASS_NAMES[search_name]}({params})"
        #         )
        #     elif args.search_method in SEARCH_METHOD_CLASS_NAMES:
        #         search_method = eval(
        #             f"{SEARCH_METHOD_CLASS_NAMES[args.search_method]}()"
        #         )
        #     else:
        #         raise ValueError(f"Error: unsupported attack {args.search_method}")

        # return Attack(
        #     goal_function,
        #     constraints,
        #     transformation,
        #     search_method,
        #     constraint_cache_size=args.constraint_cache_size,
        # )
        return Attack()


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
