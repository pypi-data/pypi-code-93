from torch.utils.data import get_worker_info


def generic_worker_init_fn(worker_id):
    # pylint: disable=unused-argument
    worker_info = get_worker_info()

    candidate_datasets = [worker_info.dataset]

    # Make it work with Subset and other Datasets that themselves can contain Datasets.
    while len(candidate_datasets) > 0:
        current_dataset = candidate_datasets.pop()

        if hasattr(current_dataset, 'on_worker_init'):
            current_dataset.on_worker_init(worker_id)

        if hasattr(current_dataset, 'dataset'):
            candidate_datasets.append(current_dataset.dataset)

        if hasattr(current_dataset, 'datasets'):
            candidate_datasets += list(current_dataset.datasets)
