import asyncio
import json
from pathlib import Path
from typing import List, Text

import click
import randomname
from rich.console import Console

from neuralspace.apis import get_async_http_session
from neuralspace.constants import NAME_GENERATOR_CONFIG
from neuralspace.nlu.apis import (
    create_project,
    delete_examples,
    delete_models,
    delete_project,
    deploy,
    get_languages,
    list_examples,
    list_models,
    list_projects,
    parse,
    train_model,
    upload_dataset,
    wait_till_training_completes,
)
from neuralspace.nlu.constants import SUPPORTED_LANGUAGES, TRAINING_PROGRESS
from neuralspace.utils import print_logo, setup_logger

console = Console()


@click.group(name="nlu")
def nlu():
    pass


@nlu.command(name="get-languages")
@click.option(
    "-l", "--log-level", type=click.Choice(["INFO", "DEBUG", "ERROR"]), default="INFO"
)
def nlu_get_languages(log_level: Text):
    setup_logger(log_level=log_level)
    loop = asyncio.new_event_loop()
    loop.run_until_complete(get_languages())
    loop.run_until_complete(get_async_http_session().close())


@nlu.command(name="create-project")
@click.option(
    "-p",
    "--project-name",
    type=click.STRING,
    required=False,
    help="Project Name",
)
@click.option(
    "-L",
    "--languages",
    type=click.STRING,
    multiple=True,
    required=True,
    help="List of languages. -L en -L de; You can add multiple languages",
)
@click.option(
    "-l", "--log-level", type=click.Choice(["INFO", "DEBUG", "ERROR"]), default="INFO"
)
def nlu_create_project(project_name: Text, languages: List[Text], log_level: Text):
    setup_logger(log_level=log_level)
    languages = list(languages)
    if project_name is None:
        project_name = randomname.get_name(**NAME_GENERATOR_CONFIG)
    if not languages:
        ValueError(f"Languages is mandatory. You can select from {SUPPORTED_LANGUAGES}")
    loop = asyncio.new_event_loop()
    loop.run_until_complete(create_project(project_name, languages))
    loop.run_until_complete(get_async_http_session().close())


@nlu.command(name="delete-project")
@click.option(
    "-p",
    "--project-id",
    type=click.STRING,
    required=True,
    help="Project id",
)
@click.option(
    "-l", "--log-level", type=click.Choice(["INFO", "DEBUG", "ERROR"]), default="INFO"
)
def nlu_delete_project(project_id: Text, log_level: Text):
    setup_logger(log_level=log_level)
    loop = asyncio.new_event_loop()
    loop.run_until_complete(delete_project(project_id))
    loop.run_until_complete(get_async_http_session().close())


@nlu.command(name="list-projects")
@click.option(
    "-S",
    "--search",
    type=click.STRING,
    required=False,
    default="",
    help="Substring search",
)
@click.option(
    "-p",
    "--page-number",
    type=click.INT,
    required=False,
    default=1,
    help="Which page number to fetch",
)
@click.option(
    "-s",
    "--page-size",
    type=click.INT,
    required=False,
    default=20,
    help="items per page to fetch",
)
@click.option(
    "-L",
    "--language",
    type=click.STRING,
    multiple=True,
    default=[],
    help="List of languages. E.g., -L en -L de; You can add multiple languages",
)
@click.option(
    "-l", "--log-level", type=click.Choice(["INFO", "DEBUG", "ERROR"]), default="INFO"
)
def nlu_list_projects(
    search: Text,
    page_number: int,
    page_size: int,
    language: List[Text],
    log_level: Text,
):
    setup_logger(log_level=log_level)
    languages = list(language)
    if not languages:
        ValueError(f"Languages is mandatory. You can select from {SUPPORTED_LANGUAGES}")
    loop = asyncio.new_event_loop()
    loop.run_until_complete(list_projects(search, page_size, page_number, languages))
    loop.run_until_complete(get_async_http_session().close())


