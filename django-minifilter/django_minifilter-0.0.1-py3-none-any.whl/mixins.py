from typing import List, Tuple
from minifilter.filters import search_filter, parameter_filter


class FilterMixin(object):
    search_fields: List[str] = []
    filter_parameters: List[Tuple[str]] = []

    def get_context_data(self, *, object_list=None, **kwargs):
        # get queryset (based on MultipleObjectMixin.get_context_data
        # and BaseListView.get)
        queryset = object_list if object_list is not None else self.get_queryset()  # noqa
        # filter by search term (which is obtained from a url query parameter)
        queryset, search_form = search_filter(
            queryset=queryset, request=self.request, # noqa
            search_fields=self.search_fields)
        # filter by other url query parameters
        queryset, parameter_choices = parameter_filter(
            queryset=queryset, request=self.request,  # noqa
            filter_parameters=self.filter_parameters)
        # get context after filtering, so that (optional) pagination will be
        # applied to the filtered queryset
        context = super().get_context_data(object_list=queryset, **kwargs)  # noqa
        # amend context
        context['parameter_choices'] = parameter_choices
        context['search_form'] = search_form
        return context
