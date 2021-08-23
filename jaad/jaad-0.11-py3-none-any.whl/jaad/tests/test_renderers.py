from django.test import SimpleTestCase
from jaad.renderers import PrettyJsonRenderer

SIMPLE_DICT = {
    "correspondents": {"from": "user", "to": "world"},
    "messages": ["hello", "everybody"],
}


class RendererTests(SimpleTestCase):
    maxDiff = None

    def test_that_pretty_json_renderer_renders_simple_dict(self):
        self.assertEqual(
            b"{\n"
            b'    "correspondents": {\n'
            b'        "from": "user",\n'
            b'        "to": "world"\n'
            b"    },\n"
            b'    "messages": [\n'
            b'        "hello",\n'
            b'        "everybody"\n'
            b"    ]"
            b"\n}",
            PrettyJsonRenderer().render(SIMPLE_DICT),
        )
