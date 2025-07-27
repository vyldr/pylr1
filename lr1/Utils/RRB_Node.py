from ..IO.LRBinaryReader import LRBinaryReader
from ..Utils.LRVector3 import LRVector3
from ..Utils.LRQuaternion import LRQuaternion
from ..Utils.Token import Token


class RRB_Node:
    position: LRVector3
    rotation: LRQuaternion
    f1: float
    f2: float
    timing: int

    def __init__(self, f1: float = 0, f2: float = 0, timing: int = 0) -> None:
        self.position = LRVector3()
        self.rotation = LRQuaternion()
        self.f1 = f1
        self.f2 = f2
        self.timing = timing

    def read(self, reader: LRBinaryReader) -> 'RRB_Node':
        val: RRB_Node = RRB_Node()

        # Don't use LRVector3.Read() here because we are not reading floats
        val.position.x = reader.read_typed_int()
        val.position.y = reader.read_typed_int()
        val.position.z = reader.read_typed_int()
        val.position.scale(1.0 / 256, 1.0 / 256, 1.0 / 16)

        # ZWXY?
        val.rotation.z = reader.read_typed_int() / 127.0
        val.rotation.w = reader.read_typed_int() / 127.0
        val.rotation.x = reader.read_typed_int() / 127.0
        val.rotation.y = reader.read_typed_int() / 127.0

        val.f1 = reader.read_int(Token.SByte, True)
        val.f2 = reader.read_int(Token.SByte, True)

        val.timing = reader.read_int(Token.Byte, True)

        return val

    def __str__(self) -> str:
        return (
            'RRB_Node: {'
            f'DX:{self.position.x}, '
            f'DY:{self.position.y}, '
            f'DZ:{self.position.z}, '
            f'RX:{self.rotation.x}, '
            f'RY:{self.rotation.y}, '
            f'RZ:{self.rotation.z}, '
            f'RW:{self.rotation.w}, '
            f'F1:{self.f1}, '
            f'F2:{self.f2}, '
            f'Time:{self.timing}'
            '}'
        )
