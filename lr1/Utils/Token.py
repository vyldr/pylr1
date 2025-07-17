from enum import IntEnum


class Token(IntEnum):
    """Each Token is a byte that represents the next data type in the file, unless it's a bracket"""

    String = 0x02
    Float = 0x03
    Int32 = 0x04
    LeftCurly = 0x05
    RightCurly = 0x06
    LeftBracket = 0x07
    RightBracket = 0x08
    SByte = 0x0B
    Byte = 0x0C
    Short = 0x0D
    UShort = 0x0E
    Array = 0x14
    Struct = 0x16
