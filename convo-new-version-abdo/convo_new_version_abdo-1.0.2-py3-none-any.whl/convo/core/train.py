import argparse
import asyncio
import logging
import os
import tempfile
import typing
from typing import Dict, Optional, Text, Union, List

import convo.shared.utils.io
import convo.utils.io
from convo.constants import NO_OF_TRAINING_STORY_FILE, PERCENTAGE_WISE_KEY
from convo.shared.core.domain import Domain
from convo.shared.importers.importer import TrainingDataImporter
from convo.utils.common import TempDirPath

if typing.TYPE_CHECKING:
    from convo.shared.nlu.interpreter import NaturalLangInterpreter
    from convo.core.utils import AvailableEndpoints


log = logging.getLogger(__name__)


async def train(
    domain_file: Union[Domain, Text],
    training_resource: Union[Text, "TrainingDataImporter"],
    output_path: Text,
    interpreter: Optional["NaturalLangInterpreter"] = None,
    last_points: "AvailableEndpoints" = None,
    policy_config: Optional[Union[Text, Dict]] = None,
    exclusion_percentage: Optional[int] = None,
    extra_args: Optional[Dict] = None,
):
    from convo.core.agent import CoreAgent
    from convo.core import config, utils
    from convo.core.utils import AvailableEndpoints



    if not last_points:
        last_points = AvailableEndpoints()

    if not extra_args:
        extra_args = {}

    guidelines = config.load(policy_config)

    train_agent = CoreAgent(
        domain_file,
        generator=last_points.nlg,
        action_endpoint=last_points.action,
        interpreter=interpreter,
        policies=guidelines,
    )

    data_set_load_arguments, extra_args = utils.additional_arguments(
        extra_args,
        {
            "use_story_concatenation",
            "unique_last_num_of_states",
            "augmentation_factor",
            "remove_identical",
            "debug_plots",
        },
    )
    training_data_set = await train_agent.load_data_set(
        training_resource, exclusion_percentage=exclusion_percentage, **data_set_load_arguments
    )
    train_agent.train(training_data_set, **extra_args)
    train_agent.persist(output_path)

    return train_agent


async def train_differentiation_between_models(
    story_file: Text,
    domain: Text,
    output_path: Text = "",
    eliminate_percentage: Optional[List] = None,
    policy_configurations: Optional[List] = None,
    runs: int = 1,
    add_on_arguments: Optional[Dict] = None,
):
    """Train multiple models for comparison of policies"""
    from convo import model

    eliminate_percentage = eliminate_percentage or []
    policy_configurations = policy_configurations or []

    for r in range(runs):
        logging.info("Starting run {}/{}".format(r + 1, runs))

        for current_run, percentage in enumerate(eliminate_percentage, 1):
            for policy_config in policy_configurations:

                importer_files = TrainingDataImporter.load_core_importer_from_configuration(
                    policy_config, domain, [story_file]
                )

                configuration_name = os.path.splitext(os.path.basename(policy_config))[0]
                logging.info(
                    "Starting to train {} round {}/{}"
                    " with {}% exclusion"
                    "".format(
                        configuration_name, current_run, len(eliminate_percentage), percentage
                    )
                )

                with TempDirPath(tempfile.mkdtemp()) as train_path:
                    _, new_fingerprint = await asyncio.gather(
                        train(
                            domain,
                            importer_files,
                            train_path,
                            policy_config=policy_config,
                            exclusion_percentage=percentage,
                            extra_args=add_on_arguments,
                        ),
                        model.model_finger_print(importer_files),
                    )

                    output_directory = os.path.join(output_path, "run_" + str(r + 1))
                    name_of_model = configuration_name + PERCENTAGE_WISE_KEY + str(percentage)
                    model.pack_model(
                        fingerprint=new_fingerprint,
                        output_directory=output_directory,
                        train_path=train_path,
                        fixed_model_name=name_of_model,
                    )


async def fetch_no_of_stories(story_file: Text, domain: Text) -> int:
    """Get number of stories in a file."""
    from convo.shared.core.domain import Domain
    from convo.shared.core.training_data import loading

    trained_stories = await loading.loadDataFromFiles([story_file], Domain.load(domain))
    return len(trained_stories)


async def have_comparative_training(
    args: argparse.Namespace,
    story_file: Text,
    add_on_arguments: Optional[Dict] = None,
):
    _, number_stories = await asyncio.gather(
        train_differentiation_between_models(
            story_file=story_file,
            domain=args.domain,
            output_path=args.out,
            eliminate_percentage=args.percentages,
            policy_configurations=args.config,
            runs=args.runs,
            add_on_arguments=add_on_arguments,
        ),
        fetch_no_of_stories(args.stories, args.domain),
    )

    # store the list of the number of stories present at each exclusion
    # percentage
    story_scope = [
        number_stories - round((x / 100.0) * number_stories) for x in args.percentages
    ]

    training_story_for_specific_model_file = os.path.join(
        args.out, NO_OF_TRAINING_STORY_FILE
    )
    convo.shared.utils.io.dump_object_as_json_to_file(
        training_story_for_specific_model_file, story_scope
    )


def have_interactive_learning(
    args: argparse.Namespace, file_importer: TrainingDataImporter
):
    from convo.core.training import interactive

    interactive.execute_interactive_learning(
        file_importer=file_importer,
        skip_visualization=args.skip_visualization,
        conversation_id=args.conversation_id,
        server_arguments=args.__dict__,
    )
