from nr_common.search import NRRecordsSearch


class DatasetRecordSearch(NRRecordsSearch):
    """Dataset collection search."""
    LIST_SOURCE_FIELDS = [
        'id', 'oarepo:validity.valid', 'oarepo:draft',
        'title', 'abstract', 'creators', 'dates', 'resource_type',
        'contributor', 'keywords', 'subject', 'abstract', 'state', 'languages',
        '_primary_community', '_communities', 'access'
        '$schema', '_files'
    ]
    HIGHLIGHT_FIELDS = {
        'title.cs': None,
        'title._': None,
        'title.en': None
    }
