import hashlib
import pandas
import os

results_dict = {}

def results():
    return results_dict


def add_result(identifier, value):
    results_dict[identifier] = value


def is_member_variable(object, identifier):
    return not callable(getattr(object, identifier)) and not identifier.startswith("__")


def hash_id(file, args):
    args = [(ident, getattr(args, ident)) for ident in dir(args) if is_member_variable(args, ident)]
    string = file + str(sorted(args))
    return hashlib.md5(string.encode()).hexdigest()


def write_results(file, args):
    global results_dict

    # args is a Argumentparser object
    id = hash_id(file, args)
    results_dict['id'] = id
    results_dict['file'] = file

    for ident in dir(args):
        if is_member_variable(args, ident):
            results_dict[ident] = getattr(args, ident)

    results = pandas.DataFrame([results_dict], columns=list(results_dict.keys()))
    results = results.set_index('id')

    os.makedirs('args_to_db_cache', exist_ok=True)

    results.to_pickle(f'args_to_db_cache/{id}.pkl')
    # results.to_csv(f'args_to_db_cache/{id}.csv')