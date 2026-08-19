from dataclasses import dataclass

from .employee import EmployeeRecord


@dataclass
class HierarchyResult:
    employees_by_id: dict
    employees_by_email: dict
    manager_of: dict
    direct_reports: dict
    roots: list
    errors: list


def build_hierarchy(
    records: list[EmployeeRecord],
) -> HierarchyResult:

    employees_by_id = {}
    employees_by_email = {}

    errors = []

    # ---------------------------------------------------------
    # Build employee indexes
    # ---------------------------------------------------------

    for record in records:

        employee = record.employee

        if employee.employee_id:
            employees_by_id[employee.employee_id] = record

        if employee.email:
            employees_by_email[employee.email] = record

    # ---------------------------------------------------------
    # Resolve manager relationships
    # ---------------------------------------------------------

    manager_of = {}

    # Keep track of employees whose manager reference
    # was invalid.
    invalid_manager_references = set()

    for record in records:

        employee = record.employee

        manager_record = None

        has_manager_id = bool(
            employee.manager_id
        )

        has_manager_email = bool(
            employee.manager_email
        )

        # -----------------------------------------------------
        # Resolve manager_id
        # -----------------------------------------------------

        if has_manager_id:

            manager_record = employees_by_id.get(
                employee.manager_id
            )

            if manager_record is None:

                errors.append({
                    "row": record.row_number,
                    "employee_id": employee.employee_id,
                    "field": "manager_id",
                    "message": (
                        f"Manager '{employee.manager_id}' "
                        "does not exist"
                    ),
                })

                invalid_manager_references.add(
                    employee.employee_id
                )

        # -----------------------------------------------------
        # Resolve manager_email
        # -----------------------------------------------------

        if has_manager_email:

            email_manager_record = (
                employees_by_email.get(
                    employee.manager_email
                )
            )

            if email_manager_record is None:

                errors.append({
                    "row": record.row_number,
                    "employee_id": employee.employee_id,
                    "field": "manager_email",
                    "message": (
                        f"Manager email "
                        f"'{employee.manager_email}' "
                        "does not exist"
                    ),
                })

                invalid_manager_references.add(
                    employee.employee_id
                )

            # -------------------------------------------------
            # Both references exist
            # -------------------------------------------------

            elif manager_record is not None:

                id_manager_id = (
                    manager_record.employee.employee_id
                )

                email_manager_id = (
                    email_manager_record.employee.employee_id
                )

                if id_manager_id != email_manager_id:

                    errors.append({
                        "row": record.row_number,
                        "employee_id": employee.employee_id,
                        "field": "manager",
                        "message": (
                            "manager_id and manager_email "
                            "refer to different employees"
                        ),
                    })

                    invalid_manager_references.add(
                        employee.employee_id
                    )

                    manager_record = None

            # -------------------------------------------------
            # Only manager_email was supplied
            # -------------------------------------------------

            else:

                manager_record = email_manager_record

        # -----------------------------------------------------
        # Self-manager
        # -----------------------------------------------------

        if manager_record is not None:

            manager_id = (
                manager_record.employee.employee_id
            )

            if manager_id == employee.employee_id:

                errors.append({
                    "row": record.row_number,
                    "employee_id": employee.employee_id,
                    "field": "manager",
                    "message": (
                        "Employee cannot be "
                        "their own manager"
                    ),
                })

                invalid_manager_references.add(
                    employee.employee_id
                )

                continue

            manager_of[
                employee.employee_id
            ] = manager_id

    # ---------------------------------------------------------
    # Build manager → direct reports
    # ---------------------------------------------------------

    direct_reports = {}

    for employee_id, manager_id in manager_of.items():

        direct_reports.setdefault(
            manager_id,
            []
        ).append(employee_id)

    # ---------------------------------------------------------
    # Find legitimate roots
    # ---------------------------------------------------------

    roots = []

    for record in records:

        employee = record.employee

        employee_id = employee.employee_id

        # -----------------------------------------------------
        # No manager information supplied.
        #
        # This is a legitimate root.
        # -----------------------------------------------------

        if (
            not employee.manager_id
            and not employee.manager_email
        ):

            roots.append(employee_id)

    return HierarchyResult(
        employees_by_id=employees_by_id,
        employees_by_email=employees_by_email,
        manager_of=manager_of,
        direct_reports=direct_reports,
        roots=roots,
        errors=errors,
    )