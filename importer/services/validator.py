from collections import Counter

from .employee import EmployeeRecord


def validate_employees(records: list[EmployeeRecord]) -> list[dict]:
    """
    Validate basic employee data.

    This function currently checks:

    - Missing employee ID
    - Missing name
    - Missing email
    - Duplicate employee ID
    - Duplicate email

    Manager-related validation is handled separately because it requires
    building employee indexes and resolving manager relationships.

    Args:
        records: Parsed employee records including their CSV row numbers.

    Returns:
        A list of structured validation errors.
    """

    errors = []

    # ---------------------------------------------------------
    # Build frequency maps
    # ---------------------------------------------------------
    #
    # Counter lets us identify duplicates in O(N) time instead
    # of comparing every employee with every other employee.
    #

    employee_id_counts = Counter(
        record.employee.employee_id
        for record in records
        if record.employee.employee_id
    )

    email_counts = Counter(
        record.employee.email
        for record in records
        if record.employee.email
    )

    # ---------------------------------------------------------
    # Validate each employee
    # ---------------------------------------------------------

    for record in records:
        employee = record.employee

        # -----------------------------------------------------
        # Required employee ID
        # -----------------------------------------------------

        if not employee.employee_id:
            errors.append({
                "row": record.row_number,
                "employee_id": None,
                "field": "employee_id",
                "message": "Employee ID is required",
            })

        # -----------------------------------------------------
        # Required name
        # -----------------------------------------------------

        if not employee.employee_name:
            errors.append({
                "row": record.row_number,
                "employee_id": employee.employee_id or None,
                "field": "employee_name",
                "message": "Employee name is required",
            })

        # -----------------------------------------------------
        # Required email
        # -----------------------------------------------------

        if not employee.email:
            errors.append({
                "row": record.row_number,
                "employee_id": employee.employee_id or None,
                "field": "email",
                "message": "Email is required",
            })

        # -----------------------------------------------------
        # Duplicate employee ID
        # -----------------------------------------------------

        if (
            employee.employee_id
            and employee_id_counts[employee.employee_id] > 1
        ):
            errors.append({
                "row": record.row_number,
                "employee_id": employee.employee_id,
                "field": "employee_id",
                "message": "Duplicate employee ID",
            })

        # -----------------------------------------------------
        # Duplicate email
        # -----------------------------------------------------

        if (
            employee.email
            and email_counts[employee.email] > 1
        ):
            errors.append({
                "row": record.row_number,
                "employee_id": employee.employee_id or None,
                "field": "email",
                "message": "Duplicate email",
            })

    return errors