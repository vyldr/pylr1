from collections.abc import Iterator

from ..IO.LRBinaryReader import LRBinaryReader

from ..Utils.LRVector3 import LRVector3
from ..Utils.LRVector2 import LRVector2
from ..Utils.LRColor import LRColor


class GDB_Vertex_Color:
    position: LRVector3
    tex_coords: LRVector2
    color: LRColor

    def __init__(
        self,
        position: LRVector3 = LRVector3(),
        tex_coords: LRVector2 = LRVector2(),
        color: LRColor = LRColor(),
    ) -> None:
        self.position = position
        self.tex_coords = tex_coords
        self.color = color

    def read(self, reader: LRBinaryReader) -> 'GDB_Vertex_Color':
        val: GDB_Vertex_Color = GDB_Vertex_Color()
        val.position = LRVector3.read(None, reader)
        val.tex_coords = LRVector2.read(None, reader)
        val.color = LRColor.read(None, reader)

        val.tex_coords.y = val.tex_coords.y
        return val

    def __iter__(self) -> Iterator[float]:
        return iter(self.position.to_tuple())

    def __str__(self) -> str:
        return (
            'GDB_Vertex_Color: {'
            f'position: {self.position}, '
            f'tex_coords: {self.tex_coords}, '
            f'color: {self.color}'
            '}'
        )
