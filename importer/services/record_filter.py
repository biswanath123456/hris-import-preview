def get_valid_records(records, errors):
    """
    Return records that don't have row-level validation errors.

    Errors are expected to contain a 'row' field.
    """

    invalid_rows = {
        error["row"]
        for error in errors
        if error.get("row") is not None
    }

    return [
        record
        for record in records
        if record.row_number not in invalid_rows
    ]
