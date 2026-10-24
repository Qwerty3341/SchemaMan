from dataclasses import dataclass
from enum import StrEnum
from typing import assert_never


class AlertColor(StrEnum):
    GREEN = 'green'
    YELLOW = 'yellow'
    RED = 'red'
    GRAY = 'gray'

    @property
    def blocks_pipeline(self) -> bool:
        match self:
            case AlertColor.RED | AlertColor.GRAY:  # Stops the algorithm
                return True
            case AlertColor.GREEN | AlertColor.YELLOW:  # Continue the algorithm
                return False
            case _:
                assert_never(self)


@dataclass(frozen=True)
class Alert:
    color: AlertColor

    @property
    def blocks_pipeline(self) -> bool:
        return self.color.blocks_pipeline
