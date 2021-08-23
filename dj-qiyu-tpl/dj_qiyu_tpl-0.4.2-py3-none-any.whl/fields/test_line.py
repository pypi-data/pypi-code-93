from django.forms import CharField, Form

from .custom import CustomFormField
from ..forms import CustomForm


class DemoCharForm(Form):
    char = CharField(
        max_length=100, min_length=10, label="测试", help_text="这是一个测试的字段"
    )  # noqa


def test_demo_char_field():
    form = DemoCharForm(data={"char": "hello world"})
    html = """<p><label for="id_char">测试:</label> <input type="text" name="char" value="hello world" maxlength="100" minlength="10" required id="id_char"> <span class="helptext">这是一个测试的字段</span></p>"""  # noqa
    assert form.as_p() == html
    table_html = """<tr><th><label for="id_char">测试:</label></th><td><input type="text" name="char" value="hello world" maxlength="100" minlength="10" required id="id_char"><br><span class="helptext">这是一个测试的字段</span></td></tr>"""  # noqa
    assert table_html == form.as_table()


class BulmaLineForm(CustomForm):
    char = CustomFormField(
        max_length=100, min_length=10, label="测试", help_text="这是一个测试的字段"
    )


def test_bulma_line_field():
    form = BulmaLineForm(data={"char": "hello world"})
    p = form.as_p()
    print(p)
