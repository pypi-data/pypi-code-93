import logging
import os
from typing import Text

from convo import telemetry
from convo.shared.utils.cli import printing_error

from convo.shared.core.domain import InvalidDomain

log = logging.getLogger(__name__)


async def visualize(
    config_path: Text,
    domain_path: Text,
    stories_path: Text,
    nlu_data_path: Text,
    output_path: Text,
    max_history: int,
):
    from convo.core.agent import CoreAgent
    from convo.core import config

    try:
        policies = config.load(config_path)
    except ValueError as e:
        printing_error(
            "Could not load config due to: '{}'. To specify a valid config file use "
            "the '--config' argument.".format(e)
        )
        return

    try:
        visualize_agent = CoreAgent(domain=domain_path, policies=policies)
    except InvalidDomain as e:
        printing_error(
            "Could not load domain due to: '{}'. To specify a valid domain path use "
            "the '--domain' argument.".format(e)
        )
        return

    # this is optional, only needed if the `/greet` type of
    # messages in the stories should be replaced with actual
    # messages (e.g. `hello`)
    if nlu_data_path is not None:
        import convo.shared.nlu.training_data.loading

        nlu_train_data = convo.shared.nlu.training_data.loading.load_data_set(
            nlu_data_path
        )
    else:
        nlu_train_data = None

    log.info("Starting to visualize stories...")
    telemetry.traverse_visualization()
    await visualize_agent.fetch_visualization(
        stories_path, output_path, max_history, nlu_training_data=nlu_train_data
    )

    full_output_path = "file://{}".format(os.path.abspath(output_path))
    log.info(f"Finished graph creation. Saved into {full_output_path}")

    import webbrowser

    webbrowser.open(full_output_path)
