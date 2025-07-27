from ..IO.LRBinaryReader import LRBinaryReader

from ..Utils.LRVector3 import LRVector3
from ..Utils.LRVector2 import LRVector2


class GDB_Vertex_Normal:
    position: LRVector3
    tex_coords: LRVector2
    normal: LRVector3

    def __init__(
        self,
        position: LRVector3 = LRVector3(),
        tex_coords: LRVector2 = LRVector2(),
        normal: LRVector3 = LRVector3(),
    ) -> None:
        self.position = position
        self.tex_coords = tex_coords
        self.normal = normal

    def read(self, reader: LRBinaryReader) -> 'GDB_Vertex_Normal':
        val: GDB_Vertex_Normal = GDB_Vertex_Normal()
        val.position = LRVector3().read(reader)
        val.tex_coords = LRVector2().read(reader)
        val.normal = LRVector3().read(reader)
        return val
