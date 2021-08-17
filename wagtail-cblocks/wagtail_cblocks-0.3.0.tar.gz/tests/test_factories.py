from wagtail.core.blocks import StructValue

from wagtail_cblocks.factories import HeadingBlockFactory, ParagraphBlockFactory


def test_heading_block_factory():
    assert HeadingBlockFactory(text="Another title", level=4) == StructValue(
        None, [('text', "Another title"), ('level', 4)]
    )


def test_paragraph_block_factory():
    assert ParagraphBlockFactory(value="<p>A paragraph.</p>").source == (
        "<p>A paragraph.</p>"
    )
