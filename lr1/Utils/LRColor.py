from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..IO.LRBinaryReader import LRBinaryReader


class LRColor:
    r: int
    g: int
    b: int
    a: int

    def __init__(
        self, r: int = 0, g: int = 0, b: int = 0, a: int = 255
    ) -> None:
        self.r = r
        self.g = g
        self.b = b
        self.a = a

    def read(self: 'LRColor | None', reader: 'LRBinaryReader') -> 'LRColor':
        val: LRColor = LRColor()
        val.r = reader.read_typed_int()
        val.g = reader.read_typed_int()
        val.b = reader.read_typed_int()
        val.a = reader.read_typed_int()

        return val

    def to_tuple(self) -> tuple[float, float, float, float]:
        """Converts to a tuple of floats 0.0 - 1.0 for Blender"""

        return (self.r / 255.0, self.g / 255.0, self.b / 255.0, self.a / 255.0)

    def __str__(self) -> str:
        return f'LRColor: {{R:{self.r:>3}, G:{self.g:>3}, B:{self.b:>3}, A:{self.a:>3}}}'

    def hex(self) -> str:
        """Returns the color as a hex string for debug"""

        return '#{:02X}{:02X}{:02X}{:02X}'.format(
            self.r, self.g, self.b, self.a
        )

    def __len__(self) -> int:
        return 4

    def __getitem__(self, i: int) -> float:
        """Accesses vertices by index"""
        match i:
            case 0:
                return self.r
            case 1:
                return self.g
            case 2:
                return self.b
            case 3:
                return self.a
            case _:
                raise IndexError(f'Index out of range: {i}')
