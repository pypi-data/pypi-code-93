import pytest

from sym.sdk.templates import ApprovalTemplate, Template


class TestTemplates:
    def test_approval(self):
        template = ApprovalTemplate("sym:template:approval:1.0.0")
        assert isinstance(template, Template)

    def test_abstract_base(self):
        with pytest.raises(TypeError):
            Template()
