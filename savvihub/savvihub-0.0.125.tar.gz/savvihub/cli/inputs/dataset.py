from savvihub.cli.exceptions import ExitException
from savvihub.cli.typer import Context
from savvihub.cli.utils import inquire_list, inquire_text, parse_dataset


def dataset_full_name_callback(ctx: Context, dataset_full_name: str) -> str:
    if dataset_full_name:
        _, dataset_name, _ = parse_dataset(dataset_full_name)
        ctx.store['dataset_name'] = dataset_name
        return dataset_full_name

    datasets = ctx.authenticated_client.dataset_list(ctx.organization.name).results
    if len(datasets) == 0:
        raise ExitException(f'Dataset not found in the default organization `{ctx.organization.name}`.\n'
                            f'Specify the dataset name in {{organization}}/{{dataset}} format to select a dataset of another organization.')

    dataset = inquire_list(
        'Select dataset',
        [(d.name, d) for d in datasets],
    )
    ctx.store['dataset_name'] = dataset.name
    return f'{ctx.organization.name}/{dataset.name}'


def download_dest_path_callback(ctx: Context, dest_path: str) -> str:
    if dest_path:
        return dest_path

    dataset_name = ctx.store.get('dataset_name')
    return inquire_text('Dest path', f'./{dataset_name}' if dataset_name else '.')
