import asyncio
import os
from pdb import set_trace
import tempfile
from contextlib import ExitStack
from typing import Text, Optional, List, Union, Dict

import convo.core.interpreter
from convo.shared.nlu.interpreter import NaturalLangInterpreter
from convo.shared.importers.importer import TrainingDataImporter
from convo import model, telemetry
from convo.model import FingerprintComparisonResult
from convo.shared.core.domain import Domain
from convo.nlu.model import Interpreter
import convo.utils.common
from convo.utils.common import TempDirPath

from convo.shared.utils.cli import (
    printing_success,
    printing_warning,
    printing_error,
    printing_color,
)
import convo.shared.utils.io
from convo.shared.constants import (
    DEFAULT_MODEL_PATH ,
    DEFAULT_CORE_SUB_DIRECTORY_NAME,
    DEFAULT_NLU_SUB_DIRECTORY_NAME,
)


def train(
    domain: Text,
    config: Text,
    training_files: Union[Text, List[Text]],
    output: Text = DEFAULT_MODEL_PATH ,
    force_training: bool = False,
    fixed_model_name: Optional[Text] = None,
    persist_nlu_training_data: bool = False,
    core_additional_args: Optional[Dict] = None,
    nlu_additional_args: Optional[Dict] = None,
    loop: Optional[asyncio.AbstractEventLoop] = None,
) -> Optional[Text]:
    return convo.utils.common.running_in_loop(
        train_asynchronous(
            domain=domain,
            config=config,
            training_filename=training_files,
            output_path_flow=output,
            force_training=force_training,
            fixed_model_name=fixed_model_name,
            persist_nlu_training_data=persist_nlu_training_data,
            core_additional_arguments=core_additional_args,
            nlu_additional_arguments=nlu_additional_args,
        ),
        loop,
    )


async def train_asynchronous(
    domain: Union[Domain, Text],
    config: Text,
    training_filename: Optional[Union[Text, List[Text]]],
    output_path_flow: Text = DEFAULT_MODEL_PATH ,
    force_training: bool = False,
    fixed_model_name: Optional[Text] = None,
    persist_nlu_training_data: bool = False,
    core_additional_arguments: Optional[Dict] = None,
    nlu_additional_arguments: Optional[Dict] = None,
) -> Optional[Text]:
    """Trains a Convo model (Core and NLU).

    Args:
        domain: Path to the domain file.
        config: Path to the config for Core and NLU.
        training_filename: Paths to the training data for Core and NLU.
        output_path_flow: Output path.
        force_training: If `True` retrain model even if data has not changed.
        fixed_model_name: Name of model to be stored.
        persist_nlu_training_data: `True` if the NLU training data should be persisted
                                   with the model.
        core_additional_arguments: Additional training parameters for core training.
        nlu_additional_arguments: Additional training parameters forwarded to training
                                  method of each NLU component.

    Returns:
        Path of the trained model archive.
    """

    file_importer = TrainingDataImporter.load_from_configuration(
        config, domain, training_filename
    )
    with ExitStack() as stack:
        train_path = stack.enter_context(TempDirPath(tempfile.mkdtemp()))

        domain = await file_importer.domain()

        if domain.is_empty():
            return await handle_domain_if_not_found(
                file_importer, output_path_flow, fixed_model_name
            )

        return await _train_asynchronous_internal(
            file_importer,
            train_path,
            output_path_flow,
            force_training,
            fixed_model_name,
            persist_nlu_training_data,
            core_additional_arguments=core_additional_arguments,
            nlu_additional_arguments=nlu_additional_arguments,
        )


async def handle_domain_if_not_found(
    file_importer: TrainingDataImporter, output_path, fixed_model_name
):
    nlu_model_only = await _train_nlu_with_validated_data_set(
        file_importer, output=output_path, set_model_name=fixed_model_name
    )
    printing_warning(
        "Core training was skipped because no valid domain file was found. "
        "Only an NLU-model was created. Please specify a valid domain using "
        "the '--domain' argument or check if the provided domain file exists."
    )
    return nlu_model_only


