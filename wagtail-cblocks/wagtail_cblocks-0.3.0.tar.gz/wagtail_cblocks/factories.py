import factory
import wagtail_factories

from . import blocks


class HeadingBlockFactory(wagtail_factories.StructBlockFactory):
    text = "A title"
    level = 3

    class Meta:
        model = blocks.HeadingBlock


class ParagraphBlockFactory(factory.Factory):
    # FIXME: In waiting of https://github.com/wagtail/wagtail-factories/pull/25

    value = "<p>Some <b>formatted</b> text.</p>"

    class Meta:
        model = blocks.ParagraphBlock

    @classmethod
    def _build(cls, model_class, value):
        return model_class().to_python(value)

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        return cls._build(model_class, *args, **kwargs)
