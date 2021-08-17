import pytest

from sym.sdk.flow import Flow, Run


class TestFlow:
    def test_flow_abstract(self):
        with pytest.raises(TypeError) as exc_info:
            flow = Flow()
        assert str(exc_info.value).startswith("Can't instantiate abstract class Flow")

    def test_run_abstract(self):
        with pytest.raises(TypeError) as exc_info:
            run = Run()
        assert str(exc_info.value).startswith("Can't instantiate abstract class Run")
