from django.core.exceptions import ImproperlyConfigured

import pytest
from bs4 import BeautifulSoup
from pytest_django.asserts import assertHTMLEqual
from wagtail_factories import DocumentFactory, ImageFactory, PageFactory

from wagtail_cblocks import blocks
from wagtail_cblocks.blocks import CSSClassMixin, Style, StylizedStructBlock

from .models import BaseBlock, ColumnsBlock, RowColumnsBlock


class BlockTest:
    def render(self, data, block=None):
        if block is None:
            block = self.block
        return block.render(block.to_python(data))

    def render_html(self, *args, **kwargs):
        return BeautifulSoup(self.render(*args, **kwargs), 'html.parser')


class TestCSSClassMixin:
    class Block(CSSClassMixin, blocks.ParagraphBlock):
        pass

    def test_in_meta(self):
        class Block(self.Block):
            class Meta:
                css_class = 'lead'

        block = Block()
        context = block.get_context(block.to_python('<p>Paragraph</p>'))
        assert context['css_class'] == 'lead'

    @pytest.mark.parametrize('value', ('lead', {'lead'}, ['lead']))
    def test_at_init(self, value):
        block = self.Block(css_class=value)
        context = block.get_context(block.to_python('<p>Paragraph</p>'))
        assert context['css_class'] == 'lead'

    def test_empty(self):
        block = self.Block()
        context = block.get_context(block.to_python('<p>Paragraph</p>'))
        assert context['css_class'] == ''


class TestStylizedStructBlock:
    STYLES = [
        Style('foo', "Foo", 'is-foo'),
        Style('bar', "Bar", 'is-bar'),
    ]

    def test_empty_styles(self):
        block = StylizedStructBlock()
        assert 'style' not in block.child_blocks
        context = block.get_context(block.to_python({}))
        assert context['css_class'] == ''

    def test_styles_from_property(self):
        class Block(StylizedStructBlock):
            styles = self.STYLES

        value = Block().to_python({'style': 'foo'})
        assert value.get('style').name == 'foo'

    def test_style(self):
        block = StylizedStructBlock(styles=self.STYLES)
        value = block.to_python({'style': 'foo'})
        assert isinstance(value.get('style'), Style)
        assert value.get('style').name == 'foo'
        context = block.get_context(value)
        assert context['css_class'] == 'is-foo'

    def test_style_with_css_class(self):
        block = StylizedStructBlock(styles=self.STYLES, css_class='block')
        context = block.get_context(block.to_python({'style': 'foo'}))
        assert context['css_class'] == 'block is-foo'

    def test_default_style(self):
        block = StylizedStructBlock(styles=self.STYLES, default_style='bar')
        value = block.to_python({})
        assert isinstance(value.get('style'), Style)
        assert value.get('style').name == 'bar'
        context = block.get_context(value)
        assert context['css_class'] == 'is-bar'

    def test_default_style_object(self):
        block = StylizedStructBlock(
            styles=self.STYLES, default_style=self.STYLES[1]
        )
        value = block.to_python({})
        assert isinstance(value.get('style'), Style)
        assert value.get('style').name == 'bar'

    def test_unknown_style(self):
        block = StylizedStructBlock(styles=self.STYLES, default_style='bar')
        value = block.to_python({'style': 'baz'})
        assert value.get('style') is None
        context = block.get_context(value)
        assert context['css_class'] == ''


class TestHeadingBlock(BlockTest):
    block = blocks.HeadingBlock()

    def test_render(self):
        assertHTMLEqual(
            self.render({'text': "Un titre !", 'level': 2}),
            '<h2 id="un-titre">Un titre !</h2>',
        )


class TestParagraphBlock(BlockTest):
    block = blocks.ParagraphBlock()

    def test_features(self):
        assert self.block.features == blocks.ParagraphBlock.features

        block = blocks.ParagraphBlock(features=['bold', 'italic'])
        assert block.features == ['bold', 'italic']

    def test_render(self):
        data = '<p><i>Un</i> paragraphe !</p>'
        assertHTMLEqual(self.render(data), data)


