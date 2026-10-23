from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from sqlglot import exp

if TYPE_CHECKING:
    from .filters.utils.table_classes import Table


@dataclass
class PipeLineContext:
    # Data from the interface
    sql: str
    dialect: str
    target_normal_form: str

    # Results produced by pipeline filters
    sql_ast: list[exp.Expression] | None = None
    schema: list[Table] | None = None
    violations: list[Any] = field(default_factory=list)
    report: Any | None = None
