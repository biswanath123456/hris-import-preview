import csv
import io

from .employee import Employee, EmployeeRecord


REQUIRED_COLUMNS = {
    "employee_id",
    "employee_name",
    "email",
    "department",
    "manager_id",
    "manager_email",
}


def parse_csv(file):
    """
    Parse an uploaded CSV file into EmployeeRecord objects.
    """

    try:
        raw_data = file.read()

        if isinstance(raw_data, bytes):
            raw_data = raw_data.decode("utf-8-sig")

        stream = io.StringIO(raw_data)

        reader = csv.DictReader(stream)

    except UnicodeDecodeError:
        return [], [{
            "row": 1,
            "employee_id": None,
            "field": None,
            "message": "CSV file must use UTF-8 encoding",
        }]

    except Exception as exc:
        return [], [{
            "row": 1,
            "employee_id": None,
            "field": None,
            "message": f"Unable to read CSV: {exc}",
        }]

    # ---------------------------------------------------------
    # Empty CSV
    # ---------------------------------------------------------

    if reader.fieldnames is None:
        return [], [{
            "row": 1,
            "employee_id": None,
            "field": None,
            "message": "CSV file has no header row",
        }]

    # ---------------------------------------------------------
    # Normalize column names
    # ---------------------------------------------------------

    reader.fieldnames = [
        field.strip().lower()
        if field
        else field
        for field in reader.fieldnames
    ]

    # ---------------------------------------------------------
    # Check required columns
    # ---------------------------------------------------------

    missing_columns = (
        REQUIRED_COLUMNS - set(reader.fieldnames)
    )

    if missing_columns:
        return [], [{
            "row": 1,
            "employee_id": None,
            "field": None,
            "message": (
                "Missing columns: "
                + ", ".join(sorted(missing_columns))
            ),
        }]

    records = []

    # ---------------------------------------------------------
    # Parse employee rows
    # ---------------------------------------------------------

    for row_number, row in enumerate(reader, start=2):

        employee = Employee(
            employee_id=(row.get("employee_id") or "").strip(),

            employee_name=(row.get("employee_name") or "").strip(),

            email=(row.get("email") or "")
            .strip()
            .lower(),

            department=(row.get("department") or "").strip(),

            manager_id=(row.get("manager_id") or "").strip()
            or None,

            manager_email=(row.get("manager_email") or "")
            .strip()
            .lower()
            or None,
        )

        records.append(
            EmployeeRecord(
                employee=employee,
                row_number=row_number,
            )
        )

    return records, []