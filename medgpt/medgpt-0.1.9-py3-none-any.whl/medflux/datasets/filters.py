def filter_by_count(dataset, min_count=5, min_length=5):
    r''' Filters tokens of a dataset and leaves only the ones with frequencey >= min_count

    Args:
        dataset
        min_count
        min_length:
            Examples below will be removed, in other words patients with less than min_length concepts
    '''
    token_cnt = {}
    for stream in dataset['stream']:
        for tkn in stream:
            token_cnt[tkn] = token_cnt.get(tkn, 0) + 1

    dataset = dataset.map(function=lambda example: {'stream': [token for token in example['stream'] if token_cnt[token] >= min_count]},
                      load_from_cache_file=False)

    if min_length > 0:
        dataset = dataset.filter(function=lambda example: len(example['stream']) >=  min_length)

    return dataset
