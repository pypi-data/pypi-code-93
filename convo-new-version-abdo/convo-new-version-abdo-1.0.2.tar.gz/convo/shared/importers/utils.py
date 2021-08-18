from typing import Iterable, Text, Optional, Dict, List

from convo.shared.core.domain import Domain
from convo.shared.core.training_data.structures import StoryPlot
from convo.shared.nlu.training_data.training_data import TrainingDataSet


def training_dataset_from_paths(convo_paths: Iterable[Text], language: Text) -> TrainingDataSet:
    from convo.shared.nlu.training_data import loading

    training_datasets = [loading.load_data_set(nlu_file, language) for nlu_file in convo_paths]
    return TrainingDataSet().merge(*training_datasets)


async def story_graph_from_path(
    files: List[Text],
    domain: Domain,
    template_variables: Optional[Dict] = None,
    use_e2e: bool = False,
    exclusion_percentage: Optional[int] = None,
) -> StoryPlot:

    from convo.shared.core.training_data import loading

    story_step = await loading.loadDataFromFiles(
        files, domain, template_variables, use_e2e, exclusion_percentage
    )
    return StoryPlot(story_step)
