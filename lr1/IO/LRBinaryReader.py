from typing import IO
from typing import Any
from collections.abc import Callable
import struct

from ..Utils.Token import Token
from ..Utils.LRVector3 import LRVector3

# Convert tokens to format characters
FORMAT = {
    Token.Float: 'f',
    Token.Int32: 'i',
    Token.SByte: 'b',
    Token.Byte: 'B',
    Token.Short: 'h',
    Token.UShort: 'H',
}


class LRBinaryReader:
    """
    File reader with functions to read specialized binary data

    Attributes:
        reader (BytesIO): The data to read from
        position (int): The current read position in the file
    """

    reader: IO[bytes]
    _length: int

    def __init__(self, file: IO[bytes]):
        self.reader = file

        # Calculate the length of the file by seeking to the end
        current_pos = self.reader.tell()
        self.reader.seek(0, 2)
        self._length = self.reader.tell()
        self.reader.seek(current_pos, 0)

    def __len__(self) -> int:
        return self._length

    @property
    def position(self) -> int:
        return self.reader.tell()

    def expect(self, expected: int | list[int]) -> int:
        """Reads a byte that we hopefully know in advance"""

        actual: int = self.read_int(Token.Byte)

        if type(expected) is list[int]:
            if actual not in expected:
                raise ValueError(
                    f'Invalid Token.  Expected {str(expected)}.  Got {str(actual)}'
                )

        elif type(expected) is int:
            if actual != expected:
                raise ValueError(
                    f'Invalid data. Expected {hex(expected)}. Got {hex(actual)}.'
                )

        return actual

    def next(self, expected: Token) -> bool:
        """Checks the next byte without changing the read position"""

        actual: int = self.read_int(Token.Byte)
        self.reader.seek(-1, 1)  # Go back one byte
        return actual == expected

    def read_bytes(self, count: int) -> bytes:
        """Reads an array of bytes"""

        return self.reader.read(count)

    def read_int(self, format: Token, header: bool = False) -> int:
        """Reads an integer-like value"""

        # Optionally read the header
        if header:
            self.expect(format)

        fmt: str = f'<{FORMAT[format]}'
        size = struct.calcsize(fmt)
        bytes_read = self.reader.read(size)
        return int(struct.unpack(fmt, bytes_read)[0])

    def read_float(self, header: bool = False) -> float:
        """Reads a float value from the file"""

        # Optionally read the header
        if header:
            self.expect(Token.Float)

        bytes_read = self.reader.read(4)
        f: float = struct.unpack('<f', bytes_read)[0]
        return f

    def read_typed_int(self) -> int:
        """Reads the header byte to determine the format, then reads the value"""

        valid_types: list[int] = [
            Token.SByte,
            Token.Byte,
            Token.Int32,
            Token.UShort,
            Token.Short,
        ]
        type: int = self.expect(valid_types)

        return self.read_int(Token(type))

    def read_string(self, header: bool = False) -> str:
        """Reads a C style string, character bytes terminated by a null byte"""

        # Optionally read the header
        if header:
            self.expect(Token.String)

        string: str = ''
        byte: int

        # Read characters until null byte
        while True:
            byte = self.read_int(Token.Byte)
            if byte == 0x00:
                break
            string += chr(byte)

        return string

    def read_array_block(
        self, read_func: Callable[[Any, 'LRBinaryReader'], Any]
    ) -> list[Any]:
        """Reads the array setup and length, then uses the read_func to read each item"""

        output: list[Any] = []

        # Read the array length
        self.expect(Token.LeftBracket)
        array_len: int = self.read_int(Token.Int32, True)
        self.expect(Token.RightBracket)

        # Read the array
        self.expect(Token.LeftCurly)
        for _ in range(array_len):
            output.append(read_func(None, self))
        self.expect(Token.RightCurly)

        return output

    def read_dict_block(
        self, read_func: Callable[[Any, 'LRBinaryReader'], Any], type_byte: int
    ) -> dict[str, Any]:
        """Reads a dictionary from the binary file"""

        output: dict[str, Any] = dict()

        # Read the dictionary length
        self.expect(Token.LeftBracket)
        dict_len: int = self.read_int(Token.Int32, True)
        self.expect(Token.RightBracket)

        # Read the dictionary
        self.expect(Token.LeftCurly)
        for i in range(dict_len):
            self.expect(type_byte)
            item_key: str = str(i)
            if self.next(Token.String):
                item_key = self.read_string(True)
            item_value: Any = self.read_struct(read_func)
            output[item_key] = item_value
        self.expect(Token.RightCurly)

        return output

    def read_struct(self, read_func: Callable[[Any, 'LRBinaryReader'], Any]) -> Any:
        self.expect(Token.LeftCurly)
        output: Any = read_func(None, self)
        self.expect(Token.RightCurly)
        return output

    def read_str_array_block(self) -> list[str]:
        """Reads an array of strings"""

        return self.read_array_block(lambda _, br: br.read_string(True))

    def read_vector_3f_array_block(self) -> list[LRVector3]:
        """Reads an array of Vector3"""

        return self.read_array_block(LRVector3.read)
