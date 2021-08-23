from saleboxdjango.models import Product, ProductVariant


def sync_productvariant(data):
    # get fieldname
    fieldnames = [f.name for f in ProductVariant._meta.get_fields()]

    # retrieve / create object
    o = ProductVariant.objects.filter(id=data['id']).first()
    if o is None:
        o = ProductVariant()

    # populate foreign keys
    if data['product']:
        data['product'] = Product.objects.get(id=data['product'])

    # define fields to exclude from update
    exclude = ['attribute_1', 'attribute_2', 'attribute_3', 'attribute_4', 'attribute_5', 'attribute_6', 'attribute_7', 'attribute_8', 'attribute_9', 'attribute_10']

    # save data
    for key in data:
        if key in fieldnames and key not in exclude:
            setattr(o, key, data[key])
    o.save()

    # save many to many
    for i in range(1, 11):
        key = f'attribute_{i}'
        getattr(o, key).set(data[key])
