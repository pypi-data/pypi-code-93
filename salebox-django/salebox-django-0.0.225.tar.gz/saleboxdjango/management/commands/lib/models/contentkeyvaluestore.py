from saleboxdjango.models import ContentKeyValueStore


def sync_contentkeyvaluestore(data):
    # get fieldname
    fieldnames = [f.name for f in ContentKeyValueStore._meta.get_fields()]

    # retrieve / create object
    o = ContentKeyValueStore.objects.filter(id=data['id']).first()
    if o is None:
        o = ContentKeyValueStore()

    # define fields to exclude from update
    exclude = []

    # save data
    for key in data:
        if key in fieldnames and key not in exclude:
            setattr(o, key, data[key])
    o.save()