async def _train_asynchronous_internal(
    file_importer: TrainingDataImporter,
    train_path: Text,
    output_path: Text,
    by_force_training: bool,
    fixed_model_name: Optional[Text],
    persist_nlu_training_data: bool,
    core_additional_arguments: Optional[Dict] = None,
    nlu_additional_arguments: Optional[Dict] = None,
) -> Optional[Text]:
    """Trains a Convo model (Core and NLU). Use only from `train_asynchronous`.

    Args:
        file_importer: `TrainingDataImporter` which supplies the training data.
        train_path: Directory in which to train the model.
        output_path: Output path.
        by_force_training: If `True` retrain model even if data has not changed.
        fixed_model_name: Name of model to be stored.
        persist_nlu_training_data: `True` if the NLU training data should be persisted
                                   with the model.
        core_additional_arguments: Additional training parameters for core training.
        nlu_additional_arguments: Additional training parameters forwarded to training
                                  method of each NLU component.

    Returns:
        Path of the trained model archive.
    """

    



    stories, nlu_data = await asyncio.gather(
        file_importer.fetch_stories(), file_importer.fetch_nlu_data()
    )

    if stories.is_empty() and nlu_data.nlu_model_train_check():
        printing_error(
            "No training data given. Please provide stories and NLU data in "
            "order to train a Convo model using the '--data' argument."
        )
        return

    if stories.is_empty():
        printing_warning("No stories present. Just a Convo NLU model will be trained.")
        return await _train_nlu_with_validated_data_set(
            file_importer,
            output=output_path,
            set_model_name=fixed_model_name,
            persist_nlu_training_data=persist_nlu_training_data,
            add_on_arguments=nlu_additional_arguments,
        )

    if nlu_data.nlu_model_train_check():
        printing_warning("No NLU data present. Just a Convo Core model will be trained.")
        return await _train_core_with_validated_data_set(
            file_importer,
            output=output_path,
            fixed_model_name=fixed_model_name,
            add_on_arguments=core_additional_arguments,
        )

    new_fingerprint = await model.model_finger_print(file_importer)
    old_model = model.fetch_latest_model(output_path)

    if not by_force_training:
        fingerprint_comparison = model.should_retrain(
            new_fingerprint, old_model, train_path
        )
    else:
        fingerprint_comparison = FingerprintComparisonResult(force_training=True)

    if fingerprint_comparison.is_supervising_required():
        

        async with telemetry.track_model_training(file_importer, model_type="convo"):
            await _do_supervising(
                file_importer,
                output_path=output_path,
                train_path=train_path,
                fingerprint_comparison_result=fingerprint_comparison,
                fixed_model_name=fixed_model_name,
                persist_nlu_training_data=persist_nlu_training_data,
                core_additional_arguments=core_additional_arguments,
                nlu_additional_arguments=nlu_additional_arguments,
                old_model_zip_path=old_model,
            )

        return model.pack_model(
            fingerprint=new_fingerprint,
            output_directory=output_path,
            train_path=train_path,
            fixed_model_name=fixed_model_name,
        )

    printing_success(
        "Nothing changed. You can use the old model stored at '{}'."
        "".format(os.path.abspath(old_model))
    )

    


    return old_model


async def _do_supervising(
    file_importer: TrainingDataImporter,
    output_path: Text,
    train_path: Text,
    fingerprint_comparison_result: Optional[FingerprintComparisonResult] = None,
    fixed_model_name: Optional[Text] = None,
    persist_nlu_training_data: bool = False,
    core_additional_arguments: Optional[Dict] = None,
    nlu_additional_arguments: Optional[Dict] = None,
    old_model_zip_path: Optional[Text] = None,
):
    


    if not fingerprint_comparison_result:
        fingerprint_comparison_result = FingerprintComparisonResult()

    interpreter_path = None
    if fingerprint_comparison_result.should_resupervise_nlu():
        

        model_path = await _train_nlu_with_validated_data_set(
            file_importer,
            output=output_path,
            train_path=train_path,
            set_model_name=fixed_model_name,
            persist_nlu_training_data=persist_nlu_training_data,
            add_on_arguments=nlu_additional_arguments,
        )
        interpreter_path = os.path.join(model_path, DEFAULT_NLU_SUB_DIRECTORY_NAME)
    else:
        printing_color(
            "NLU data/configuration did not change. No need to retrain NLU model.",
            color=convo.shared.utils.io.bcolours.OK_BLUE,
        )
    if fingerprint_comparison_result.should_resupervise_core():

        await _train_core_with_validated_data_set(
            file_importer,
            output=output_path,
            train_path=train_path,
            fixed_model_name=fixed_model_name,
            add_on_arguments=core_additional_arguments,
            interpreter=_interpreter_loaded(interpreter_path)
                        or _previous_model_interpreter(old_model_zip_path),
        )
    elif fingerprint_comparison_result.should_resupervise_nlg():
        printing_color(
            "Core stories/configuration did not change. "
            "Only the templates section has been changed. A new model with "
            "the updated templates will be created.",
            color=convo.shared.utils.io.bcolours.OK_BLUE,
        )
        await model.upgrade_model_with_new_domain(file_importer, train_path)
    else:
        printing_color(
            "Core stories/configuration did not change. No need to retrain Core model.",
            color=convo.shared.utils.io.bcolours.OK_BLUE,
        )


