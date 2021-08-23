import datetime as dt

"""
"   Creates a new dataset reference to be stored in the registry
"""
def create_dataset_reference(uid, **kwargs):
    """
    @param::key: key identifying the registry entrant
    @param::uid: unique id that identifies the cached feature dataset
    @param::kwargs: additional properties to include in dataset_reference
    Returns dataset_reference dictionary object
    """
    _UID = 'uid'
    _CREATED_AT = 'created_at'
    _CACHE_DURATION = 'cache_duration'
    _EXPIRATION_DATE = 'expiration_date'

    new_dataset_reference = {
        _UID: str(uid),
        _CREATED_AT: dt.datetime.now()
    }
    # Additional information on dataset node
    for arg in kwargs:
        if arg not in new_dataset_reference:
            if arg == _CACHE_DURATION:
                cache_duration = kwargs[_CACHE_DURATION] # cache duration in number of days
                expiration_date = dt.date.today() + dt.timedelta(days=cache_duration)
                new_dataset_reference[_EXPIRATION_DATE] = expiration_date
            else:
                new_dataset_reference[arg] = kwargs[arg]
    return new_dataset_reference

"""
" Removes all expired dataset_references from cache registry dictionary
" Pass-by-reference parameter for non-additional space complexity
"""
def remove_all_expired(cache_registry):
    """
    @param::cache_registry: pass-by-reference dictionary object, removes expired in-place
    """
    for key, dataset_reference in list(cache_registry.items()):
        if is_expired(dataset_reference):
            cache_registry.pop(key)

"""
" Checks if dataset is expired and removes it if it is expired
"""
def is_expired(dataset_reference):
    """
    @param::dataset_reference: dictionary containing reference/info of the cached dataset
    Returns false if dataset is not expired, true if it is expired
    """
    _EXPIRATION_DATE = 'expiration_date'

    try:
        if not isinstance(dataset_reference, dict):
            raise TypeError('> is_expired: dataset_reference is not a dictionary type!')

        expiration_date = dataset_reference.get(_EXPIRATION_DATE)
        if expiration_date is None or expiration_date >= dt.date.today():
            return False
        return True
    except Exception as e:
        print(e)
        raise

"""
"   Converts <datetime> in value to a string
"""
def stringify_datetime(dataset_reference):
    """
    @param::dataset_reference: dictionary containing information on dataset
    Returns modified dataset_reference, where all <datetime> types converted to string
    """
    for key, value in dataset_reference.items():
        if isinstance(value, (dt.date, dt.datetime, dt.time, dt.timezone)):
            dataset_reference[key] = str(value)
    return dataset_reference