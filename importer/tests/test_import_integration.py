from io import BytesIO

from django.test import SimpleTestCase

from importer.services.import_service import process_import


class ImportIntegrationTests(SimpleTestCase):

    def run_import(self, csv_content):
        """
        Simulate an uploaded CSV file.
        """

        uploaded_file = BytesIO(
            csv_content.encode("utf-8")
        )

        uploaded_file.name = "employees.csv"

        return process_import(uploaded_file)

    # ---------------------------------------------------------
    # 1. Valid organization
    # ---------------------------------------------------------

    def test_valid_organization(self):

        csv_content = """employee_id,employee_name,email,department,manager_id,manager_email
E001,John,john@example.com,Engineering,,
E002,Alice,alice@example.com,Engineering,E001,
E003,Bob,bob@example.com,Engineering,E001,
E004,Charlie,charlie@example.com,HR,E001,
"""

        result = self.run_import(csv_content)

        self.assertEqual(
            result.error_count,
            0,
        )

        self.assertEqual(
            result.cycle_count,
            0,
        )

        self.assertEqual(
            result.root_count,
            1,
        )

        self.assertEqual(
            result.total_employees,
            4,
        )

        self.assertTrue(
            result.is_valid
        )

    # ---------------------------------------------------------
    # 2. Invalid manager reference
    # ---------------------------------------------------------

    def test_invalid_manager_reference(self):

        csv_content = """employee_id,employee_name,email,department,manager_id,manager_email
E001,Alice,alice@example.com,Engineering,E999,
"""

        result = self.run_import(csv_content)

        self.assertGreater(
            result.error_count,
            0,
        )

        self.assertFalse(
            result.is_valid
        )

        self.assertEqual(
            result.root_count,
            0,
        )

    # ---------------------------------------------------------
    # 3. Employee without manager is a root
    # ---------------------------------------------------------

    def test_employee_without_manager_is_root(self):

        csv_content = """employee_id,employee_name,email,department,manager_id,manager_email
E001,Alice,alice@example.com,Engineering,,
"""

        result = self.run_import(csv_content)

        self.assertEqual(
            result.error_count,
            0,
        )

        self.assertEqual(
            result.root_count,
            1,
        )

        self.assertEqual(
            result.roots,
            ["E001"],
        )

        self.assertTrue(
            result.is_valid
        )

    # ---------------------------------------------------------
    # 4. Two-person reporting cycle
    # ---------------------------------------------------------

    def test_two_person_cycle(self):

        csv_content = """employee_id,employee_name,email,department,manager_id,manager_email
E001,Alice,alice@example.com,Engineering,E002,
E002,Bob,bob@example.com,Engineering,E001,
"""

        result = self.run_import(csv_content)

        self.assertEqual(
            result.error_count,
            0,
        )

        self.assertEqual(
            result.cycle_count,
            1,
        )

        self.assertFalse(
            result.is_valid
        )

    # ---------------------------------------------------------
    # 5. Three-person reporting cycle
    # ---------------------------------------------------------

    def test_three_person_cycle(self):

        csv_content = """employee_id,employee_name,email,department,manager_id,manager_email
E001,Alice,alice@example.com,Engineering,E002,
E002,Bob,bob@example.com,Engineering,E003,
E003,Charlie,charlie@example.com,Engineering,E001,
"""

        result = self.run_import(csv_content)

        self.assertEqual(
            result.error_count,
            0,
        )

        self.assertEqual(
            result.cycle_count,
            1,
        )

        self.assertFalse(
            result.is_valid
        )

    # ---------------------------------------------------------
    # 6. Duplicate employee ID
    # ---------------------------------------------------------

    def test_duplicate_employee_id(self):

        csv_content = """employee_id,employee_name,email,department,manager_id,manager_email
E001,Alice,alice@example.com,Engineering,,
E001,Bob,bob@example.com,Engineering,,
"""

        result = self.run_import(csv_content)

        self.assertGreater(
            result.error_count,
            0,
        )

        self.assertFalse(
            result.is_valid
        )

    # ---------------------------------------------------------
    # 7. Duplicate email
    # ---------------------------------------------------------

    def test_duplicate_email(self):

        csv_content = """employee_id,employee_name,email,department,manager_id,manager_email
E001,Alice,alice@example.com,Engineering,,
E002,Bob,alice@example.com,Engineering,,
"""

        result = self.run_import(csv_content)

        self.assertGreater(
            result.error_count,
            0,
        )

        self.assertFalse(
            result.is_valid
        )

    # ---------------------------------------------------------
    # 8. Manager resolved by email
    # ---------------------------------------------------------

    def test_manager_resolved_by_email(self):

        csv_content = """employee_id,employee_name,email,department,manager_id,manager_email
E001,Alice,alice@example.com,Engineering,,john@example.com
E002,John,john@example.com,Engineering,,
"""

        result = self.run_import(csv_content)

        self.assertEqual(
            result.error_count,
            0,
        )

        self.assertEqual(
            result.manager_count,
            1,
        )

        self.assertTrue(
            result.is_valid
        )

    # ---------------------------------------------------------
    # 9. Matching manager ID and email
    # ---------------------------------------------------------

    def test_matching_manager_id_and_email(self):

        csv_content = """employee_id,employee_name,email,department,manager_id,manager_email
E001,Alice,alice@example.com,Engineering,E002,john@example.com
E002,John,john@example.com,Engineering,,
"""

        result = self.run_import(csv_content)

        self.assertEqual(
            result.error_count,
            0,
        )

        self.assertEqual(
            result.manager_count,
            1,
        )

        self.assertTrue(
            result.is_valid
        )

    # ---------------------------------------------------------
    # 10. Conflicting manager ID and email
    # ---------------------------------------------------------

    def test_conflicting_manager_id_and_email(self):

        csv_content = """employee_id,employee_name,email,department,manager_id,manager_email
E001,Alice,alice@example.com,Engineering,E002,other@example.com
E002,John,john@example.com,Engineering,,
E003,Other,other@example.com,Engineering,,
"""

        result = self.run_import(csv_content)

        self.assertGreater(
            result.error_count,
            0,
        )

        self.assertFalse(
            result.is_valid
        )

    # ---------------------------------------------------------
    # 11. Self manager
    # ---------------------------------------------------------

    def test_employee_cannot_manage_themselves(self):

        csv_content = """employee_id,employee_name,email,department,manager_id,manager_email
E001,Alice,alice@example.com,Engineering,E001,
"""

        result = self.run_import(csv_content)

        self.assertGreater(
            result.error_count,
            0,
        )

        self.assertFalse(
            result.is_valid
        )

    # ---------------------------------------------------------
    # 12. Multiple root employees
    # ---------------------------------------------------------

    def test_multiple_root_employees(self):

        csv_content = """employee_id,employee_name,email,department,manager_id,manager_email
E001,Alice,alice@example.com,Engineering,,
E002,Bob,bob@example.com,HR,,
E003,Charlie,charlie@example.com,Finance,,
"""

        result = self.run_import(csv_content)

        self.assertEqual(
            result.error_count,
            0,
        )

        self.assertEqual(
            result.root_count,
            3,
        )

        self.assertTrue(
            result.is_valid
        )

    # ---------------------------------------------------------
    # 13. Manager with multiple reports
    # ---------------------------------------------------------

    def test_manager_has_multiple_direct_reports(self):

        csv_content = """employee_id,employee_name,email,department,manager_id,manager_email
E001,John,john@example.com,Engineering,,
E002,Alice,alice@example.com,Engineering,E001,
E003,Bob,bob@example.com,Engineering,E001,
E004,Charlie,charlie@example.com,Engineering,E001,
"""

        result = self.run_import(csv_content)

        self.assertEqual(
            result.error_count,
            0,
        )

        self.assertEqual(
            result.manager_count,
            1,
        )

        self.assertEqual(
            len(result.direct_reports["E001"]),
            3,
        )

        self.assertTrue(
            result.is_valid
        )