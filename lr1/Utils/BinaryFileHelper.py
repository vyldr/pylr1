from io import BytesIO

from ..IO.LRBinaryReader import LRBinaryReader
from ..IO.LRBinaryWriter import LRBinaryWriter
from ..Utils.Token import Token


class BinaryFileHelper:
    def decompress(self, file: BytesIO) -> LRBinaryReader:
        reader: LRBinaryReader = LRBinaryReader(file)

        structs: dict[int, list[int]] = {}
        stream: BytesIO = BytesIO()

        writer: LRBinaryWriter = LRBinaryWriter(stream)
        while reader.position < len(reader):
            block_id: int = reader.read_int(Token.Byte)
            self.recursive_decompress(block_id, reader, writer, structs)

        stream.seek(0)

        return LRBinaryReader(stream)

    def recursive_decompress(
        self,
        block_id: int,
        reader: LRBinaryReader,
        writer: LRBinaryWriter,
        structs: dict[int, list[int]],
    ) -> None:
        match block_id:
            case (
                Token.LeftCurly
                | Token.RightCurly
                | Token.LeftBracket
                | Token.RightBracket
            ):
                writer.write_token(block_id)

            case Token.Byte | Token.SByte:
                writer.write_token(block_id)
                writer.write_bytes(reader.read_bytes(1))

            case Token.Short | Token.UShort:
                writer.write_token(block_id)
                writer.write_bytes(reader.read_bytes(2))

            case Token.Int32 | Token.Float:
                writer.write_token(block_id)
                writer.write_bytes(reader.read_bytes(4))

            case Token.String:
                writer.write_token(block_id)
                writer.write_string(reader.read_string())

            case Token.Array:
                array_len: int = reader.read_int(Token.Short)
                array_type: int = reader.read_int(Token.Byte)
                for i in range(array_len):
                    self.recursive_decompress(array_type, reader, writer, structs)

            case Token.Struct:
                struct_id: int = reader.read_int(Token.Byte)
                struct_len: int = reader.read_int(Token.Byte)
                struct_def: list[int] = []
                for i in range(struct_len):
                    struct_def.append(reader.read_int(Token.Byte))
                structs[struct_id] = struct_def

            case _:
                if block_id in structs:
                    for i in range(len(structs[block_id])):
                        self.recursive_decompress(
                            structs[block_id][i], reader, writer, structs
                        )
                else:
                    writer.write_bytes(bytes([block_id]))
