from collections import namedtuple

from django.core.exceptions import ImproperlyConfigured
from django.utils.functional import cached_property
from django.utils.safestring import mark_safe
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from wagtail.core import blocks as core_blocks
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.images.blocks import ImageChooserBlock

# MIXINS AND BASE CLASSES
# ------------------------------------------------------------------------------

Style = namedtuple('Style', ['name', 'label', 'css_class'])


class CSSClassMixin:
    """
    Add the CSS class defined for a block to its rendering context.
    """

    def get_css_classes(self, value):
        if hasattr(self.meta, 'css_class'):
            if isinstance(self.meta.css_class, str):
                return [self.meta.css_class]
            if not isinstance(self.meta.css_class, list):
                return list(self.meta.css_class)
            return self.meta.css_class
        return []

    def get_context(self, value, **kwargs):
        context = super().get_context(value, **kwargs)
        context['css_class'] = ' '.join(self.get_css_classes(value))
        return context


class StyleChoiceBlock(core_blocks.ChoiceBlock):
    class Meta:
        label = _("Style")

    def __init__(self, styles, default=None):
        self.styles = styles

        super().__init__(
            choices=[(s.name, s.label) for s in styles],
            default=default,
        )

    def to_python(self, value):
        for style in self.styles:
            if style.name == value:
                return style

    def get_default(self):
        if isinstance(self.meta.default, Style):
            return self.meta.default
        return self.to_python(self.meta.default)


class StylizedStructBlock(CSSClassMixin, core_blocks.StructBlock):
    """
    A group of sub-blocks which defines an element with different styles.
    """

    styles = ()

    class Meta:
        default_style = None

    def __init__(self, *args, styles=None, **kwargs):
        super().__init__(*args, **kwargs)

        if styles is None:
            styles = self.styles

        if styles:
            style = StyleChoiceBlock(styles, default=self.meta.default_style)
            style.set_name('style')

            self.child_blocks['style'] = style

    def get_css_classes(self, value):
        css_classes = super().get_css_classes(value)
        style = value.get('style', None)
        if style and style.css_class:
            css_classes.append(style.css_class)
        return css_classes


# TYPOGRAPHY
# ------------------------------------------------------------------------------

HEADING_LEVELS = [
    (i, _("Level %(level)d heading") % {'level': i}) for i in range(2, 6)
]


class HeadingValue(core_blocks.StructValue):
    @cached_property
    def tag(self):
        """Return the HTML tag to use for the level."""
        return 'h{}'.format(self.get('level'))

    @cached_property
    def anchor(self):
        """Generate a slug from the title to be used as an anchor."""
        return slugify(self.get('text'))


class HeadingBlock(core_blocks.StructBlock):
    """
    A section heading with a choosable level.
    """

    text = core_blocks.CharBlock(label=_("Title"), classname='title')
    level = core_blocks.ChoiceBlock(
        choices=HEADING_LEVELS,
        default=2,
        label=_("Level"),
    )

    class Meta:
        icon = 'title'
        label = _("Title")
        template = 'wagtail_cblocks/heading_block.html'
        value_class = HeadingValue


class ParagraphBlock(core_blocks.RichTextBlock):
    """
    A paragraph with simple or customized features.
    """

    features = ('bold', 'italic', 'ol', 'ul', 'hr', 'link', 'document-link')

    def __init__(self, features=None, **kwargs):
        if features is None:
            features = self.features
        return super().__init__(features=features, **kwargs)

    class Meta:
        icon = 'pilcrow'
        label = _("Paragraph")
        template = 'wagtail_cblocks/paragraph_block.html'


# LINK AND BUTTONS
# ------------------------------------------------------------------------------


class LinkTargetBlock(core_blocks.StreamBlock):
    """
    The target of a link, used by `LinkBlock`.
    """

    page = core_blocks.PageChooserBlock(
        label=_("Page"), icon='doc-empty-inverse'
    )
    document = DocumentChooserBlock(label=_("Document"), icon='doc-full')
    image = ImageChooserBlock(label=_("Image"))
    url = core_blocks.URLBlock(label=_("External link"))
    anchor = core_blocks.CharBlock(
        label=_("Anchor link"),
        help_text=mark_safe(
            _(
                "An anchor in the current page, for example: "
                "<code>#target-id</code>."
            )
        ),
    )

    class Meta:
        icon = 'link'
        max_num = 1
        form_classname = 'link-target-block'


class LinkValue(core_blocks.StructValue):
    @cached_property
    def href(self):
        """Return the URL of the chosen target or `None` if it is undefined."""
        try:
            child_value = self['target'][0].value
        except (IndexError, KeyError):
            return None
        if hasattr(child_value, 'file') and hasattr(child_value.file, 'url'):
            href = child_value.file.url
        elif hasattr(child_value, 'url'):
            href = child_value.url
        else:
            href = child_value
        return href


class LinkBlock(core_blocks.StructBlock):
    """
    A link with a target chosen from a range of types - i.e. a page, an URL.
    """

    class Meta:
        icon = 'link'
        label = _("Link")
        value_class = LinkValue
        form_classname = 'link-block'

    def __init__(self, *args, required=True, **kwargs):
        super().__init__(*args, required=required, **kwargs)

        target = LinkTargetBlock(required=required)
        target.set_name('target')

        self.child_blocks['target'] = target

    @property
    def required(self):
        return self.meta.required


class ButtonBlock(StylizedStructBlock):
    """
    A button which acts like a link.
    """

    text = core_blocks.CharBlock(label=_("Text"))
    link = LinkBlock()

    class Meta:
        icon = 'link'
        label = _("Button")
        template = 'wagtail_cblocks/button_block.html'


# IMAGES
# ------------------------------------------------------------------------------


class ImageBlock(core_blocks.StructBlock):
    """
    An image with optional caption and link.
    """

    image = ImageChooserBlock(label=_("Image"))
    caption = core_blocks.CharBlock(required=False, label=_("Caption"))
    link = LinkBlock(required=False)

    class Meta:
        icon = 'image'
        label = _("Image")
        template = 'wagtail_cblocks/image_block.html'


# LAYOUT
# ------------------------------------------------------------------------------

HORIZONTAL_ALIGNMENTS = [
    ('start', _("Left")),
    ('center', _("Center")),
    ('end', _("Right")),
]
HORIZONTAL_ALIGNMENT_DEFAULT = None


class ColumnsBlock(core_blocks.StructBlock):
    """
    A list of columns which can be horizontally aligned.
    """

    horizontal_align = core_blocks.ChoiceBlock(
        choices=HORIZONTAL_ALIGNMENTS,
        default=HORIZONTAL_ALIGNMENT_DEFAULT,
        required=False,
        label=_("Horizontal alignment"),
    )

    class Meta:
        icon = 'table'
        label = _("Columns")
        template = 'wagtail_cblocks/columns_block.html'

    def __init__(self, column_block=None, **kwargs):
        super().__init__(**kwargs)

        if column_block is None:
            if not hasattr(self.meta, 'column_block'):
                raise ImproperlyConfigured(
                    "ColumnsBlock was not passed a 'column_block' object"
                )
            column_block = self.meta.column_block

        columns = core_blocks.ListBlock(
            column_block,
            form_classname='columns-block-list',
            label=_("Columns"),
        )
        columns.set_name('columns')

        self.child_blocks['columns'] = columns
        self.child_blocks.move_to_end('columns', last=False)
