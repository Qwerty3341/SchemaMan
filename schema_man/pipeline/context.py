from dataclasses import dataclass, field
from typing import Any, List, Optional


@dataclass
class PipeLineContext:
    # data from interface
    sql: str
    dialect: str
    target_normal_form: str

    # Resoults
    sql_checked: Optional[Any] = None
    schema: Optional[Any] = None
    violations: List[Any] = field(default_factory=list)
    report: Optional[Any] = None
