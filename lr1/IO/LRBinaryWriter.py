from io import BytesIO


class LRBinaryWriter:
    writer: BytesIO

    def __init__(self, writer: BytesIO) -> None:
        self.writer = writer

    def write_token(self, token: int) -> None:
        self.writer.write(bytes([token]))

    def write_bytes(self, value: bytes) -> None:
        self.writer.write(value)

    def write_string(self, value: str) -> None:
        self.writer.write(value.encode('ascii'))
        self.writer.write(b'\x00')
