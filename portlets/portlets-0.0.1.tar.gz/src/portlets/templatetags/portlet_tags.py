from django import template
from django.template.defaultfilters import stringfilter
from django.utils import translation
from wagtail.core.models import Site

from ..models import PortletAssignment

register = template.Library()


@register.inclusion_tag('portlets/slot.html', takes_context=True)
def slot(context, slot_name, path_override=None, extra=None, **kwargs):
    if slot_name == '':
        raise Exception('Slot name must be non-empty string')
    slot_class = ''
    if ':' in slot_name:
        slot_name, slot_class = slot_name.split(':')
    request = context.get('request')
    lang = translation.get_language()
    if extra and str(extra) != '':
        slot_name = '-'.join((slot_name, str(extra)))
    if path_override:
        path = path_override
    else:
        path = request.path

    current_site = Site.find_for_request(request)
    assignments = PortletAssignment.get_for_path(
        path=path, slot=slot_name, language=lang, site=current_site,
    )

    portlets = []
    blocklist = []
    for a in assignments:
        if a.prohibit:
            blocklist.append(a.portlet.pk)
            continue
        portlet = a.portlet.get_object()
        portlet.update(request)
        portlet.assignment = a
        portlet.prohibited = portlet.pk in blocklist
        portlets.append(portlet)

    ctx = {
        'portlets': portlets,
        'slot_name': slot_name,
        'request': request,
        'slot_class': slot_class,
    }
    # also include any kwargs in context
    ctx.update(**kwargs)

    return ctx


@register.filter()
def get_all_but_first(qs):
    return qs[1:]


@register.filter()
def get_specific_objects(qs, args):
    if args is None:
        return False
    arg_list = [arg.strip() for arg in args.split(',')]
    x = int(arg_list[0])
    y = int(arg_list[1])
    return qs[x:y]


@register.filter()
def get_specific_termine(qs, args):
    if qs:
        qs = qs.extra(select={'datediff': 'ABS(DATEDIFF(meeting_date, NOW()))'}).order_by(
            'datediff',
        )
        if args is None:
            return False
        arg_list = [arg.strip() for arg in args.split(',')]
        x = int(arg_list[0])
        y = int(arg_list[1])
        return qs[x:y]


@register.filter
@stringfilter
def split_number_character(number_ch):
    num_lst = []
    all_el_lst = number_ch.split(' ')
    for el in all_el_lst:
        if el.isdigit():
            num_lst.append(int(el))
