from django.test import SimpleTestCase

from importer.services.employee import Employee, EmployeeRecord
from importer.services.hierarchy import build_hierarchy


class HierarchyTests(SimpleTestCase):

    def test_manager_relationship_is_created(self):
        records = [
            EmployeeRecord(
                employee=Employee(
                    employee_id="E001",
                    employee_name="Alice",
                    email="alice@example.com",
                    department="Engineering",
                    manager_id="E002",
                ),
                row_number=2,
            ),
            EmployeeRecord(
                employee=Employee(
                    employee_id="E002",
                    employee_name="John",
                    email="john@example.com",
                    department="Engineering",
                ),
                row_number=3,
            ),
        ]

        result = build_hierarchy(records)

        self.assertEqual(
            result.manager_of,
            {
                "E001": "E002",
            },
        )

    def test_direct_reports_are_created(self):
        records = [
            EmployeeRecord(
                employee=Employee(
                    employee_id="E001",
                    employee_name="Alice",
                    email="alice@example.com",
                    department="Engineering",
                    manager_id="E003",
                ),
                row_number=2,
            ),
            EmployeeRecord(
                employee=Employee(
                    employee_id="E002",
                    employee_name="Bob",
                    email="bob@example.com",
                    department="Engineering",
                    manager_id="E003",
                ),
                row_number=3,
            ),
            EmployeeRecord(
                employee=Employee(
                    employee_id="E003",
                    employee_name="John",
                    email="john@example.com",
                    department="Engineering",
                ),
                row_number=4,
            ),
        ]

        result = build_hierarchy(records)

        self.assertEqual(
            result.direct_reports,
            {
                "E003": ["E001", "E002"],
            },
        )

    def test_root_employee_is_detected(self):
        records = [
            EmployeeRecord(
                employee=Employee(
                    employee_id="E001",
                    employee_name="John",
                    email="john@example.com",
                    department="Engineering",
                ),
                row_number=2,
            )
        ]

        result = build_hierarchy(records)

        self.assertEqual(
            result.roots,
            ["E001"],
        )

    def test_unknown_manager_id_creates_error(self):
        records = [
            EmployeeRecord(
                employee=Employee(
                    employee_id="E001",
                    employee_name="Alice",
                    email="alice@example.com",
                    department="Engineering",
                    manager_id="E999",
                ),
                row_number=7,
            )
        ]

        result = build_hierarchy(records)

        self.assertEqual(len(result.errors), 1)

        self.assertEqual(
            result.errors[0]["row"],
            7,
        )

        self.assertEqual(
            result.errors[0]["field"],
            "manager_id",
        )

    def test_unknown_manager_email_creates_error(self):
        records = [
            EmployeeRecord(
                employee=Employee(
                    employee_id="E001",
                    employee_name="Alice",
                    email="alice@example.com",
                    department="Engineering",
                    manager_email="unknown@example.com",
                ),
                row_number=8,
            )
        ]

        result = build_hierarchy(records)

        self.assertEqual(len(result.errors), 1)

        self.assertEqual(
            result.errors[0]["field"],
            "manager_email",
        )

    def test_manager_id_and_email_must_match(self):
        records = [
            EmployeeRecord(
                employee=Employee(
                    employee_id="E001",
                    employee_name="Alice",
                    email="alice@example.com",
                    department="Engineering",
                    manager_id="E002",
                    manager_email="david@example.com",
                ),
                row_number=9,
            ),
            EmployeeRecord(
                employee=Employee(
                    employee_id="E002",
                    employee_name="John",
                    email="john@example.com",
                    department="Engineering",
                ),
                row_number=10,
            ),
            EmployeeRecord(
                employee=Employee(
                    employee_id="E003",
                    employee_name="David",
                    email="david@example.com",
                    department="Engineering",
                ),
                row_number=11,
            ),
        ]

        result = build_hierarchy(records)

        self.assertEqual(len(result.errors), 1)

        self.assertEqual(
            result.errors[0]["field"],
            "manager",
        )

    def test_self_manager_is_rejected(self):
        records = [
            EmployeeRecord(
                employee=Employee(
                    employee_id="E001",
                    employee_name="Alice",
                    email="alice@example.com",
                    department="Engineering",
                    manager_id="E001",
                ),
                row_number=12,
            )
        ]

        result = build_hierarchy(records)

        self.assertEqual(len(result.errors), 1)

        self.assertEqual(
            result.errors[0]["message"],
            "Employee cannot be their own manager",
        )

        self.assertNotIn(
            "E001",
            result.manager_of,
        )


    def test_employee_with_invalid_manager_is_not_root(self):
        records = [
            EmployeeRecord(
                employee=Employee(
                    employee_id="E001",
                    employee_name="Alice",
                    email="alice@example.com",
                    department="Engineering",
                    manager_id="E999",
                ),
                row_number=2,
            ),
            EmployeeRecord(
                employee=Employee(
                    employee_id="E002",
                    employee_name="John",
                    email="john@example.com",
                    department="Engineering",
                ),
                row_number=3,
            ),
        ]

        result = build_hierarchy(records)

        self.assertEqual(
            result.roots,
            ["E002"],
        )

    def test_manager_can_be_resolved_by_email(self):
        records = [
            EmployeeRecord(
                employee=Employee(
                    employee_id="E001",
                    employee_name="Alice",
                    email="alice@example.com",
                    department="Engineering",
                    manager_email="john@example.com",
                ),
                row_number=2,
            ),
            EmployeeRecord(
                employee=Employee(
                    employee_id="E002",
                    employee_name="John",
                    email="john@example.com",
                    department="Engineering",
                ),
                row_number=3,
            ),
        ]

        result = build_hierarchy(records)

        self.assertEqual(
            result.manager_of,
            {
                "E001": "E002",
            },
        )

    def test_matching_manager_id_and_email_are_valid(self):
        records = [
            EmployeeRecord(
                employee=Employee(
                    employee_id="E001",
                    employee_name="Alice",
                    email="alice@example.com",
                    department="Engineering",
                    manager_id="E002",
                    manager_email="john@example.com",
                ),
                row_number=2,
            ),
            EmployeeRecord(
                employee=Employee(
                    employee_id="E002",
                    employee_name="John",
                    email="john@example.com",
                    department="Engineering",
                ),
                row_number=3,
            ),
        ]

        result = build_hierarchy(records)

        self.assertEqual(
            result.errors,
            [],
        )

        self.assertEqual(
            result.manager_of,
            {
                "E001": "E002",
            },
        )
