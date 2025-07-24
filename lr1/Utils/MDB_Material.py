from enum import IntEnum

from .LRColor import LRColor
from .Token import Token
from ..IO.LRBinaryReader import LRBinaryReader
from ..BMP import BMP


class PROPERTY(IntEnum):
    # TODO: Find out what all of these values mean
    AMBIENT_COLOR = 0x28
    DIFFUSE_COLOR = 0x29
    P_2A = 0x2A
    P_2B = 0x2B
    TEXTURE_NAME = 0x2C
    P_2D = 0x2D
    P_2E = 0x2E
    P_38 = 0x38
    P_3A = 0x3A
    P_3F = 0x3F
    P_41 = 0x41
    P_45 = 0x45
    ALPHA = 0x46
    P_4A = 0x4A


class MDB_Material:
    ambient_color: LRColor | None
    diffuse_color: LRColor | None
    bool_2a: bool
    bool_2b: bool
    texture_name: str
    bool_2d: bool
    bool_2e: bool
    bool_38: bool
    bool_3a: bool
    bool_3f: bool
    bool_41: bool
    bool_45: bool
    alpha: int
    bool_4a: bool

    texture: BMP

    def __init__(self) -> None:
        self.ambient_color = None
        self.diffuse_color = None
        self.bool_2a = False
        self.bool_2b = False
        self.texture_name = ''
        self.bool_2d = False
        self.bool_2e = False
        self.bool_38 = False
        self.bool_3a = False
        self.bool_3f = False
        self.bool_41 = False
        self.bool_45 = False
        self.alpha = 0xFF
        self.bool_4a = False

    def read(self: 'MDB_Material | None', reader: LRBinaryReader) -> 'MDB_Material':
        val: MDB_Material = MDB_Material()

        while not reader.next(Token.RightCurly):
            property_id: int = reader.read_int(Token.Byte)
            match property_id:
                case PROPERTY.AMBIENT_COLOR:
                    val.ambient_color = LRColor().read(reader)

                case PROPERTY.DIFFUSE_COLOR:
                    val.diffuse_color = LRColor().read(reader)

                case PROPERTY.P_2A:
                    val.bool_2a = True

                case PROPERTY.P_2B:
                    val.bool_2b = True

                case PROPERTY.TEXTURE_NAME:
                    val.texture_name = reader.read_string(True)
                    val.texture = BMP()

                case PROPERTY.P_2D:
                    val.bool_2d = True

                case PROPERTY.P_2E:
                    val.bool_2e = True

                case PROPERTY.P_38:
                    val.bool_38 = True

                case PROPERTY.P_3A:
                    val.bool_3a = True

                case PROPERTY.P_3F:
                    val.bool_3f = True

                case PROPERTY.P_41:
                    val.bool_41 = True

                case PROPERTY.P_45:
                    val.bool_45 = True

                case PROPERTY.ALPHA:
                    val.alpha = reader.read_int(Token.Int32, True)

                case PROPERTY.P_4A:
                    val.bool_4a = True

                case _:
                    raise ValueError(property_id, reader.position - 1)
        return val

    def bool_str(self, value: bool | None) -> str:
        """Make a bool easier to read in debug output"""

        if value:
            return '1'
        else:
            return '-'

    def __str__(self) -> str:
        return (
            f'Texture: {self.texture_name:<8}  '
            f'{self.bool_str(self.bool_2a)}'
            f'{self.bool_str(self.bool_2b)}'
            f'{self.bool_str(self.bool_2d)}'
            f'{self.bool_str(self.bool_2e)}'
            f'{self.bool_str(self.bool_38)}'
            f'{self.bool_str(self.bool_3a)}'
            f'{self.bool_str(self.bool_3f)}'
            f'{self.bool_str(self.bool_41)}'
            f'{self.bool_str(self.bool_45)}'
            f'{self.bool_str(self.bool_4a)}  '
            f'Alpha: {str(self.alpha):<3}  '
            f'Ambient: {(self.ambient_color.hex() if self.ambient_color is not None else ""):<9}  '
            f'Diffuse: {(self.diffuse_color.hex() if self.diffuse_color is not None else ""):<9}'
        )
