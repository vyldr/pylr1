from abc import ABC, abstractmethod
from collections.abc import Iterator

from ..IO.LRBinaryReader import LRBinaryReader


class GDB_Vertex(ABC):
    """Abstract base class for GDB vertex types."""

    @abstractmethod
    def read(self, reader: LRBinaryReader) -> 'GDB_Vertex':
        """Read the vertex data from the binary reader."""
        pass

    @abstractmethod
    def __iter__(self) -> Iterator[float]:
        """Return an iterator over the vertex data."""
        pass

    @abstractmethod
    def __str__(self) -> str:
        """Return a string representation of the vertex."""
        pass
