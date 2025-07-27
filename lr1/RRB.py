from enum import IntEnum

from .Utils.BinaryFileHelper import BinaryFileHelper
from .IO.LRBinaryReader import LRBinaryReader
from .IO.LRFile import LRFile

from .Utils.Token import Token
from .Utils.RRB_Node import RRB_Node
from .Utils.LRQuaternion import LRQuaternion
from .Utils.LRVector3 import LRVector3


class ID(IntEnum):
    NODES = 0x27
    START_ROTATION = 0x28
    START_POSITION = 0x29
    END_POSITION = 0x2A
    END_ROTATION = 0x2B
    TIMING = 0x2C
    UNKNOWN_2D = 0x2D


class RRB:
    nodes: list[RRB_Node]

    start_rotation: LRQuaternion
    start_position: LRVector3

    end_rotation: LRQuaternion
    end_position: LRVector3

    milliseconds: int
    unknown_2D: int

    def __init__(self, file: LRFile) -> None:
        helper: BinaryFileHelper = BinaryFileHelper()
        reader: LRBinaryReader = helper.decompress(file.data)

        while reader.position < len(reader):
            blockId: int = reader.read_int(Token.Byte)

            match blockId:
                case ID.NODES:
                    self.nodes = reader.read_array_block(RRB_Node.read)

                case ID.START_ROTATION:
                    self.start_rotation = LRQuaternion().read(reader)

                case ID.START_POSITION:
                    self.start_position = LRVector3().read(reader)

                case ID.END_POSITION:
                    self.end_position = LRVector3().read(reader)

                case ID.END_ROTATION:
                    self.end_rotation = LRQuaternion().read(reader)

                case ID.TIMING:
                    self.milliseconds = reader.read_int(Token.Int32, True)

                case ID.UNKNOWN_2D:
                    self.unknown_2D = reader.read_int(Token.Int32, True)

                case _:
                    raise ValueError(f'The byte is 0x{blockId:02X}')
