import functools

"""
"
" decorator for metadata definition
"
"""
def metadata(name, namespace, index, dataframe, **kwargs):
    """
    @param::name: the name of feature artifact
    @param::namespace: the namespace it belongs to
    @param::index: the index of the dataframe
    @param::dataframe: the dataframe type
    @param::kwargs: the keyword argument list
    return the decorated feature function with metadata attribute attached.
    """
    def feature_decorator(func):
        from dimsum.core.metadata_builder import MetadataBuilder
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        metadata = MetadataBuilder.feature(name, index, dataframe, namespace)
        if 'author' in kwargs:
            metadata.author = kwargs['author']
        if 'params' in kwargs:
            metadata.params = kwargs['params']
        if 'comment' in kwargs:
            metadata.comment = kwargs['comment']
        if 'versioning' in kwargs:
            metadata.versioning = kwargs['versioning']
        if 'tags' in kwargs:
            metadata.tags = set(kwargs['tags'])
        wrapper.metadata = metadata
        return wrapper
    return feature_decorator

