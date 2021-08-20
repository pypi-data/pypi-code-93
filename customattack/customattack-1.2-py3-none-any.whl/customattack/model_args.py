from dataclasses import dataclass
import json
import os
import transformers
import customattack
from customattack.shared.utils import ARGS_SPLIT_TOKEN, load_module_from_file

HUGGINGFACE_MODELS = {"hungging_test":None}
CUSTOMATTACK_MODELS = {
    "lstm-ag-news": "models_v2/classification/lstm/ag-news",
    "lstm-imdb": "models_v2/classification/lstm/imdb",
    "lstm-mr": "models_v2/classification/lstm/mr",
    "lstm-sst2": "models_v2/classification/lstm/sst2",
    "lstm-yelp": "models_v2/classification/lstm/yelp",
    "resnet50":"custommodels/resnet_v1_50.ckpt"
}
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

    @classmethod
    def _create_model_from_args(cls, args):
        """Given ``ModelArgs``, return specified
        ``customattack.models.wrappers.ModelWrapper`` object."""

        assert isinstance(
            args, cls
        ), f"Expect args to be of type `{type(cls)}`, but got type `{type(args)}`."

        if args.model_from_file:
            # Support loading the model from a .py file where a model wrapper
            # is instantiated.
            colored_model_name = customattack.shared.utils.color_text(
                args.model_from_file, color="blue", method="ansi"
            )
            customattack.shared.logger.info(
                f"Loading model and tokenizer from file: {colored_model_name}"
            )
            if ARGS_SPLIT_TOKEN in args.model_from_file:
                model_file, model_name = args.model_from_file.split(ARGS_SPLIT_TOKEN)
            else:
                _, model_name = args.model_from_file, "model_wrapper"
            try:
                model_module = load_module_from_file(args.model_from_file)
            except Exception:
                raise ValueError(f"Failed to import file {args.model_from_file}.")
            try:
                model = getattr(model_module, model_name)
            except AttributeError:
                raise AttributeError(
                    f"Variable `{model_name}` not found in module {args.model_from_file}."
                )

            if not isinstance(model, customattack.models.wrappers.ModelWrapper):
                raise TypeError(
                    f"Variable `{model_name}` must be of type "
                    f"``customattack.models.ModelWrapper``, got type {type(model)}."
                )
        elif (args.model in HUGGINGFACE_MODELS) or args.model_from_huggingface:
            # Support loading models automatically from the HuggingFace model hub.

            model_name = (
                HUGGINGFACE_MODELS[args.model]
                if (args.model in HUGGINGFACE_MODELS)
                else args.model_from_huggingface
            )
            colored_model_name = customattack.shared.utils.color_text(
                model_name, color="blue", method="ansi"
            )
            customattack.shared.logger.info(
                f"Loading pre-trained model from HuggingFace model repository: {colored_model_name}"
            )
            model = transformers.AutoModelForSequenceClassification.from_pretrained(
                model_name
            )
            tokenizer = transformers.AutoTokenizer.from_pretrained(
                model_name, use_fast=True
            )
            model = customattack.models.wrappers.HuggingFaceModelWrapper(model, tokenizer)
        elif args.model in CUSTOMATTACK_MODELS:
            # Support loading TextAttack pre-trained models via just a keyword.
            colored_model_name = customattack.shared.utils.color_text(
                args.model, color="blue", method="ansi"
            )
            if args.model.startswith("lstm"):
                customattack.shared.logger.info(
                    f"Loading pre-trained TextAttack LSTM: {colored_model_name}"
                )
                model = customattack.models.helpers.LSTMForClassification.from_pretrained(
                    args.model
                )
            elif args.model.startswith("cnn"):
                customattack.shared.logger.info(
                    f"Loading pre-trained TextAttack CNN: {colored_model_name}"
                )
                model = (
                    customattack.models.helpers.WordCNNForClassification.from_pretrained(
                        args.model
                    )
                )
            elif args.model.startswith("t5"):
                model = customattack.models.helpers.T5ForTextToText.from_pretrained(
                    args.model
                )
            else:
                raise ValueError(f"Unknown customattack model {args.model}")

            # Choose the approprate model wrapper (based on whether or not this is
            # a HuggingFace model).
            if isinstance(model, customattack.models.helpers.T5ForTextToText):
                model = customattack.models.wrappers.HuggingFaceModelWrapper(
                    model, model.tokenizer
                )
            else:
                model = customattack.models.wrappers.PyTorchModelWrapper(
                    model, model.tokenizer
                )
        elif args.model and os.path.exists(args.model):
            # Support loading TextAttack-trained models via just their folder path.
            # If `args.model` is a path/directory, let's assume it was a model
            # trained with customattack, and try and load it.
            if os.path.exists(os.path.join(args.model, "t5-wrapper-config.json")):
                model = customattack.models.helpers.T5ForTextToText.from_pretrained(
                    args.model
                )
                model = customattack.models.wrappers.HuggingFaceModelWrapper(
                    model, model.tokenizer
                )
            elif os.path.exists(os.path.join(args.model, "config.json")):
                with open(os.path.join(args.model, "config.json")) as f:
                    config = json.load(f)
                model_class = config["architectures"]
                if (
                    model_class == "LSTMForClassification"
                    or model_class == "WordCNNForClassification"
                ):
                    model = eval(
                        f"customattack.models.helpers.{model_class}.from_pretrained({args.model})"
                    )
                    model = customattack.models.wrappers.PyTorchModelWrapper(
                        model, model.tokenizer
                    )
                else:
                    # assume the model is from HuggingFace.
                    model = (
                        transformers.AutoModelForSequenceClassification.from_pretrained(
                            args.model
                        )
                    )
                    tokenizer = transformers.AutoTokenizer.from_pretrained(
                        args.model, use_fast=True
                    )
                    model = customattack.models.wrappers.HuggingFaceModelWrapper(
                        model, tokenizer
                    )
        else:
            raise ValueError(f"Error: unsupported TextAttack model {args.model}")

        assert isinstance(
            model, customattack.models.wrappers.ModelWrapper
        ), "`model` must be of type `customattack.models.wrappers.ModelWrapper`."
        return model