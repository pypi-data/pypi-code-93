import pkgutil


labels_path = {
    'ms_coco': 'mscoco_labels.json',
    'imagenet':'ImageNetLabels.txt',
    'tfhub_biggan_categories':'tfhub_biggan_categories.json',
}

def _get_labels_path(name):
    if name in labels_path:
        return labels_path.get(name)
    else:
        raise ValueError(f"No label file foudn with name '{name}'")

def get_labels(name):
    return pkgutil.get_data(__name__, _get_labels_path(name))
