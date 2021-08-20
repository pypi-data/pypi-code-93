def _get_ranges(model, data):
    features = model.features
    ranges = {}
    for i in model:
        if i.name in features:
            name = i.name
            if "cat" in i.spec:
                ranges[name] = data[name].unique()
            else:
                ranges[name] = (data[name].min(), data[name].max())
    return ranges
