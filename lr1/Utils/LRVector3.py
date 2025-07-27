from typing import TYPE_CHECKING
import math

if TYPE_CHECKING:
    from ..IO.LRBinaryReader import LRBinaryReader


class LRVector3:
    x: float
    y: float
    z: float

    def __init__(self, x: float = 0, y: float = 0, z: float = 0) -> None:
        self.x = x
        self.y = y
        self.z = z

    def read(self, reader: 'LRBinaryReader') -> 'LRVector3':
        """Reads the vector components from a file"""
        val: LRVector3 = LRVector3()
        val.x = reader.read_float(True)
        val.y = reader.read_float(True)
        val.z = reader.read_float(True)

        return val

    def normalize(self) -> None:
        """Scales the vector to a magnitude of 1"""

        length: float = math.sqrt(self.x**2 + self.y**2 + self.z**2)
        if length == 0:
            raise ValueError('Cannot normalize a zero-length vector')
        self.x = self.x / length
        self.y = self.y / length
        self.z = self.z / length

    def __add__(self, v: 'LRVector3') -> 'LRVector3':
        return LRVector3(self.x + v.x, self.y + v.y, self.z + v.z)

    def scale(
        self, x: float = 1, y: float | None = None, z: float | None = None
    ) -> 'LRVector3':
        """Scales the vector by x, y, and z.  Scales proportionally if only x is provided"""

        # Scale proportionally if only x is provided
        if z is None or y is None:
            y, z = x, x

        self.x *= x
        self.y *= y
        self.z *= z

        return self

    def scaled(self, multiplier: float) -> 'LRVector3':
        """Returns a new LRVector3, scaled by the multiplier"""

        val: LRVector3 = LRVector3(self.x, self.y, self.z)
        val.scale(multiplier)
        return val

    def to_tuple(self) -> tuple[float, float, float]:
        return (self.x, self.y, self.z)

    def __str__(self) -> str:
        return f'LRVector3: {{X:{self.x}, Y:{self.y}, Z:{self.z}}}'

    def __len__(self) -> int:
        return 3

    def __getitem__(self, i: int) -> float:
        match i:
            case 0:
                return self.x
            case 1:
                return self.y
            case 2:
                return self.z
            case _:
                raise IndexError(f'Index out of range: {i}')
