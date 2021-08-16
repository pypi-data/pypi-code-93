"""builder.py module."""


class CDSRBuilderException(Exception):
    """CDSRBuilderException."""


def build_collection(metadata: dict) -> str:
    """Builds collection name based on metadata dict."""

    # check metadata type
    if not isinstance(metadata, dict):
        raise CDSRBuilderException(f'Metadata must be a dict, not a `{type(metadata)}`.')

    # mandatory keys
    keys = ['satellite', 'sensor', 'geo_processing', 'radio_processing']

    # get all keys that are missing inside metadata dict
    missing_keys = [k for k in keys if k not in metadata]

    if missing_keys:
        raise CDSRBuilderException(f"Missing keys inside metadata: `{', '.join(missing_keys)}`.")

    # get all keys inside metadata that their values are not strings
    not_str_keys = [k for k in keys if not isinstance(metadata[k], str)]

    if not_str_keys:
        raise CDSRBuilderException('All mandatory values inside metadata dict must be strings, but '
                                  f"the following keys are not: `{', '.join(not_str_keys)}`.")

    return f"{metadata['satellite']}_{metadata['sensor']}_" \
           f"L{metadata['geo_processing']}_{metadata['radio_processing']}"


def build_item(metadata: dict) -> str:
    """Builds item name based on metadata dict."""

    # check metadata type
    if not isinstance(metadata, dict):
        raise CDSRBuilderException(f'Metadata must be a dict, not a `{type(metadata)}`.')

    # mandatory keys
    keys = ['satellite', 'sensor', 'path', 'row', 'date', 'antenna']

    # get all keys that are missing inside metadata dict
    missing_keys = [k for k in keys if k not in metadata]

    if missing_keys:
        raise CDSRBuilderException(f"Missing keys inside metadata: `{', '.join(missing_keys)}`.")

    # get all keys inside metadata that their values are not strings
    not_str_keys = [k for k in keys if not isinstance(metadata[k], str)]

    if not_str_keys:
        raise CDSRBuilderException('All mandatory values inside metadata dict must be strings, but '
                                  f"the following keys are not: `{', '.join(not_str_keys)}`.")

    return f"{metadata['satellite']}_{metadata['sensor']}_" \
           f"{metadata['path']}{metadata['row']}_{metadata['date'].replace('-', '')}_" \
           f"{metadata['antenna']}"
