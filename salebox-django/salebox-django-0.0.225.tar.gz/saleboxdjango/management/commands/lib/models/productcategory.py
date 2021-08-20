from saleboxdjango.models import ProductCategory


def sync_productcategory(data):
    # get fieldname
    fieldnames = [f.name for f in ProductCategory._meta.get_fields()]

    # retrieve / create object
    o = ProductCategory.objects.filter(id=data['id']).first()
    if o is None:
        o = ProductCategory()

    # populate foreign keys
    if data['parent']:
        data['parent'] = ProductCategory.objects.get(id=data['parent'])

    # define fields to exclude from update
    exclude = []

    # save data
    for key in data:
        if key in fieldnames and key not in exclude:
            setattr(o, key, data[key])
    o.save()