from django.test import SimpleTestCase

from importer.services.cycle_detector import detect_cycles


class CycleDetectorTests(SimpleTestCase):

    def test_no_cycle(self):
        manager_of = {
            "E001": "E003",
            "E002": "E003",
        }

        cycles = detect_cycles(manager_of)

        self.assertEqual(cycles, [])

    def test_two_employee_cycle(self):
        manager_of = {
            "E001": "E002",
            "E002": "E001",
        }

        cycles = detect_cycles(manager_of)

        self.assertEqual(len(cycles), 1)

        cycle = cycles[0]

        self.assertEqual(
            set(cycle[:-1]),
            {"E001", "E002"},
        )

        self.assertEqual(
            cycle[0],
            cycle[-1],
        )

    def test_three_employee_cycle(self):
        manager_of = {
            "E001": "E002",
            "E002": "E003",
            "E003": "E001",
        }

        cycles = detect_cycles(manager_of)

        self.assertEqual(len(cycles), 1)

        cycle = cycles[0]

        self.assertEqual(
            set(cycle[:-1]),
            {
                "E001",
                "E002",
                "E003",
            },
        )

        self.assertEqual(
            cycle[0],
            cycle[-1],
        )

    def test_cycle_inside_larger_hierarchy(self):
        manager_of = {
            "E001": "E002",
            "E002": "E003",
            "E003": "E001",

            "E004": "E002",
            "E005": "E004",
        }

        cycles = detect_cycles(manager_of)

        self.assertEqual(len(cycles), 1)

        cycle = cycles[0]

        self.assertEqual(
            set(cycle[:-1]),
            {
                "E001",
                "E002",
                "E003",
            },
        )

    def test_multiple_independent_cycles(self):
        manager_of = {
            # Cycle 1
            "E001": "E002",
            "E002": "E001",

            # Cycle 2
            "E003": "E004",
            "E004": "E005",
            "E005": "E003",
        }

        cycles = detect_cycles(manager_of)

        self.assertEqual(len(cycles), 2)

        cycle_nodes = [
            set(cycle[:-1])
            for cycle in cycles
        ]

        self.assertIn(
            {"E001", "E002"},
            cycle_nodes,
        )

        self.assertIn(
            {"E003", "E004", "E005"},
            cycle_nodes,
        )

    def test_chain_without_cycle(self):
        manager_of = {
            "E001": "E002",
            "E002": "E003",
            "E003": "E004",
        }

        cycles = detect_cycles(manager_of)

        self.assertEqual(cycles, [])

    def test_self_cycle(self):
        manager_of = {
            "E001": "E001",
        }

        cycles = detect_cycles(manager_of)

        self.assertEqual(len(cycles), 1)

        self.assertEqual(
            cycles[0],
            ["E001", "E001"],
        )