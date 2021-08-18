
from constellate.client import (
    get_description,
    get_metadata,
    get_dataset,
    dataset_reader,
    download_gutenberg_sample
)


# Jupyter Extension points
def _jupyter_nbextension_paths():
    return [dict(
        section="notebook",
        src="./static",
        dest="constellate-plugin",
        require="constellate-plugin/main")]
