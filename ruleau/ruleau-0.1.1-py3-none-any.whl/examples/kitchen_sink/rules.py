from ruleau import All, ApiAdapter, OverrideLevel, execute, rule


@rule(rule_id="rul_child", name="Has children")
def has_children(_, payload):
    """
    Checks whether the custom has any children.

    >>> has_children(None, {"data": {"number_of_children": 0}})
    False
    >>> has_children(None, {"data": {"number_of_children": 1}})
    True
    """
    return payload["data"]["number_of_children"] > 0


@rule(rule_id="rul_cap", name="Have sufficient capital", depends_on=[has_children])
def has_sufficient_capital(context, payload):
    """
    Checks that the client has sufficient capital, considering the number of
    children they have.

    >>> from ruleau import mock_context
    >>> context = mock_context({
    ...     "has_children": True
    ... })
    >>> has_sufficient_capital(context, {"data": {"capital": 10_000}})
    False

    >>> from ruleau import mock_context
    >>> context = mock_context({
    ...     "has_children": False
    ... })
    >>> has_sufficient_capital(context, {"data": {"capital": 10_000}})
    True
    """
    if context.dependent_results.has_children:
        return payload["data"]["capital"] > 12_000
    else:
        return payload["data"]["capital"] > 8_000


@rule(rule_id="rul_01", name="kyc_threshold", override_level=OverrideLevel.NO_OVERRIDE)
def kyc_risk_greater_than_threshold(_, payload):
    """
    Know Your Customer (KYC) score must be greater than the threshold,
    in this case greater than `LOW`

    :Override Guidance: kyc_threshold to mark this failure into review

    >>> kyc_risk_greater_than_threshold(None, {"data": {"kyc": "HIGH"}})
    False
    >>> kyc_risk_greater_than_threshold(None, {"data": {"kyc": "LOW"}})
    True
    """
    return payload["data"]["kyc"] == "LOW"


@rule(rule_id="rul_02", name="fico_score")
def fico_score_greater_than_threshold(_, payload):
    """
    FICO score must be greater than 630

    :Owner: Penny Farthing
    :Override Guidance: Feel free to override in almost any circumstance

    >>> fico_score_greater_than_threshold(None, {"data": {"fico_score": 400}})
    False
    >>> fico_score_greater_than_threshold(None, {"data": {"fico_score": 630}})
    False
    >>> fico_score_greater_than_threshold(None, {"data": {"fico_score": 650}})
    True
    """
    return payload["data"]["fico_score"] > 630


@rule(rule_id="rul_ccjs_required", name="CCJS check required")
def ccjs_check_required(_, payload):
    return payload["data"]["ccjs_required"]


@rule(rule_id="rul_03", name="no_ccjs", run_if=ccjs_check_required)
def has_no_ccjs(_, payload):
    """
    Make sure customer has no county court judgements
    >>> has_no_ccjs(None, {"data": {"ccjs": []}})
    True
    >>> has_no_ccjs(None, {"data": {"ccjs": ["Example CCJ"]}})
    False
    >>> has_no_ccjs(None, {"data": {"ccjs": [{"example": "CCJ Object"}]}})
    False
    """
    return len(payload["data"]["ccjs"]) == 0


@rule("rul-101A", "Causes skipped")
def causes_skip(_, __):
    return False


@rule("rul_101", "Skipped Rule", run_if=causes_skip)
def skipped_rule(_, __):
    return False


@rule("rul-102A", "Causes not skipped")
def causes_no_skip(_, __):
    return True


@rule("rul_102", "Not Skipped Rule", run_if=causes_no_skip)
def not_skipped_rule(_, __):
    return False


@rule("rul200-c", "Skipped tree bottom")
def skipped_tree_bottom(_, __):
    return False


@rule(
    "rul200-a",
    "Skipped tree 1  skipped",
    depends_on=[skipped_tree_bottom],
    run_if=causes_skip,
)
def skipped_tree_1_a(_, __):
    return False


@rule(
    "rul200-b",
    "Skipped tree 1 not skipped",
    depends_on=[skipped_tree_bottom],
    run_if=causes_no_skip,
)
def skipped_tree_1_b(_, __):
    return False


@rule("rul200", "Skipped tree 1 Top", depends_on=[skipped_tree_1_a, skipped_tree_1_b])
def skipped_tree_1(_, __):
    return False


conditionals = All(
    "ID",
    "name",
    skipped_rule,
    causes_no_skip,
    skipped_tree_1,
)

will_lend = All(
    "rul_04",
    "Top level",
    kyc_risk_greater_than_threshold,
    fico_score_greater_than_threshold,
    has_no_ccjs,
    has_sufficient_capital,
    conditionals,
)

if __name__ == "__main__":
    result = execute(
        will_lend,
        {
            "data": {
                "fico_score": 150,
                "ccjs": [],
                "kyc": "low",
                "number_of_children": 1,
                "capital": 10_000,
                "ccjs_required": True,
            }
        },
        api_adapter=ApiAdapter(base_url="http://127.0.0.1:8000"),
        case_id="132",
    )
    print("Result", result.result)