def _interpreter_loaded(
    interpreter_path: Optional[Text],
) -> Optional[NaturalLangInterpreter]:
    if interpreter_path:
        return convo.core.interpreter.generate_interpreter(interpreter_path)

    return None


def _previous_model_interpreter(
    old_model_zip_path: Optional[Text],
) -> Optional[NaturalLangInterpreter]:
    if not old_model_zip_path:
        return None

    with model.unpacking_model(old_model_zip_path) as unpacked:
        _, old_nlu = model.fetch_model_subdirectories(unpacked)
        return convo.core.interpreter.generate_interpreter(old_nlu)


def supervise_core(
    domain: Union[Domain, Text],
    config: Text,
    stories: Text,
    output: Text,
    train_path: Optional[Text] = None,
    fixed_model_name: Optional[Text] = None,
    add_on_arguments: Optional[Dict] = None,
) -> Optional[Text]:
    return convo.utils.common.running_in_loop(
        train_core_asynchronous(
            domain=domain,
            config=config,
            stories=stories,
            output=output,
            train_path=train_path,
            fixed_model_name=fixed_model_name,
            add_on_arguments=add_on_arguments,
        )
    )


async def train_core_asynchronous(
    domain: Union[Domain, Text],
    config: Text,
    stories: Text,
    output: Text,
    train_path: Optional[Text] = None,
    fixed_model_name: Optional[Text] = None,
    add_on_arguments: Optional[Dict] = None,
) -> Optional[Text]:
    """Trains a Core model.

    Args:
        domain: Path to the domain file.
        config: Path to the config file for Core.
        stories: Path to the Core training data.
        output: Output path.
        train_path: If `None` the model will be trained in a temporary
            dir, otherwise in the provided dir.
        fixed_model_name: Name of model to be stored.
        add_on_arguments: Additional training parameters.

    Returns:
        If `train_path` is given it returns the path to the model archive,
        otherwise the path to the dir with the trained model files.

    """

    file_importer = TrainingDataImporter.load_core_importer_from_configuration(
        config, domain, [stories]
    )
    domain = await file_importer.domain()
    if domain.is_empty():
        printing_error(
            "Core training was skipped because no valid domain file was found. "
            "Please specify a valid domain using '--domain' argument or check "
            "if the provided domain file exists."
        )
        return None

    if not await file_importer.fetch_stories():
        printing_error(
            "No stories given. Please provide stories in order to "
            "train a Convo Core model using the '--stories' argument."
        )
        return

    return await _train_core_with_validated_data_set(
        file_importer,
        output=output,
        train_path=train_path,
        fixed_model_name=fixed_model_name,
        add_on_arguments=add_on_arguments,
    )


async def _train_core_with_validated_data_set(
    file_importer: TrainingDataImporter,
    output: Text,
    train_path: Optional[Text] = None,
    fixed_model_name: Optional[Text] = None,
    add_on_arguments: Optional[Dict] = None,
    interpreter: Optional[Interpreter] = None,
) -> Optional[Text]:
    """Train Core with validated training and config data."""

    import convo.core.train

    

    

    

    

    

    


    with ExitStack() as stack:
        if train_path:
            # If the train path was provided, do nothing on exit.
            _train_path = train_path
        else:
            # Otherwise, create a temp train path and clean it up on exit.
            _train_path = stack.enter_context(TempDirPath(tempfile.mkdtemp()))

        # normal (not compare) training
        printing_color("Training Core model...", color=convo.shared.utils.io.bcolours.OK_BLUE)
        domain, config = await asyncio.gather(
            file_importer.domain(), file_importer.get_config()
        )
        async with telemetry.track_model_training(file_importer, model_type="core"):
            await convo.core.train(
                domain_file=domain,
                training_resource=file_importer,
                output_path=os.path.join(_train_path, DEFAULT_CORE_SUB_DIRECTORY_NAME),
                policy_config=config,
                extra_args=add_on_arguments,
                interpreter=interpreter,
            )
        printing_color(
            "Core model training completed.", color=convo.shared.utils.io.bcolours.OK_BLUE
        )

        if train_path is None:
            # Only Core was trained.
            new_fingerprint = await model.model_finger_print(file_importer)
            return model.pack_model(
                fingerprint=new_fingerprint,
                output_directory=output,
                train_path=_train_path,
                fixed_model_name=fixed_model_name,
                model_prefix="core-",
            )

        return _train_path


