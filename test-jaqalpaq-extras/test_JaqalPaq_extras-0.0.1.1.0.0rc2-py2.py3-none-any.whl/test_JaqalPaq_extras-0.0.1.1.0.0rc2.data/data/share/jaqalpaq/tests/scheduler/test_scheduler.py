import unittest, pytest
import jaqalpaq
from jaqalpaq.core.circuitbuilder import build
from jaqalpaq.scheduler import schedule_circuit

qscout = pytest.importorskip("qscout")
from qscout.v1.std import NATIVE_GATES as native_gates


class SchedulerTester(unittest.TestCase):
    scheduled_circuit_0 = (
        "circuit",
        ("register", "q", 2),
        (
            "sequential_block",
            ("gate", "prepare_all"),
            (
                "parallel_block",
                ("gate", "Px", ("array_item", "q", 0)),
                ("gate", "Py", ("array_item", "q", 1)),
            ),
            ("gate", "measure_all"),
        ),
    )
    unscheduled_circuit_0a = (
        "circuit",
        ("register", "q", 2),
        (
            "unscheduled_block",
            ("gate", "prepare_all"),
            ("gate", "Px", ("array_item", "q", 0)),
            ("gate", "Py", ("array_item", "q", 1)),
            ("gate", "measure_all"),
        ),
    )
    unscheduled_circuit_0b = (
        "circuit",
        ("register", "q", 2),
        (
            "sequential_block",
            ("gate", "prepare_all"),
            (
                "unscheduled_block",
                ("gate", "Px", ("array_item", "q", 0)),
                ("gate", "Py", ("array_item", "q", 1)),
            ),
            ("gate", "measure_all"),
        ),
    )
    unscheduled_circuit_0c = (
        "circuit",
        ("register", "q", 2),
        (
            "unscheduled_block",
            ("gate", "prepare_all"),
            (
                "parallel_block",
                ("gate", "Px", ("array_item", "q", 0)),
                ("gate", "Py", ("array_item", "q", 1)),
            ),
            ("gate", "measure_all"),
        ),
    )
    scheduled_circuit_1 = (
        "circuit",
        ("register", "q", 4),
        (
            "sequential_block",
            ("gate", "prepare_all"),
            (
                "parallel_block",
                ("gate", "Px", ("array_item", "q", 0)),
                ("gate", "Py", ("array_item", "q", 1)),
            ),
            (
                "parallel_block",
                ("gate", "Px", ("array_item", "q", 2)),
                ("gate", "Py", ("array_item", "q", 3)),
            ),
            ("gate", "measure_all"),
        ),
    )
    unscheduled_circuit_1 = (
        "circuit",
        ("register", "q", 4),
        (
            "sequential_block",
            (
                "unscheduled_block",
                ("gate", "prepare_all"),
                ("gate", "Px", ("array_item", "q", 0)),
                ("gate", "Py", ("array_item", "q", 1)),
            ),
            (
                "unscheduled_block",
                ("gate", "Px", ("array_item", "q", 2)),
                ("gate", "Py", ("array_item", "q", 3)),
                ("gate", "measure_all"),
            ),
        ),
    )
    scheduled_circuit_2 = (
        "circuit",
        ("register", "q", 3),
        (
            "sequential_block",
            ("gate", "prepare_all"),
            (
                "parallel_block",
                ("gate", "Px", ("array_item", "q", 0)),
                ("gate", "Py", ("array_item", "q", 1)),
            ),
            ("gate", "Px", ("array_item", "q", 0)),
            ("gate", "Py", ("array_item", "q", 2)),
            ("gate", "Pz", ("array_item", "q", 2)),
            ("gate", "measure_all"),
        ),
    )
    unscheduled_circuit_2 = (
        "circuit",
        ("register", "q", 3),
        (
            "unscheduled_block",
            ("gate", "prepare_all"),
            ("gate", "Px", ("array_item", "q", 0)),
            (
                "sequential_block",
                ("gate", "Px", ("array_item", "q", 0)),
                ("gate", "Py", ("array_item", "q", 2)),
            ),
            ("gate", "Py", ("array_item", "q", 1)),
            ("gate", "Pz", ("array_item", "q", 2)),
            ("gate", "measure_all"),
        ),
    )
    scheduled_circuit_3 = (
        "circuit",
        ("register", "q", 3),
        (
            "sequential_block",
            ("gate", "prepare_all"),
            (
                "parallel_block",
                ("gate", "Px", ("array_item", "q", 0)),
                ("gate", "Py", ("array_item", "q", 1)),
            ),
            (
                "loop",
                5,
                (
                    "sequential_block",
                    ("gate", "Px", ("array_item", "q", 0)),
                    ("gate", "Py", ("array_item", "q", 2)),
                ),
            ),
            ("gate", "Pz", ("array_item", "q", 2)),
            ("gate", "measure_all"),
        ),
    )
    unscheduled_circuit_3 = (
        "circuit",
        ("register", "q", 3),
        (
            "unscheduled_block",
            ("gate", "prepare_all"),
            ("gate", "Px", ("array_item", "q", 0)),
            (
                "loop",
                5,
                (
                    "sequential_block",
                    ("gate", "Px", ("array_item", "q", 0)),
                    ("gate", "Py", ("array_item", "q", 2)),
                ),
            ),
            ("gate", "Py", ("array_item", "q", 1)),
            ("gate", "Pz", ("array_item", "q", 2)),
            ("gate", "measure_all"),
        ),
    )
    scheduled_circuit_4 = (
        "circuit",
        ("register", "q", 5),
        (
            "macro",
            "Hadamard",
            "a",
            ("sequential_block", ("gate", "Pz", "a"), ("gate", "Sy", "a")),
        ),
        (
            "sequential_block",
            ("gate", "prepare_all"),
            ("gate", "Sxx", ("array_item", "q", 2), ("array_item", "q", 3)),
            ("gate", "Sxx", ("array_item", "q", 0), ("array_item", "q", 1)),
            (
                "parallel_block",
                ("gate", "Px", ("array_item", "q", 0)),
                ("gate", "Px", ("array_item", "q", 2)),
                ("gate", "Py", ("array_item", "q", 1)),
                ("gate", "Py", ("array_item", "q", 3)),
            ),
            ("gate", "Hadamard", ("array_item", "q", 4)),
            ("gate", "measure_all"),
        ),
    )
    unscheduled_circuit_4 = (
        "circuit",
        ("register", "q", 5),
        (
            "macro",
            "Hadamard",
            "a",
            ("sequential_block", ("gate", "Pz", "a"), ("gate", "Sy", "a")),
        ),
        (
            "unscheduled_block",
            ("gate", "prepare_all"),
            ("gate", "Sxx", ("array_item", "q", 2), ("array_item", "q", 3)),
            ("gate", "Sxx", ("array_item", "q", 0), ("array_item", "q", 1)),
            ("gate", "Px", ("array_item", "q", 0)),
            ("gate", "Px", ("array_item", "q", 2)),
            (
                "parallel_block",
                ("gate", "Py", ("array_item", "q", 1)),
                ("gate", "Py", ("array_item", "q", 3)),
            ),
            ("gate", "Hadamard", ("array_item", "q", 4)),
            ("gate", "measure_all"),
        ),
    )

    def run_test(self, unscheduled, scheduled):
        self.assertEqual(
            build(scheduled, native_gates),
            schedule_circuit(build(unscheduled, native_gates)),
        )

    def test_identity_reschedule(self):
        self.run_test(self.scheduled_circuit_0, self.scheduled_circuit_0)
        self.run_test(self.scheduled_circuit_1, self.scheduled_circuit_1)
        self.run_test(self.scheduled_circuit_2, self.scheduled_circuit_2)
        self.run_test(self.scheduled_circuit_3, self.scheduled_circuit_3)
        self.run_test(self.scheduled_circuit_4, self.scheduled_circuit_4)

    def test_reschedule_body(self):
        self.run_test(self.unscheduled_circuit_0a, self.scheduled_circuit_0)

    def test_reschedule_deep(self):
        self.run_test(self.unscheduled_circuit_0b, self.scheduled_circuit_0)

    def test_reschedule_parallel_inside(self):
        self.run_test(self.unscheduled_circuit_0c, self.scheduled_circuit_0)

    def test_reschedule_sequential_inside(self):
        self.run_test(self.unscheduled_circuit_2, self.scheduled_circuit_2)

    def test_reschedule_loop_inside(self):
        self.run_test(self.unscheduled_circuit_3, self.scheduled_circuit_3)

    def test_reschedule_cannot_parallelize(self):
        self.run_test(self.unscheduled_circuit_4, self.scheduled_circuit_4)

    def test_reschedule_barrier(self):
        self.run_test(self.unscheduled_circuit_1, self.scheduled_circuit_1)