@nlu.command(name="upload-dataset")
@click.option(
    "-d",
    "--dataset-file",
    type=click.Path(exists=True, dir_okay=False),
    required=True,
    help="an nlu dataset file",
)
@click.option(
    "-p",
    "--project-id",
    type=click.STRING,
    required=True,
    help="NLU project id",
)
@click.option(
    "-L",
    "--language",
    type=click.Choice(SUPPORTED_LANGUAGES),
    required=True,
    help="Language",
)
@click.option(
    "-s",
    "--skip-first",
    type=click.INT,
    required=False,
    default=0,
    help="Skip this many example from the beginning",
)
@click.option(
    "-e",
    "--ignore-errors",
    type=click.BOOL,
    required=False,
    default=False,
    help="to ignore errors and go to the next example",
)
@click.option(
    "-l", "--log-level", type=click.Choice(["INFO", "DEBUG", "ERROR"]), default="INFO"
)
def nlu_upload_dataset(
    dataset_file: Path,
    project_id: Text,
    language: Text,
    skip_first: int,
    ignore_errors: bool,
    log_level: Text,
):
    setup_logger(log_level=log_level)
    dataset = json.loads(Path(dataset_file).read_text())
    loop = asyncio.new_event_loop()
    loop.run_until_complete(
        upload_dataset(
            dataset,
            project_id=project_id,
            language=language,
            skip_first=skip_first,
            ignore_errors=ignore_errors,
        )
    )
    loop.run_until_complete(get_async_http_session().close())


@nlu.command(name="list-examples")
@click.option(
    "-p",
    "--project-id",
    type=click.STRING,
    required=True,
    help="Project ID",
)
@click.option(
    "-L",
    "--language",
    type=click.STRING,
    required=True,
    help="Language",
)
@click.option(
    "-P",
    "--prepared",
    type=click.Choice(["true", "false"]),
    required=False,
    default="true",
    help="Flag to filter only prepared examples",
)
@click.option(
    "-t",
    "--type",
    type=click.Choice(["train", "test"]),
    required=False,
    default="train",
    help="Flag to filter only prepared examples",
)
@click.option(
    "-i",
    "--intent",
    type=click.STRING,
    required=False,
    help="Flag to filter examples only in this intent",
)
@click.option(
    "-n",
    "--page-number",
    type=click.INT,
    required=False,
    default=1,
    help="Which page number to fetch",
)
@click.option(
    "-s",
    "--page-size",
    type=click.INT,
    required=False,
    default=20,
    help="items per page to fetch",
)
@click.option(
    "-l", "--log-level", type=click.Choice(["INFO", "DEBUG", "ERROR"]), default="INFO"
)
def nlu_list_examples(
    project_id: Text,
    language: Text,
    prepared: Text,
    type: Text,
    intent: Text,
    page_number: int,
    page_size: int,
    log_level: Text,
):

    setup_logger(log_level=log_level)
    prepared_flag = False
    if prepared == "true":
        prepared_flag = True
    loop = asyncio.new_event_loop()
    loop.run_until_complete(
        list_examples(
            project_id, language, prepared_flag, type, intent, page_number, page_size
        )
    )
    loop.run_until_complete(get_async_http_session().close())


@nlu.command(name="delete-example")
@click.option(
    "-e",
    "--example-id",
    type=click.STRING,
    required=True,
    multiple=True,
    help="Example ID",
)
@click.option(
    "-l", "--log-level", type=click.Choice(["INFO", "DEBUG", "ERROR"]), default="INFO"
)
def nlu_delete_example(example_id: List[Text], log_level: Text):
    setup_logger(log_level=log_level)
    example_ids = list(example_id)
    loop = asyncio.new_event_loop()
    loop.run_until_complete(delete_examples(example_ids))
    loop.run_until_complete(get_async_http_session().close())


@nlu.command(name="train")
@click.option(
    "-p",
    "--project-id",
    type=click.STRING,
    required=False,
    help="Project ID",
)
@click.option(
    "-L",
    "--language",
    type=click.STRING,
    required=False,
    help="Language",
)
@click.option(
    "-m",
    "--model-name",
    type=click.STRING,
    required=False,
    help="Name of the model",
)
@click.option(
    "-w",
    "--wait",
    type=click.BOOL,
    required=False,
    default=True,
    help="Wait for training to complete",
)
@click.option(
    "-i",
    "--wait-interval",
    type=click.INT,
    required=False,
    default=1,
    help="Time to wait between consecutive pools.",
)
def nlu_train_model(
    project_id: Text, language: Text, model_name: Text, wait: bool, wait_interval: int
):

    if project_id and language:
        print_logo()
        if model_name is None:
            model_name = randomname.get_name(**NAME_GENERATOR_CONFIG)
        loop = asyncio.new_event_loop()
        loop.run_until_complete(
            train_model(project_id, language, model_name, wait, wait_time=wait_interval)
        )
        loop.run_until_complete(get_async_http_session().close())
    else:
        list_projects()


