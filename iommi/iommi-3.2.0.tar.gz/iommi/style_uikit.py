from django.utils.safestring import mark_safe

from iommi import Fragment
from iommi.asset import Asset
from iommi.style import (
    Style,
)
from iommi.style_base import base
from iommi.style_font_awesome_4 import font_awesome_4

navbar_burger_click_js = Fragment(
    mark_safe(
        """\
<script>
    $(document).ready(function() {
          // Check for click events on the navbar burger icon
          $(".navbar-burger").click(function() {

              // Toggle the "is-active" class on both the "navbar-burger" and the "navbar-menu"
              $(".navbar-burger").toggleClass("is-active");
              $(".navbar-menu").toggleClass("is-active");

          });
    });
</script>
"""
    )
)

uikit_base = Style(
    base,
    root__assets=dict(
        css=Asset.css(
            attrs=dict(
                href='https://cdn.jsdelivr.net/npm/halfmoon@1.1.1/css/halfmoon.min.css',
                # integrity='sha256-fPEGZjub3hSSE9IDD9Jouuees5qtbNLWOxL27ConJ08=',
                crossorigin='anonymous',
            )
        ),
        navbar_burger_click_js=navbar_burger_click_js,
    ),
    Header__attrs__class={
        'title': True,
    },
    Container=dict(
        tag='div',
        attrs__class={
            'main': True,
            'container': True,
        },
    ),
    Field=dict(
        shortcuts=dict(
            boolean=dict(

            ),
            textarea=dict(
                input__attrs__class={'uk-input': True},
            ),
            radio=dict(
                input__attrs__class={'uk-radio': True},
            ),
        ),
        # template='iommi/form/uikit/field.html',
        # input__attrs__class={
        #     'is-danger': lambda field, **_: bool(field.errors),
        # },
        # errors__attrs__class={
        #     'is-danger': True,
        #     'help': True,
        # },
        # help__attrs__class=dict(
        #     help=True,
        # ),
    ),
    Actions=dict(
        tag="div",
        attrs__class=dict(links=False, buttons=True),
    ),
    Action=dict(
        shortcuts=dict(
            # In uikit the most neutral button styling is button, which
            # gets you a button that's just an outline.
            button__attrs__class={
                'button': True,
            },
            delete__attrs__class={
                'is-danger': True,
            },
            primary__attrs__class={
                'is-primary': True,
            },
        ),
    ),
    Table={
        'attrs__class__table': True,
        'attrs__class__is-fullwidth': True,
        'attrs__class__is-hoverable': True,
    },
    Column=dict(
        shortcuts=dict(
            select=dict(
                header__attrs__title='Select all',
            ),
            number=dict(
                cell__attrs__class={
                    'has-text-right': True,
                },
                header__attrs__class={
                    'has-text-right': True,
                },
            ),
        ),
    ),
    Query__form=dict(
        iommi_style='uikit_query_form',
    ),
    Query__form_container=dict(
        tag='span',
        attrs__class={
            'is-horizontal': True,
            'field': True,
        },
    ),
    Menu=dict(
        attrs__class__navbar=True,
        tag='nav',
    ),
    MenuItem__a__attrs__class={'navbar-item': True},
    MenuItem__active_class='is-active',
    DebugMenu=dict(
        tag='aside',
        attrs__class={
            'navbar': False,
            'menu': True,
        },
    ),
    Paginator=dict(
        # template='iommi/table/uikit/paginator.html',
    ),
    Errors__attrs__class={
        'help': True,
        'is-danger': True,
    },
)
uikit = Style(
    uikit_base,
    font_awesome_4,
)


uikit_query_form = Style(
    uikit,
    internal=True,
    Field=dict(
        attrs__class={
            'mr-4': True,
        },
        label__attrs__class={
            'mt-2': True,
            'mr-1': True,
        },
    ),
)
