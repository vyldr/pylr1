from enum import IntEnum

from ..IO.LRBinaryReader import LRBinaryReader
from ..Utils.Token import Token
from .LRColor import LRColor


class PROPERTY(IntEnum):
    P_28 = 0x28
    BMP_TGA = 0x2A
    P_2B = 0x2B
    TRANS_COLOR = 0x2C
    P_2D = 0x2D


class TDB_Texture:
    bool_28: bool
    is_bitmap: bool
    bool_2b: bool
    trans_color: bool
    color: LRColor
    bool_2d: bool

    def __init__(
        self,
        bool_28: bool = False,
        is_bitmap: bool = False,
        bool_2b: bool = False,
        trans_color: bool = False,
        color: LRColor = LRColor(),
        bool_2d: bool = False,
    ) -> None:
        self.bool_28 = bool_28
        self.is_bitmap = is_bitmap
        self.bool_2b = bool_2b
        self.trans_color = trans_color
        self.color = color
        self.bool_2d = bool_2d

    def read(self, reader: LRBinaryReader) -> 'TDB_Texture':
        val: TDB_Texture = TDB_Texture()
        while not reader.next(Token.RightCurly):
            property_id: int = reader.read_int(Token.Byte)

            match property_id:
                case PROPERTY.P_28:
                    val.bool_28 = True

                case PROPERTY.BMP_TGA:
                    val.is_bitmap = True

                case PROPERTY.P_2B:
                    val.bool_2b = True

                case PROPERTY.TRANS_COLOR:
                    val.trans_color = True
                    val.color = LRColor().read(reader, alpha=False)

                case PROPERTY.P_2D:
                    val.bool_2d = True

                case _:
                    raise ValueError(
                        f'Unexpected property ID: {property_id}, position: {reader.position - 1}'
                    )

        return val

    def bool_str(self, value: bool | None) -> str:
        """Make a bool easier to read in debug output"""

        if value:
            return '1'
        else:
            return '-'

    def __str__(self) -> str:
        return (
            'TDB_Texture: { '
            f'{self.bool_str(self.is_bitmap)}'
            f'{self.bool_str(self.bool_28)}'
            f'{self.bool_str(self.bool_2b)}'
            f'{self.bool_str(self.trans_color)}'
            f'{self.bool_str(self.bool_2d)} '
            f'{self.color} '
            '}'
        )
