def stream_to_separate_examples(examples):
    r''' Convert a stream to separate examples that can be used to train
    a next concept predictor unable to handle sequences. Use with HF datasets map function.

    '''
    out = {}
    out['input_ids'] = [example[0:i+1] for example in examples['stream'] for i in range(len(example) - 1)]
    out['labels'] = [example[i+1] for example in examples['stream'] for i in range(len(example) - 1)]

    return out
