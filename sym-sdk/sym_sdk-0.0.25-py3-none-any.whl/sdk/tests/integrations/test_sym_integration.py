from sym.sdk.util.template.sym import debug, get_flows, handles_to_users


class TestSymIntegrationInterface:
    def test_missing_body(self):
        v1 = get_flows(user="andrew@symops.io")
        v2 = handles_to_users(
            integration_type="pager_duty",
            integration_srn=None,
            handles=["andrew@symops.io"],
        )

        v3 = debug("message")

        assert v1 is None
        assert v2 is None
        assert v3 is None
