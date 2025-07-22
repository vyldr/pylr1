from enum import IntEnum

from .Utils.Token import Token
from .Utils.LRVector3 import LRVector3
from .Utils.BVB_Polygon import BVB_Polygon
from .Utils.BVB_PolygonRange import BVB_PolygonRange
from .IO.LRBinaryReader import LRBinaryReader
from .Utils.BinaryFileHelper import BinaryFileHelper
from .IO.LRFile import LRFile


class ID(IntEnum):
    MATERIALS = 0x27
    POLYGONS = 0x2D
    VERTICES = 0x34
    POLYGON_RANGES = 0x8E


class BVB:
    """
    Collision boundaries for the track

    Attributes:
        materials (list[str]): List of material names used in the BVB
        vertices (list[LRVector3]): List of vertices in the BVB
        polygons (list[BVB_Polygon]): List of polygons defined by vertices and materials
    """

    materials: list[str]
    vertices: list[LRVector3]
    polygons: list[BVB_Polygon]
    polygon_ranges: list[BVB_PolygonRange]

    def __init__(self, file: LRFile) -> None:
        helper: BinaryFileHelper = BinaryFileHelper()
        reader: LRBinaryReader = helper.decompress(file.data)

        self.materials = []
        self.vertices = []
        self.polygons = []
        self.polygon_ranges = []

        while reader.position < len(reader):
            block_id: int = reader.read_int(Token.Byte)

            match block_id:
                case ID.MATERIALS:
                    self.materials = reader.read_str_array_block()

                case ID.POLYGONS:
                    self.polygons = reader.read_array_block(BVB_Polygon.read)

                case ID.VERTICES:
                    self.vertices = reader.read_vector_3f_array_block()

                case ID.POLYGON_RANGES:
                    self.polygon_ranges = reader.read_array_block(BVB_PolygonRange.read)

                case _:
                    raise ValueError(
                        f'Unexpected block: {hex(block_id)}, Position: {hex(reader.position)}'
                    )

        self.build_tree()

    def build_tree(self) -> None:
        for polygon_range in self.polygon_ranges:
            if polygon_range.index_left >= 0:
                polygon_range.node_left = self.polygon_ranges[polygon_range.index_left]
            if polygon_range.index_right >= 0:
                polygon_range.node_right = self.polygon_ranges[
                    polygon_range.index_right
                ]
