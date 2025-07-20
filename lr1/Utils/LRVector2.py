from typing import TYPE_CHECKING
import math

if TYPE_CHECKING:
    from ..IO.LRBinaryReader import LRBinaryReader


class LRVector2:
    x: float
    y: float

    def __init__(self, x: float = 0, y: float = 0) -> None:
        self.x = x
        self.y = y

    def read(self: 'LRVector2 | None', reader: 'LRBinaryReader') -> 'LRVector2':
        val: LRVector2 = LRVector2()
        val.x = reader.read_float(True)
        val.y = reader.read_float(True)

        return val

    def normalize(self) -> None:
        """Scales the vector to a magnitude of 1"""

        length: float = math.sqrt(self.x**2 + self.y**2)
        if length == 0:
            raise ValueError('Cannot normalize a zero-length vector')
        self.x = self.x / length
        self.y = self.y / length

    def __add__(self, v: 'LRVector2') -> 'LRVector2':
        self.x += v.x
        self.y += v.y
        return self

    def scale(self, x: float = 1, y: float | None = None) -> 'LRVector2':
        """Scales the vector by x and y.  Scales proportionally if only x is provided"""

        # Only x is provided, scale proportionally
        if y is None:
            y = x

        self.x *= x
        self.y *= y

        return self

    def scaled(self, multiplier: float) -> 'LRVector2':
        """Returns a new LRVector2, scaled by the multiplier"""

        val: LRVector2 = LRVector2(self.x, self.y)
        val.scale(multiplier)
        return val

    def to_tuple(self) -> tuple[float, float]:
        return (self.x, self.y)

    def __str__(self) -> str:
        return f'LRVector2: {{X:{self.x}, Y:{self.y}}}'

    def __len__(self) -> int:
        return 2

    def __getitem__(self, i: int) -> float:
        match i:
            case 0:
                return self.x
            case 1:
                return self.y
            case _:
                raise IndexError(f'Index out of range: {i}')
