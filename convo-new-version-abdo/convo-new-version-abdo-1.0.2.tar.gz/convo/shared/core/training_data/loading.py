import logging
import os
from pathlib import Path
from typing import Text, Optional, Dict, List, Union

import convo.shared.data
import convo.shared.utils.io
from convo.shared.core.domain import Domain
from convo.shared.core.training_data.story_reader.markdown_story_reader import (
    MarkdownStoryReviewer,
)
from convo.shared.core.training_data.story_reader.story_reader import storyReviewer
from convo.shared.core.training_data.story_reader.yaml_story_reader import (
    YAMLStoryReviewer,
)
from convo.shared.core.training_data.structures import StoryStage
from convo.shared.data import CONVO_YAML_FILE_EXTENSIONS, MARK_DOWN_FILE_EXTENSIONS 

log = logging.getLogger(__name__)


def getReader(
    filename: Text,
    domain: Domain,
    template_variables: Optional[Dict] = None,
    use_e2e: bool = False,
) -> storyReviewer:

    if convo.shared.data.is_mark_down_file (filename):
        return MarkdownStoryReviewer(domain, template_variables, use_e2e, filename)
    elif convo.shared.data.is_yaml_file (filename):
        return YAMLStoryReviewer(domain, template_variables, use_e2e, filename)
    else:
        # This is a use case for uploading the story over REST API.
        # The source file has a random name.
        return guessReader(filename, domain, template_variables, use_e2e)


def guessReader(
    filename: Text,
    domain: Domain,
    template_variables: Optional[Dict] = None,
    use_e2e: bool = False,
) -> storyReviewer:
    if YAMLStoryReviewer.isStoriesFile(filename):
        return YAMLStoryReviewer(domain, template_variables, use_e2e, filename)
    elif MarkdownStoryReviewer.isStoriesFile(filename):
        return MarkdownStoryReviewer(domain, template_variables, use_e2e, filename)
    raise ValueError(
        f"Failed to find a reader class for the story file `{filename}`. "
        f"Supported formats are "
        f"{', '.join(MARK_DOWN_FILE_EXTENSIONS  + CONVO_YAML_FILE_EXTENSIONS)}."
    )


async def loadDataFromResource(
    resource: Union[Text, Path],
    domain: Domain,
    template_variables: Optional[Dict] = None,
    use_e2e: bool = False,
    exclusion_percentage: Optional[int] = None,
) -> List["StoryStage"]:
    """Loads core training data from the specified folder.

    Args:
        resource: Folder/File with core training data files.
        domain: Domain object.
        template_variables: Variables that have to be replaced in the training data.
        use_e2e: Identifies if the e2e reader should be used.
        exclusion_percentage: Identifies the percentage of training data that
                              should be excluded from the training.

    Returns:
        Story steps from the training data.
    """
    if not os.path.exists(resource):
        raise ValueError(f"Resource '{resource}' does not exist.")

    return await loadDataFromFiles(
        convo.shared.utils.io.listing_files(resource),
        domain,
        template_variables,
        use_e2e,
        exclusion_percentage,
    )


async def loadDataFromFiles(
    all_story_files: List[Text],
    domain: Domain,
    template_variables: Optional[Dict] = None,
    use_e2e: bool = False,
    exclusion_percentage: Optional[int] = None,
) -> List["StoryStage"]:
    """Loads core training data from the specified files.

    Args:
        all_story_files: List of files with training data in it.
        domain: Domain object.
        template_variables: Variables that have to be replaced in the training data.
        use_e2e: Identifies whether the e2e reader should be used.
        exclusion_percentage: Identifies the percentage of training data that
                              should be excluded from the training.

    Returns:
        Story procedures from the training data.
    """
    storySteps = []

    for story_file in all_story_files:
        reviewer = getReader(story_file, domain, template_variables, use_e2e)

        procedures = reviewer.readFromFile(story_file)
        storySteps.extend(procedures)

    if exclusion_percentage and exclusion_percentage != 100:
        import random

        index = int(round(exclusion_percentage / 100.0 * len(storySteps)))
        random.shuffle(storySteps)
        storySteps = storySteps[:-index]

    return storySteps
