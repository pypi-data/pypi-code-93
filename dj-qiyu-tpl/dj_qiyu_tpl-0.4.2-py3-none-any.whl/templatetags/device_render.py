from django import template
from django.http import HttpRequest
from django_qiyu_utils.div_node import custom_div_node_helper

register = template.Library()


def on_mobile_device(ctx: template.Context) -> bool:
    """
    判断当前的请求设备是否为移动设备
    """
    request = ctx["request"]
    assert isinstance(request, HttpRequest)
    user_agent = request.META.get("HTTP_USER_AGENT", "")
    return "mobile" in user_agent.lower()


# noinspection PyUnusedLocal
@register.tag
def mobile_render(parser, token):
    """
    如果是在移动设备上 则渲染内部模版

    usage:

        {% mobile_render %}
        what ever you content is,
        it will only render on mobile device
        {% end_mobile_render %}
    """
    return custom_div_node_helper(
        name="mobile_render", parser=parser, fn=on_mobile_device
    )


# noinspection PyUnusedLocal
@register.tag
def pc_render(parser, token):
    """
    如果在 电脑上 则 渲染内部模版

    usage:

        {% pc_render %}
        what ever you content is,
        it will only render on pc/pad device
        {% end_pc_render %}
    """

    def on_pc_device(ctx: template.Context) -> bool:
        return not on_mobile_device(ctx)

    return custom_div_node_helper(name="pc_render", parser=parser, fn=on_pc_device)
