from ruleau import execute

from examples.kitchen_sink.rules import will_lend

if __name__ == "__main__":
    payload = {"data": {"fico_score": 150, "ccjs": [], "kyc": "low", "number_of_children": 1, "capital": 10_000, "ccjs_required": True}}
    result = execute(will_lend, payload, case_id="abc")
