def tokens_to_ids(examples, token2id, name='stream'):
    r''' Convert tokens to ids, used as a map function in the datasets module from HF.

    Args:
        examples (
        token2id (`Dict[str, int]`, `required`):
            Map from tokens to ids.
        name (`str`, `optional`, defaults to `stream`):
            What `key` in examples contains the data that has to be converted.
    '''
    examples[name] = [[token2id[tkn] for tkn in example] for example in examples[name]]

    return examples
