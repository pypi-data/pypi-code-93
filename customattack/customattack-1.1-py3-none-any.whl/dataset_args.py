
from dataclasses import dataclass

import customattack
# from customattack.shared.utils import ARGS_SPLIT_TOKEN, load_module_from_file

CUSTOMATTACK_DATASET_BY_MODEL = {"test":"test"}

@dataclass
class DatasetArgs:
    """Arguments for loading dataset from command line input."""

    dataset_by_model: str = None
    dataset_from_huggingface: str = None
    dataset_from_file: str = None
    dataset_split: str = None
    filter_by_labels: list = None

    @classmethod
    def _add_parser_args(cls, parser):
        """Adds dataset-related arguments to an argparser."""

        dataset_group = parser.add_mutually_exclusive_group()
        dataset_group.add_argument(
            "--dataset-by-model",
            type=str,
            required=False,
            default=None,
            help="Dataset to load depending on the name of the model",
        )
    #
    # @classmethod
    # def _create_dataset_from_args(cls, args):
    #     """Given ``DatasetArgs``, return specified
    #     ``customattack.dataset.Dataset`` object."""
    #
    #     assert isinstance(
    #         args, cls
    #     ), f"Expect args to be of type `{type(cls)}`, but got type `{type(args)}`."
    #
    #     # Automatically detect dataset for huggingface & customattack models.
    #     # This allows us to use the --model shortcut without specifying a dataset.
    #     if hasattr(args, "model"):
    #         args.dataset_by_model = args.model
    #     if args.dataset_by_model in HUGGINGFACE_DATASET_BY_MODEL:
    #         args.dataset_from_huggingface = HUGGINGFACE_DATASET_BY_MODEL[
    #             args.dataset_by_model
    #         ]
    #     elif args.dataset_by_model in TEXTATTACK_DATASET_BY_MODEL:
    #         dataset = TEXTATTACK_DATASET_BY_MODEL[args.dataset_by_model]
    #         if dataset[0].startswith("customattack"):
    #             # unsavory way to pass custom dataset classes
    #             # ex: dataset = ('customattack.datasets.helpers.TedMultiTranslationDataset', 'en', 'de')
    #             dataset = eval(f"{dataset[0]}")(*dataset[1:])
    #             return dataset
    #         else:
    #             args.dataset_from_huggingface = dataset
    #
    #     # Get dataset from args.
    #     if args.dataset_from_file:
    #         customattack.shared.logger.info(
    #             f"Loading model and tokenizer from file: {args.model_from_file}"
    #         )
    #         if ARGS_SPLIT_TOKEN in args.dataset_from_file:
    #             dataset_file, dataset_name = args.dataset_from_file.split(
    #                 ARGS_SPLIT_TOKEN
    #             )
    #         else:
    #             dataset_file, dataset_name = args.dataset_from_file, "dataset"
    #         try:
    #             dataset_module = load_module_from_file(dataset_file)
    #         except Exception:
    #             raise ValueError(f"Failed to import file {args.dataset_from_file}")
    #         try:
    #             dataset = getattr(dataset_module, dataset_name)
    #         except AttributeError:
    #             raise AttributeError(
    #                 f"Variable ``dataset`` not found in module {args.dataset_from_file}"
    #             )
    #     elif args.dataset_from_huggingface:
    #         dataset_args = args.dataset_from_huggingface
    #         if isinstance(dataset_args, str):
    #             if ARGS_SPLIT_TOKEN in dataset_args:
    #                 dataset_args = dataset_args.split(ARGS_SPLIT_TOKEN)
    #             else:
    #                 dataset_args = (dataset_args,)
    #         if args.dataset_split:
    #             if len(dataset_args) > 1:
    #                 dataset_args[2] = args.dataset_split
    #                 dataset = customattack.datasets.HuggingFaceDataset(
    #                     *dataset_args, shuffle=False
    #                 )
    #             else:
    #                 dataset = customattack.datasets.HuggingFaceDataset(
    #                     *dataset_args, split=args.dataset_split, shuffle=False
    #                 )
    #         else:
    #             dataset = customattack.datasets.HuggingFaceDataset(
    #                 *dataset_args, shuffle=False
    #             )
    #     else:
    #         raise ValueError("Must supply pretrained model or dataset")
    #
    #     assert isinstance(
    #         dataset, customattack.datasets.Dataset
    #     ), "Loaded `dataset` must be of type `customattack.datasets.Dataset`."
    #
    #     if args.filter_by_labels:
    #         dataset.filter_by_labels_(args.filter_by_labels)
    #
    #     return dataset