def supervise_nlu(
    config: Text,
    nlu_data: Text,
    output: Text,
    train_path: Optional[Text] = None,
    fixed_model_name: Optional[Text] = None,
    persist_nlu_training_data: bool = False,
    add_on_arguments: Optional[Dict] = None,
    domain: Optional[Union[Domain, Text]] = None,
) -> Optional[Text]:
    """Trains an NLU model.

    Args:
        config: Path to the config file for NLU.
        nlu_data: Path to the NLU training data.
        output: Output path.
        train_path: If `None` the model will be trained in a temporary
            dir, otherwise in the provided dir.
        fixed_model_name: Name of the model to be stored.
        persist_nlu_training_data: `True` if the NLU training data should be persisted
                                   with the model.
        add_on_arguments: Additional training parameters which will be passed to
                              the `train` method of each component.
        domain: Path to the optional domain file/Domain object.


    Returns:
        If `train_path` is given it returns the path to the model archive,
        otherwise the path to the dir with the trained model files.

    """

    return convo.utils.common.running_in_loop(
        _train_nlu_asynchronous(
            config,
            nlu_data,
            output,
            train_path,
            fixed_model_name,
            persist_nlu_training_data,
            add_on_arguments,
            domain=domain,
        )
    )


async def _train_nlu_asynchronous(
    config: Text,
    nlu_data: Text,
    output: Text,
    train_path: Optional[Text] = None,
    fixed_model_name: Optional[Text] = None,
    persist_nlu_training_data: bool = False,
    add_on_arguments: Optional[Dict] = None,
    domain: Optional[Union[Domain, Text]] = None,
) -> Optional[Text]:
    if not nlu_data:
        printing_error(
            "No NLU data given. Please provide NLU data in order to train "
            "a Convo NLU model using the '--nlu' argument."
        )
        return

    # training NLU only hence the training files still have to be selected
    file_importer = TrainingDataImporter.load_nlu_importer_from_configuration(
        config, domain, training_data_paths=[nlu_data]
    )

    training_data = await file_importer.fetch_nlu_data()
    if training_data.nlu_model_train_check():
        printing_error(
            f"Path '{nlu_data}' doesn't contain valid NLU data in it. "
            f"Please verify the data format. "
            f"The NLU model training will be skipped now."
        )
        return

    return await _train_nlu_with_validated_data_set(
        file_importer,
        output=output,
        train_path=train_path,
        set_model_name=fixed_model_name,
        persist_nlu_training_data=persist_nlu_training_data,
        add_on_arguments=add_on_arguments,
    )


async def _train_nlu_with_validated_data_set(
    file_importer: TrainingDataImporter,
    output: Text,
    train_path: Optional[Text] = None,
    set_model_name: Optional[Text] = None,
    persist_nlu_training_data: bool = False,
    add_on_arguments: Optional[Dict] = None,
) -> Optional[Text]:
    """Train NLU with validated training and config data."""

    import convo.nlu.train

    if add_on_arguments is None:
        add_on_arguments = {}

    with ExitStack() as stack:
        if train_path:
            # If the train path was provided, do nothing on exit.
            _train_path = train_path
        else:
            # Otherwise, create a temp train path and clean it up on exit.
            _train_path = stack.enter_context(TempDirPath(tempfile.mkdtemp()))
        config = await file_importer.get_config()
        printing_color("Training NLU model...", color=convo.shared.utils.io.bcolours.OK_BLUE)
        async with telemetry.track_model_training(file_importer, model_type="nlu"):
            await convo.nlu.training(
                config,
                file_importer,
                _train_path,
                fixed_model_name="nlu",
                persist_nlu_training_data=persist_nlu_training_data,
                **add_on_arguments,
            )
        printing_color(
            "NLU model training completed.", color=convo.shared.utils.io.bcolours.OK_BLUE
        )

        if train_path is None:
            # Only NLU was trained
            new_fingerprint = await model.model_finger_print(file_importer)

            return model.pack_model(
                fingerprint=new_fingerprint,
                output_directory=output,
                train_path=_train_path,
                fixed_model_name=set_model_name,
                model_prefix="nlu-",
            )

        return _train_path
