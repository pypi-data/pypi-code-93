from saleboxdjango.models import ContentPage, ContentPageItem


def sync_contentpageitem(data):
    # get fieldname
    fieldnames = [f.name for f in ContentPageItem._meta.get_fields()]

    # retrieve / create object
    o = ContentPageItem.objects.filter(id=data['id']).first()
    if o is None:
        o = ContentPageItem()

    # populate foreign keys
    if data['page']:
        data['page'] = ContentPage.objects.get(id=data['page'])

    # define fields to exclude from update
    exclude = []

    # save data
    for key in data:
        if key in fieldnames and key not in exclude:
            setattr(o, key, data[key])
    o.save()