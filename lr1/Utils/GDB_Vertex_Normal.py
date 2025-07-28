from collections.abc import Iterator

from ..IO.LRBinaryReader import LRBinaryReader

from ..Utils.LRVector3 import LRVector3
from ..Utils.LRVector2 import LRVector2
from ..Utils.GDB_Vertex import GDB_Vertex


class GDB_Vertex_Normal(GDB_Vertex):
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

    def read(self, reader: LRBinaryReader) -> 'GDB_Vertex':
        val: GDB_Vertex_Normal = GDB_Vertex_Normal()
        val.position = LRVector3().read(reader)
        val.tex_coords = LRVector2().read(reader)
        val.normal = LRVector3().read(reader)
        return val

    def __iter__(self) -> Iterator[float]:
        return iter(self.position.to_tuple())

    def __str__(self) -> str:
        return (
            'GDB_Vertex_Normal: {'
            f'position: {self.position}, '
            f'tex_coords: {self.tex_coords}, '
            f'normal: {self.normal}'
            '}'
        )
