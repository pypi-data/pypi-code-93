from minifilter.forms import SearchForm


def parameter_filter(queryset, request, filter_parameters):
    """
    filter queryset based on url query parameters from request

    filter_parameters = [(parameter-name, lookup), ...]

    for example: [('organization', 'organization__abbreviation'), ...]

    note the order of the filter_parameters matters, because the queryset
    is refined each time
    """
    parameter_choices = dict()  # assume insertion ordered dict (python 3.7+)
    for parameter_name, lookup in filter_parameters:
        # note this evaluates the queryset
        parameter_choices[parameter_name] = [
            str(value) for value in queryset.order_by(lookup).values_list(
                lookup, flat=True).distinct()]
        # filter the queryset based on parameter value
        parameter_value = request.GET.get(parameter_name)
        if parameter_value in parameter_choices[parameter_name]:
            queryset = queryset.filter(**{lookup: parameter_value})
    return queryset, parameter_choices


def search_filter(queryset, request, search_fields):
    """ filter queryset based on search text from request """
    search_queryset = queryset.none()
    search_form = SearchForm(data=request.GET)
    if search_form.is_valid():
        search_text = search_form.cleaned_data.get('search')
        for field_name in search_fields:
            search_queryset = search_queryset | queryset.filter(
                **{f'{field_name}__icontains': search_text})
    return search_queryset, search_form
