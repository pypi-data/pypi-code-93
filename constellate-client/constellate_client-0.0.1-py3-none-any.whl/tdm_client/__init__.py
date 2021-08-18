import warnings

msg = "The tdm_client has been renamed to Constellate. Please update your code to use import constellate."

print(f"Warning: {msg}")


from constellate.client import (
    get_description,
    get_metadata,
    get_dataset,
    dataset_reader,
    download_gutenberg_sample
)