from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def update_url_query(context, param_name=None, param_value=None, **kwargs):
    """
    this allows us to update the url query parameters from the current request

    example:

        {% update_url_query variable_key variable value page=1 %}
    """
    # request.GET is a QueryDict, which is immutable unless we make a copy
    query_dict = context['request'].GET.copy()
    # set variable parameter name and value
    if param_name:
        query_dict[param_name] = param_value
        if param_value == 'remove':
            # remove the parameter altogether
            query_dict.pop(param_name, None)
    # for a normal dict we would use update(kwargs), but QueryDict.update()
    # appends values, instead of replacing them, so we need to set each key
    # explicitly
    for key, value in kwargs.items():
        query_dict[key] = value
    # urlencode converts the dict to a query string
    return query_dict.urlencode()


@register.filter
def get(list_or_dict, index_or_key):
    """
    get item from list/dict by variable index/key:

        {{ some_list|get:some_variable }}

    """
    try:
        return list_or_dict[index_or_key]
    except (TypeError, IndexError, KeyError):
        return ''
