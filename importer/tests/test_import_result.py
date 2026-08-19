from django.test import SimpleTestCase

from importer.services.import_result import ImportResult


class ImportResultTests(SimpleTestCase):

    def test_empty_result_is_valid(self):
        result = ImportResult()

        self.assertTrue(
            result.is_valid
        )

    def test_result_statistics(self):
        result = ImportResult(
            records=[
                "employee1",
                "employee2",
                "employee3",
            ],
            errors=[
                {
                    "message": "Invalid email"
                }
            ],
            cycles=[
                ["E001", "E002", "E001"]
            ],
            roots=[
                "E003"
            ],
            direct_reports={
                "E003": ["E001", "E002"]
            },
        )

        self.assertEqual(
            result.total_employees,
            3,
        )

        self.assertEqual(
            result.error_count,
            1,
        )

        self.assertEqual(
            result.cycle_count,
            1,
        )

        self.assertEqual(
            result.root_count,
            1,
        )

        self.assertEqual(
            result.manager_count,
            1,
        )

    def test_result_with_errors_is_invalid(self):
        result = ImportResult(
            errors=[
                {
                    "message": "Email is required"
                }
            ]
        )

        self.assertFalse(
            result.is_valid
        )

    def test_result_with_cycles_is_invalid(self):
        result = ImportResult(
            cycles=[
                ["E001", "E002", "E001"]
            ]
        )

        self.assertFalse(
            result.is_valid
        )

    def test_result_without_errors_or_cycles_is_valid(self):
        result = ImportResult(
            records=[
                "employee1",
                "employee2",
            ]
        )

        self.assertTrue(
            result.is_valid
        )