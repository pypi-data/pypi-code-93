from huscy.projects.models import DataAcquisitionMethod


def add_data_acquisition_method(session, type, location, order=None):
    if order is None:
        order = DataAcquisitionMethod.objects.filter(session=session).count() + 1

    return DataAcquisitionMethod.objects.create(
        session=session,
        type=type,
        location=location,
        order=order
    )


def get_data_acquisition_methods(project=None):
    queryset = DataAcquisitionMethod.objects
    if project:
        queryset = queryset.filter(session__experiment__project=project)
    return queryset.order_by('pk')
