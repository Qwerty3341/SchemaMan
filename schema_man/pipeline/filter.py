from abc import ABC, abstractmethod
from .context import PipeLineContext


class Filter(ABC):
    @abstractmethod
    def apply(self, context: PipeLineContext) -> PipeLineContext:
        """Process the context and returns it"""
        raise NotImplementedError
