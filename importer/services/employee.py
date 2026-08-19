from dataclasses import dataclass
from typing import Optional


@dataclass
class Employee:
    """
    Represents a single employee from the HRIS import.
    """

    employee_id: str
    employee_name: str
    email: str
    department: str
    manager_id: Optional[str] = None
    manager_email: Optional[str] = None


@dataclass
class EmployeeRecord:
    """
    Wraps an Employee together with the original CSV row number.

    Keeping the row number attached to the employee makes it possible
    to report validation errors against the original CSV file.
    """

    employee: Employee
    row_number: int