@nlu.command(name="model-status")
@click.option(
    "-m",
    "--model-id",
    type=click.STRING,
    required=True,
    help="Model ID",
)
@click.option(
    "-w",
    "--wait",
    type=click.BOOL,
    required=False,
    default=True,
    help="Wait for training to complete",
)
@click.option(
    "-i",
    "--wait-interval",
    type=click.INT,
    required=False,
    default=1,
    help="Time to wait between consecutive pools.",
)
@click.option(
    "-l", "--log-level", type=click.Choice(["INFO", "DEBUG", "ERROR"]), default="INFO"
)
def nlu_check_model_status(
    model_id: Text, wait: bool, wait_interval: int, log_level: Text
):
    setup_logger(log_level=log_level)
    print_logo()
    loop = asyncio.new_event_loop()
    loop.run_until_complete(wait_till_training_completes(model_id, wait, wait_interval))
    loop.run_until_complete(get_async_http_session().close())


@nlu.command(name="list-models")
@click.option(
    "-p",
    "--project-id",
    type=click.STRING,
    required=True,
    help="Project ID",
)
@click.option(
    "-L",
    "--language",
    type=click.STRING,
    required=True,
    help="Language",
)
@click.option(
    "-s",
    "--training-status",
    type=click.STRING,
    required=False,
    help=f"Flag to filter models with the given training status. "
    f"These are some valid values: {', '.join(TRAINING_PROGRESS)}",
)
@click.option(
    "-n",
    "--page-number",
    type=click.INT,
    required=False,
    default=1,
    help="Which page number to fetch",
)
@click.option(
    "-s",
    "--page-size",
    type=click.INT,
    required=False,
    default=20,
    help="items per page to fetch",
)
@click.option(
    "-l", "--log-level", type=click.Choice(["INFO", "DEBUG", "ERROR"]), default="INFO"
)
def nlu_list_models(
    project_id: Text,
    language: Text,
    training_status: List[Text],
    page_number: int,
    page_size: int,
    log_level: Text,
):

    setup_logger(log_level=log_level)
    if training_status:
        training_status = list(training_status)
    loop = asyncio.new_event_loop()
    loop.run_until_complete(
        list_models(project_id, language, training_status, page_number, page_size)
    )
    loop.run_until_complete(get_async_http_session().close())


@nlu.command(name="delete-model")
@click.option(
    "-m",
    "--model-id",
    type=click.STRING,
    required=True,
    help="Model ID",
)
@click.option(
    "-l", "--log-level", type=click.Choice(["INFO", "DEBUG", "ERROR"]), default="INFO"
)
def nlu_delete_model(model_id: Text, log_level: Text):
    setup_logger(log_level=log_level)
    loop = asyncio.new_event_loop()
    loop.run_until_complete(delete_models(model_id))
    loop.run_until_complete(get_async_http_session().close())


@nlu.command(name="deploy")
@click.option(
    "-m",
    "--model-id",
    type=click.STRING,
    required=True,
    help="Model ID",
)
@click.option(
    "-n",
    "--n-replicas",
    type=click.INT,
    required=False,
    default=1,
    help="Number of replicas  to deploy for this model",
)
@click.option(
    "-l", "--log-level", type=click.Choice(["INFO", "DEBUG", "ERROR"]), default="INFO"
)
def nlu_deploy(model_id: Text, n_replicas: int, log_level: Text):

    setup_logger(log_level=log_level)
    loop = asyncio.new_event_loop()
    loop.run_until_complete(deploy(model_id, n_replicas))
    loop.run_until_complete(get_async_http_session().close())


@nlu.command(name="parse")
@click.option(
    "-m",
    "--model-id",
    type=click.STRING,
    required=True,
    help="Model ID",
)
@click.option(
    "-i",
    "--input-text",
    type=click.STRING,
    required=True,
    help="Number of replicas  to deploy for this model",
)
@click.option(
    "-l", "--log-level", type=click.Choice(["INFO", "DEBUG", "ERROR"]), default="INFO"
)
def nlu_parse(model_id: Text, input_text: Text, log_level: Text):
    setup_logger(log_level=log_level)
    loop = asyncio.new_event_loop()
    loop.run_until_complete(parse(model_id, input_text))
    loop.run_until_complete(get_async_http_session().close())
