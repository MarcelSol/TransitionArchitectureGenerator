from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class ValidationSeverity(Enum):
    ERROR = "Error"
    WARNING = "Warning"


@dataclass(slots=True)
class ValidationIssue:

    severity: ValidationSeverity

    rule: str

    object_id: str

    object_name: str

    page: str

    message: str


@dataclass(slots=True)
class ValidationReport:

    issues: list[ValidationIssue] = field(default_factory=list)

    def add(
        self,
        severity: ValidationSeverity,
        rule: str,
        object_id: str,
        object_name: str,
        page: str,
        message: str,
    ) -> None:

        self.issues.append(
            ValidationIssue(
                severity=severity,
                rule=rule,
                object_id=object_id,
                object_name=object_name,
                page=page,
                message=message,
            )
        )

    @property
    def error_count(self) -> int:

        return sum(
            1
            for issue in self.issues
            if issue.severity == ValidationSeverity.ERROR
        )

    @property
    def warning_count(self) -> int:

        return sum(
            1
            for issue in self.issues
            if issue.severity == ValidationSeverity.WARNING
        )
