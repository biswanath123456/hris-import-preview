from django.test import SimpleTestCase

from importer.services.record_filter import get_valid_records


class RecordFilterTests(SimpleTestCase):

    def test_invalid_rows_are_removed(self):

        records = [
            type(
                "Record",
                (),
                {"row_number": 2},
            )(),
            type(
                "Record",
                (),
                {"row_number": 3},
            )(),
            type(
                "Record",
                (),
                {"row_number": 4},
            )(),
        ]

        errors = [
            {
                "row": 3,
                "message": "Duplicate employee ID",
            }
        ]

        valid_records = get_valid_records(
            records,
            errors,
        )

        self.assertEqual(
            [record.row_number for record in valid_records],
            [2, 4],
        )

    def test_records_without_errors_are_preserved(self):

        records = [
            type(
                "Record",
                (),
                {"row_number": 2},
            )(),
            type(
                "Record",
                (),
                {"row_number": 3},
            )(),
        ]

        errors = []

        valid_records = get_valid_records(
            records,
            errors,
        )

        self.assertEqual(
            len(valid_records),
            2,
        )

    def test_multiple_invalid_rows_are_removed(self):

        records = [
            type(
                "Record",
                (),
                {"row_number": 2},
            )(),
            type(
                "Record",
                (),
                {"row_number": 3},
            )(),
            type(
                "Record",
                (),
                {"row_number": 4},
            )(),
        ]

        errors = [
            {
                "row": 2,
                "message": "Duplicate employee ID",
            },
            {
                "row": 4,
                "message": "Duplicate email",
            },
        ]

        valid_records = get_valid_records(
            records,
            errors,
        )

        self.assertEqual(
            [record.row_number for record in valid_records],
            [3],
        )
