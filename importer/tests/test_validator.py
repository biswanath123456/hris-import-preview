from django.test import SimpleTestCase

from importer.services.employee import Employee, EmployeeRecord
from importer.services.validator import validate_employees


class ValidatorTests(SimpleTestCase):

    def test_valid_employee_has_no_errors(self):
        records = [
            EmployeeRecord(
                employee=Employee(
                    employee_id="E001",
                    employee_name="Alice",
                    email="alice@example.com",
                    department="Engineering",
                ),
                row_number=2,
            )
        ]

        errors = validate_employees(records)

        self.assertEqual(errors, [])

    def test_missing_employee_id_is_detected(self):
        records = [
            EmployeeRecord(
                employee=Employee(
                    employee_id="",
                    employee_name="Alice",
                    email="alice@example.com",
                    department="Engineering",
                ),
                row_number=2,
            )
        ]

        errors = validate_employees(records)

        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0]["row"], 2)
        self.assertEqual(errors[0]["field"], "employee_id")
        self.assertEqual(
            errors[0]["message"],
            "Employee ID is required",
        )

    def test_missing_name_is_detected(self):
        records = [
            EmployeeRecord(
                employee=Employee(
                    employee_id="E001",
                    employee_name="",
                    email="alice@example.com",
                    department="Engineering",
                ),
                row_number=2,
            )
        ]

        errors = validate_employees(records)

        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0]["row"], 2)
        self.assertEqual(errors[0]["field"], "employee_name")
        self.assertEqual(
            errors[0]["message"],
            "Employee name is required",
        )

    def test_missing_email_is_detected(self):
        records = [
            EmployeeRecord(
                employee=Employee(
                    employee_id="E001",
                    employee_name="Alice",
                    email="",
                    department="Engineering",
                ),
                row_number=2,
            )
        ]

        errors = validate_employees(records)

        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0]["row"], 2)
        self.assertEqual(errors[0]["field"], "email")
        self.assertEqual(
            errors[0]["message"],
            "Email is required",
        )

    def test_duplicate_employee_id_is_detected(self):
        records = [
            EmployeeRecord(
                employee=Employee(
                    employee_id="E001",
                    employee_name="Alice",
                    email="alice@example.com",
                    department="Engineering",
                ),
                row_number=2,
            ),
            EmployeeRecord(
                employee=Employee(
                    employee_id="E001",
                    employee_name="Bob",
                    email="bob@example.com",
                    department="Engineering",
                ),
                row_number=3,
            ),
        ]

        errors = validate_employees(records)

        self.assertEqual(len(errors), 2)

        for error in errors:
            self.assertEqual(error["field"], "employee_id")
            self.assertEqual(
                error["message"],
                "Duplicate employee ID",
            )

    def test_duplicate_email_is_detected(self):
        records = [
            EmployeeRecord(
                employee=Employee(
                    employee_id="E001",
                    employee_name="Alice",
                    email="same@example.com",
                    department="Engineering",
                ),
                row_number=2,
            ),
            EmployeeRecord(
                employee=Employee(
                    employee_id="E002",
                    employee_name="Bob",
                    email="same@example.com",
                    department="Engineering",
                ),
                row_number=3,
            ),
        ]

        errors = validate_employees(records)

        self.assertEqual(len(errors), 2)

        for error in errors:
            self.assertEqual(error["field"], "email")
            self.assertEqual(
                error["message"],
                "Duplicate email",
            )

    def test_multiple_validation_errors_are_detected(self):
        records = [
            EmployeeRecord(
                employee=Employee(
                    employee_id="",
                    employee_name="",
                    email="",
                    department="Engineering",
                ),
                row_number=2,
            )
        ]

        errors = validate_employees(records)

        self.assertEqual(len(errors), 3)

        fields = {error["field"] for error in errors}

        self.assertEqual(
            fields,
            {"employee_id", "employee_name", "email"},
        )

    def test_error_contains_original_csv_row_number(self):
        records = [
            EmployeeRecord(
                employee=Employee(
                    employee_id="E001",
                    employee_name="Alice",
                    email="",
                    department="Engineering",
                ),
                row_number=27,
            )
        ]

        errors = validate_employees(records)

        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0]["row"], 27)