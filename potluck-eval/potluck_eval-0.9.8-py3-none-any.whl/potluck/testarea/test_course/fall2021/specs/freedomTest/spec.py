"""
freedomTest rubric specification

Peter Mawhorter 2021-7-23
"""

from potluck import specifications as spec

# Tests for "whatever" function
spec.TestCase("whatever", (True, True))
spec.TestCase("whatever", (True, False))
spec.TestCase("whatever", (False, True))
spec.TestCase("whatever", (False, False))

spec.TestCase("whatever", (True, True), group_name="b")
spec.TestCase("whatever", (True, False), group_name="b")
spec.TestCase("whatever", (False, True), group_name="b")

# Two derived goals
gr = spec.group("whatever")
gr2 = gr.also()

# First check that it doesn't crash
gr.goal("core").succeed_unless_crashed()

# Next check that it creates the proper distinctions among outputs
spec.group("whatever", group_name="b")\
    .refine(spec.DistinctionReport)\
    .goal("core")

# Extra check for all 4 possibilities
gr2.refine(spec.DistinctionReport).goal("extra")

# Require docstrings
spec.RequireDocstrings()

# Check that tests are established and pass
spec.RequireExpectations({"whatever": 3})
spec.ObserveExpectationResults()

# Construct our rubric
rubric = spec.rubric()


# Specifications tests using the meta module:
from potluck import meta # noqa E402

# This submission should get everything right
meta.example("perfect")

meta.example("imperfect")

meta.expect("partial", "process", "core", "does not crash")
meta.expect("failed", "product", "core", "distinctions")
meta.expect("failed", "product", "extra", "distinctions")
meta.expect("partial", "testing", "core", "defines")
meta.expect("partial", "testing", "extra", "were met")


# This submission runs crashing code in a test T_T
meta.example("runscode")

meta.expect("failed", "style", "core", "documented")
meta.expect("failed", "process", "core", "does not crash")
meta.expect("failed", "product", "core", "distinctions")
meta.expect("failed", "product", "extra", "distinctions")
meta.expect("failed", "testing", "core", "defines")
meta.expect("failed", "testing", "extra", "were met")
