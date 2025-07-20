from ..IO.LRBinaryReader import LRBinaryReader


class GDB_Polygon:
    """A triangle defined by three vertex ids"""

    v0: int
    v1: int
    v2: int

    uv: list[int]

    bone: int

    def __init__(
        self, v0: int, v1: int, v2: int, uv: list[int] | None = None, bone: int = 0
    ) -> None:
        self.v0 = v0
        self.v1 = v1
        self.v2 = v2

        self.uv = uv if uv is not None else []

        self.bone = bone

    def read(self: 'GDB_Polygon | None', reader: LRBinaryReader) -> 'GDB_Polygon':
        val: GDB_Polygon = GDB_Polygon(0, 0, 0)

        val.v0 = reader.read_typed_int()
        val.v1 = reader.read_typed_int()
        val.v2 = reader.read_typed_int()

        return val

    def __str__(self) -> str:
        return (
            'GDB_Polygon: (' + f'{self.v0}, \t' + f'{self.v1}, \t' + f'{self.v2}' + ')'
        )

    def __len__(self) -> int:
        return 3  # Triangle

    def __getitem__(self, i: int) -> int:
        match i:
            case 0:
                return self.v0
            case 1:
                return self.v1
            case 2:
                return self.v2
            case _:
                raise IndexError(f'Index out of range: {i}')
