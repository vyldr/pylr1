from ..IO.LRBinaryReader import LRBinaryReader


class BVB_PolygonRange:
    index_left: int
    index_right: int
    node_left: 'BVB_PolygonRange | None'
    node_right: 'BVB_PolygonRange | None'
    x: int
    y: int
    z: int
    first_poly: int
    num_polys: int

    def read(
        self: 'BVB_PolygonRange | None', reader: LRBinaryReader
    ) -> 'BVB_PolygonRange':
        val: BVB_PolygonRange = BVB_PolygonRange()

        val.index_left = reader.read_typed_int()
        val.index_right = reader.read_typed_int()
        val.x = reader.read_typed_int()
        val.y = reader.read_typed_int()
        val.z = reader.read_typed_int()
        val.first_poly = reader.read_typed_int()
        val.num_polys = reader.read_typed_int()

        # Tree nodes
        val.node_left = None
        val.node_right = None

        return val

    def __str__(self) -> str:
        return (
            'BVB_PolygonRange: {'
            f'left:{self.index_left}, '
            f'right:{self.index_right}, '
            f'x:{self.x}, '
            f'y:{self.y}, '
            f'z:{self.z}, '
            f'FirstPoly:{self.first_poly}, '
            f'NumPolys:{self.num_polys}'
            '}'
        )
