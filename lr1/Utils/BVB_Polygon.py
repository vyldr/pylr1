from ..IO.LRBinaryReader import LRBinaryReader


class BVB_Polygon:
    """
    A triangle defined by three vertex ids and a material id

    Attributes:
        vertices (tuple[int, int, int]): A tuple of three integers representing the vertex indices.
        material (int): An integer representing the material index.
    """

    vertices: tuple[int, int, int]
    material: int

    def read(self: 'BVB_Polygon | None', reader: LRBinaryReader) -> 'BVB_Polygon':
        """Read the polygon data from a file"""

        val: BVB_Polygon = BVB_Polygon()

        val.vertices = (
            reader.read_typed_int(),
            reader.read_typed_int(),
            reader.read_typed_int(),
        )

        val.material = reader.read_typed_int()

        return val

    def __str__(self) -> str:
        return (
            'BVB_Polygon: {'
            + f'v0:{self.vertices[0]}, '
            + f'v1:{self.vertices[1]}, '
            + f'v2:{self.vertices[2]}, '
            + f'Material:{self.material}'
            + '}'
        )

    def __len__(self) -> int:
        return 3  # It's a triangle

    def __getitem__(self, i: int) -> int:
        return self.vertices[i]
