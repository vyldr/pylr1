from .Utils.BinaryFileHelper import BinaryFileHelper
from .IO.LRBinaryReader import LRBinaryReader
from .Utils.Token import Token
from .IO.LRFile import LRFile

from .Utils.TDB_Texture import TDB_Texture

ID_TEXTURES: int = 0x27


class TDB:
    textures: dict[str, TDB_Texture]

    def __init__(self, file: LRFile) -> None:
        helper: BinaryFileHelper = BinaryFileHelper()
        reader: LRBinaryReader = helper.decompress(file.data)

        self.textures = dict()
        while reader.position < len(reader):
            block_id: int = reader.read_int(Token.Byte)
            match block_id:
                case int(ID_TEXTURES):
                    self.textures = reader.read_dict_block(
                        TDB_Texture.read, ID_TEXTURES
                    )

                case _:
                    raise ValueError(
                        f'Invalid block_id: {block_id}, position: {reader.position - 1}'
                    )
