from dataclasses import dataclass
from enum import StrEnum
from typing import assert_never


class AlertColor(StrEnum):
    """
    Defines the priority of each color. Green and yellow pass the normal
    form, gray reports missing information but keeps the flow going, and
    red stops the pipe flow.
    """

    GREEN = 'GREEN'
    YELLOW = 'YELLOW'
    RED = 'RED'
    GRAY = 'GRAY'

    @property
    def blocks_pipeline(self) -> bool:
        match self:
            case AlertColor.RED:  # Stops the algorithm
                return True
            case AlertColor.GREEN | AlertColor.YELLOW | AlertColor.GRAY:
                # Continue the algorithm: gray still raises its alert.
                return False
            case _:
                assert_never(self)


@dataclass(frozen=True)
class Alert:
    color: AlertColor
    message: str
    associated_table: str

    @property
    def blocks_pipeline(self) -> bool:
        return self.color.blocks_pipeline
