from abc import ABC, abstractmethod
from enum import IntEnum

from ..IO.LRBinaryReader import LRBinaryReader
from .Token import Token


class PROPERTY(IntEnum):
    MATERIAL_ID = 0x27
    INDICES_META = 0x2D
    VERTEX_META = 0x31
    BONE_ID = 0x32


class GDB_Meta(ABC):
    @property
    @abstractmethod
    def meta_type(self) -> int:
        pass

    def read(self, reader: LRBinaryReader) -> 'GDB_Meta':
        type: int = reader.read_int(Token.Byte)
        match type:
            case PROPERTY.MATERIAL_ID:
                return GDB_Meta_Material.read(None, reader)
            case PROPERTY.INDICES_META:
                return GDB_Meta_Faces.read(None, reader)
            case PROPERTY.VERTEX_META:
                return GDB_Meta_Vertices.read(None, reader)
            case PROPERTY.BONE_ID:
                return GDB_Meta_Bone.read(None, reader)
            case _:
                raise ValueError(
                    f'Unexpected type: {hex(type)}, Position: {hex(reader.position)}'
                )

    @abstractmethod
    def __str__(self) -> str:
        pass


class GDB_Meta_Material(GDB_Meta):
    @property
    def meta_type(self) -> int:
        return PROPERTY.MATERIAL_ID

    material_id: int

    def read(
        self: 'GDB_Meta_Material | None', reader: LRBinaryReader
    ) -> 'GDB_Meta_Material':
        val: GDB_Meta_Material = GDB_Meta_Material()
        val.material_id = reader.read_int(Token.UShort, True)
        return val

    def __str__(self) -> str:
        return f'GDB_Meta_Material: {{material_id: {self.material_id}}}'


class GDB_Meta_Faces(GDB_Meta):
    @property
    def meta_type(self) -> int:
        return PROPERTY.INDICES_META

    offset: int
    length: int

    def read(self: 'GDB_Meta_Faces | None', reader: LRBinaryReader) -> 'GDB_Meta_Faces':
        val: GDB_Meta_Faces = GDB_Meta_Faces()
        val.offset = reader.read_int(Token.UShort, True)
        val.length = reader.read_int(Token.UShort, True)
        return val

    def __str__(self) -> str:
        return f'GDB_Meta_Indices: {{offset: {self.offset}, length: {self.length}}}'


class GDB_Meta_Vertices(GDB_Meta):
    @property
    def meta_type(self) -> int:
        return PROPERTY.VERTEX_META

    shift_forward_count: int
    offset: int
    length: int

    def read(
        self: 'GDB_Meta_Vertices | None', reader: LRBinaryReader
    ) -> 'GDB_Meta_Vertices':
        val: GDB_Meta_Vertices = GDB_Meta_Vertices()
        val.shift_forward_count = reader.read_int(Token.Byte, True)
        val.offset = reader.read_int(Token.UShort, True)
        val.length = reader.read_int(Token.UShort, True)
        return val

    def __str__(self) -> str:
        return f'GDB_Meta_Vertices: {{offset: {self.offset}, length: {self.length}}}'


class GDB_Meta_Bone(GDB_Meta):
    @property
    def meta_type(self) -> int:
        return PROPERTY.BONE_ID

    bone_id: int

    def read(self: 'GDB_Meta_Bone | None', reader: LRBinaryReader) -> 'GDB_Meta_Bone':
        val: GDB_Meta_Bone = GDB_Meta_Bone()
        val.bone_id = reader.read_int(Token.UShort, True)
        return val

    def __str__(self) -> str:
        return f'GDB_Meta_Bone: {{bone_id: {self.bone_id}}}'
