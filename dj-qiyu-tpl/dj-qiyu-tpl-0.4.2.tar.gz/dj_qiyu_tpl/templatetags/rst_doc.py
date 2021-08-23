from django import template
from django.http import HttpRequest

from ..rst.rst import RstHelper

register = template.Library()

__all__ = ["rst_doc"]


@register.simple_tag(takes_context=True)
def rst_doc(context: dict, code: str) -> str:
    """
    rST 文档渲染

    使用方式:

    .. code-blocks: django

        {% rst_doc code %}
    """
    request: HttpRequest = context["request"]

    # 一个页面里面，只有第一次的时候 需要加载 scripts 文件
    # 防止多次加载出现错误
    rst_doc_need_script = "__rst_doc_need_script"

    need = getattr(request, rst_doc_need_script, True)
    if need:
        setattr(request, rst_doc_need_script, False)

    return RstHelper.publish_app_doc(code, need_script=need)
