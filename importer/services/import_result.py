from dataclasses import dataclass, field


@dataclass
class ImportResult:
    records: list = field(default_factory=list)
    errors: list = field(default_factory=list)
    cycles: list = field(default_factory=list)

    roots: list = field(default_factory=list)
    direct_reports: dict = field(default_factory=dict)

    employees_by_id: dict = field(default_factory=dict)
    employees_by_email: dict = field(default_factory=dict)

    @property
    def total_employees(self) -> int:
        return len(self.records)

    @property
    def error_count(self) -> int:
        return len(self.errors)

    @property
    def cycle_count(self) -> int:
        return len(self.cycles)

    @property
    def root_count(self) -> int:
        return len(self.roots)

    @property
    def manager_count(self) -> int:
        return len(self.direct_reports)

    @property
    def is_valid(self) -> bool:
        return (
            self.error_count == 0
            and self.cycle_count == 0
        )