from .csv_parser import parse_csv
from .validator import validate_employees
from .hierarchy import build_hierarchy
from .cycle_detector import detect_cycles
from .import_result import ImportResult
from .record_filter import get_valid_records


def process_import(file) -> ImportResult:
    """
    Run the complete HRIS import preview pipeline.

    No data is persisted to the database.
    """

    # ---------------------------------------------------------
    # 1. Parse CSV
    # ---------------------------------------------------------

    records, parser_errors = parse_csv(file)

    if parser_errors:

        return ImportResult(
            records=[],
            errors=parser_errors,
        )

    # ---------------------------------------------------------
    # 2. Validate records
    # ---------------------------------------------------------

    validation_errors = validate_employees(
        records
    )

    # ---------------------------------------------------------
    # 3. Only valid records enter the hierarchy
    # ---------------------------------------------------------

    valid_records = get_valid_records(
        records,
        validation_errors,
    )

    # ---------------------------------------------------------
    # 4. Build hierarchy
    # ---------------------------------------------------------

    hierarchy = build_hierarchy(
        valid_records
    )

    # ---------------------------------------------------------
    # 5. Detect cycles
    # ---------------------------------------------------------

    cycles = detect_cycles(
        hierarchy.manager_of
    )

    # ---------------------------------------------------------
    # 6. Combine errors
    # ---------------------------------------------------------

    errors = (
        validation_errors
        + hierarchy.errors
    )

    # ---------------------------------------------------------
    # 7. Return final result
    # ---------------------------------------------------------

    return ImportResult(
        records=records,

        errors=errors,

        cycles=cycles,

        roots=hierarchy.roots,

        direct_reports=hierarchy.direct_reports,

        employees_by_id=hierarchy.employees_by_id,

        employees_by_email=hierarchy.employees_by_email,
    )