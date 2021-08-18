import os
import hashlib
import pandas as pd


def is_member_variable(obj, identifier):
    return not callable(getattr(obj, identifier)) and \
        not identifier.startswith("__")


def hash_id(file, args):
    args = [
        (ident, getattr(args, ident)) for ident in dir(args)
        if is_member_variable(args, ident)
    ]
    string = file + str(sorted(args))
    return hashlib.md5(string.encode()).hexdigest()


def write_results(file, args, results):

    # args is a Argumentparser object
    identifier = hash_id(file, args)
    results['id'] = identifier
    results['file'] = file

    for ident in dir(args):
        if is_member_variable(args, ident):
            results[ident] = getattr(args, ident)

    frame = pd.DataFrame([results], columns=list(results.keys()))
    frame = frame.set_index('id')

    os.makedirs('args_to_db_cache', exist_ok=True)

    frame.to_pickle(f'args_to_db_cache/{identifier}.pkl')
    # frame.to_csv(f'args_to_db_cache/{id}.csv')