@pytest.mark.django_db
class TestLinkBlock:
    block = blocks.LinkBlock()

    def get_value(self, target):
        return self.block.to_python({'target': target})

    def test_local_blocks(self):
        block = blocks.LinkBlock([('text', blocks.ParagraphBlock())])
        assert list(block.child_blocks.keys()) == ['text', 'target']

    def test_required(self):
        block = blocks.LinkBlock(required=False)
        assert block.required is False
        assert block.child_blocks['target'].required is False

        assert self.block.required is True
        assert self.block.child_blocks['target'].required is True

    def test_href_value_page(self, root_page):
        page = PageFactory(parent=root_page, title="About", slug='about')
        value = self.get_value([{'type': 'page', 'value': page.id}])
        assert value.href == '/about/'

    def test_href_value_page_invalid(self):
        value = self.get_value([{'type': 'page', 'value': 1000}])
        assert value.href is None

    def test_href_value_document(self):
        document = DocumentFactory()
        value = self.get_value([{'type': 'document', 'value': document.id}])
        assert value.href == document.file.url

    def test_href_value_document_invalid(self):
        value = self.get_value([{'type': 'document', 'value': 1000}])
        assert value.href is None

    def test_href_value_image(self):
        image = ImageFactory()
        value = self.get_value([{'type': 'image', 'value': image.id}])
        assert value.href == image.file.url

    def test_href_value_image_invalid(self):
        value = self.get_value([{'type': 'image', 'value': 1000}])
        assert value.href is None

    def test_href_value_external_url(self):
        url = 'http://example.org/truc/'
        value = self.get_value([{'type': 'url', 'value': url}])
        assert value.href == url

    def test_href_value_anchor(self):
        anchor = '#truc'
        value = self.get_value([{'type': 'anchor', 'value': anchor}])
        assert value.href == anchor

    def test_href_value_empty(self):
        value = self.get_value([])
        assert value.href is None

    def test_href_value_no_target(self):
        block = blocks.LinkBlock([('text', blocks.ParagraphBlock())])
        value = block.to_python({'text': "some text"})
        assert value.href is None


class TestButtonBlock(BlockTest):
    block = blocks.ButtonBlock()

    def test_render_link(self):
        url = 'http://example.org/truc/'
        assertHTMLEqual(
            self.render(
                {
                    'text': "Lien",
                    'link': {'target': [{'type': 'url', 'value': url}]},
                }
            ),
            '<a class="btn mb-3" href="{}">Lien</a>'.format(url),
        )


@pytest.mark.django_db
class TestImageBlock(BlockTest):
    block = blocks.ImageBlock()

    def test_render(self):
        html = self.render_html(
            {
                'image': ImageFactory().id,
                'caption': '',
                'link': {'target': []},
            }
        )
        assert len(html.select('img.figure-img.img-fluid.mb-0')) == 1
        assert not html.select('figcaption')
        assert not html.select('a')

    def test_render_with_caption(self):
        html = self.render_html(
            {
                'image': ImageFactory().id,
                'caption': "Une légende en dessous.",
                'link': {'target': []},
            }
        )
        assert html.select_one('figcaption').text == "Une légende en dessous."
        assert not html.select('a')

    def test_render_with_link(self):
        url = 'http://example.org/truc/'
        html = self.render_html(
            {
                'image': ImageFactory().id,
                'caption': '',
                'link': {'target': [{'type': 'url', 'value': url}]},
            }
        )
        assert html.select_one('a').attrs['href'] == url
        assert not html.select('figcaption')


class TestColumnsBlock(BlockTest):
    block = blocks.ColumnsBlock(BaseBlock())

    def test_columns_block_order(self):
        assert list(self.block.child_blocks.keys())[0] == 'columns'

    def test_render(self):
        url = 'http://example.org/truc/'
        data = {
            'columns': [
                [
                    {
                        'type': 'button_block',
                        'value': {
                            'text': "Lien",
                            'link': {
                                'target': [{'type': 'url', 'value': url}],
                            },
                            'style': 'primary',
                        },
                    },
                    {
                        'type': 'paragraph_block',
                        'value': "<p>A first paragraph.</p>",
                    },
                ],
                [
                    {
                        'type': 'paragraph_block',
                        'value': "<p>Another paragraph.</p>",
                    },
                ],
            ],
            'horizontal_align': 'center',
        }
        assertHTMLEqual(
            self.render(data),
            (
                '<div class="row text-center">'
                '<div class="col-sm">{}{}</div>'
                '<div class="col-sm">{}</div>'
                '</div>'
            ).format(
                '<a class="btn btn-primary mb-3" href="{}">Lien</a>'.format(
                    url
                ),
                '<p>A first paragraph.</p>',
                '<p>Another paragraph.</p>',
            ),
        )

    def test_sublcass_render(self):
        data = {
            'columns': [
                [
                    {
                        'type': 'paragraph_block',
                        'value': "<p>A first paragraph.</p>",
                    },
                ],
            ],
            'layout': 'auto',
        }
        assertHTMLEqual(
            self.render(data, RowColumnsBlock()),
            (
                '<div class="row row-cols-auto">'
                '<div class="col"><p>A first paragraph.</p></div>'
                '</div>'
            ),
        )

    def test_required_column_block(self):
        with pytest.raises(ImproperlyConfigured):

            class DummyColumnsBlock(ColumnsBlock):
                pass

            DummyColumnsBlock()
