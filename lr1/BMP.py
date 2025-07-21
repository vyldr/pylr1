from typing import IO
from io import BytesIO
from enum import IntEnum
import struct

from .IO.LRFile import LRFile
from .Utils.BMP_BitmapColor import BitmapColor


class IMAGE_ENCODING(IntEnum):
    PALETTE_4_BIT = 0x04
    PALETTE_8_BIT = 0x08
    RGB = 0x98


class BMP:
    """
    A BMP image/texture

    Attributes:
        width (int):
        height (int):
        encoding (IMAGE_ENCODING): Whether the image was encoded with a four or eight bit palette or no palette
        image (list[BitmapColor]): Pixels of the image as a list
        palette (list[BitmapColor]): List of colors used in the palette

    """

    width: int
    height: int

    encoding: int
    funny_font: bool  # Some font BMPs don't follow this format perfectly, so we track them when we find them

    image: list[BitmapColor]
    palette: list[BitmapColor]

    def __init__(self, file: LRFile | None = None) -> None:
        if file is None:
            # Create an empty texture
            self.width = 1
            self.height = 1
            self.image = [BitmapColor(r=0, g=0, b=0, a=0)]
            return

        file.reset()

        encoding = file.data.read(1)[0]
        self.encoding = IMAGE_ENCODING(encoding)

        self.funny_font = False

        palette_size: int = file.data.read(1)[0] + 1  # Palette size is off by one

        self.width = struct.unpack('<h', file.data.read(2))[0]
        self.height = struct.unpack('<h', file.data.read(2))[0]

        self.palette = []

        if self.encoding != IMAGE_ENCODING.RGB:
            for _ in range(palette_size):
                self.palette.append(BitmapColor(file.data))

        buffer_length: int = 0

        match self.encoding:
            case IMAGE_ENCODING.PALETTE_4_BIT:
                buffer_length = (self.width * self.height + 1) // 2

            case IMAGE_ENCODING.PALETTE_8_BIT:
                buffer_length = self.width * self.height

            case IMAGE_ENCODING.RGB:
                buffer_length = self.width * self.height * 3

            case _:
                raise ValueError(f'Invalid image encoding: {self.encoding}')

        image_buffer: BytesIO = BytesIO()

        while image_buffer.tell() < buffer_length:
            block: bytes = self.read_block(file.data)
            image_buffer.write(block)

        self.image = []

        match self.encoding:
            case IMAGE_ENCODING.RGB:
                for i in range(self.width * self.height):
                    image_buffer.seek(i * 3)
                    self.image.append(BitmapColor(image_buffer))

            case IMAGE_ENCODING.PALETTE_4_BIT:
                for i in range(self.width * self.height):
                    image_buffer.seek(i // 2)
                    index: int = image_buffer.read(1)[0]
                    index >>= 4 * (1 - (i % 2))
                    index &= 0x0F
                    if index not in range(len(self.palette)):
                        self.funny_font = True
                        print(f'Bad index: {index} at pixel: {i}')
                        index %= len(self.palette)
                        self.image.append(BitmapColor(r=255, g=0, b=0))
                    else:
                        self.image.append(self.palette[index])

            case IMAGE_ENCODING.PALETTE_8_BIT:
                for i in range(self.width * self.height):
                    image_buffer.seek(i)
                    index = image_buffer.read(1)[0]
                    self.image.append(self.palette[index])

        # Fix the broken font files
        if self.funny_font:
            self.width += 1
        while len(self.image) < self.width * self.height:
            self.image.append(self.image[0])

    def read_block(self, file: IO[bytes]) -> bytes:
        block_length_decompressed: int = struct.unpack('<h', file.read(2))[0]
        block_length_compressed: int = struct.unpack('<h', file.read(2))[0]

        if block_length_compressed == block_length_decompressed:
            return file.read(block_length_compressed)

        buffer: BytesIO = BytesIO()
        buffer.write(file.read(1))

        while self.read_sub_block(file, buffer):
            pass

        assert buffer.getbuffer().nbytes == block_length_decompressed

        return buffer.getvalue()

    def read_sub_block(self, reader: IO[bytes], buffer: BytesIO) -> bool:
        block_map: int = reader.read(1)[0]
        for _ in range(8):
            if block_map & 0x80:
                foo: int = reader.read(1)[0]
                repeat: int = foo & 0x0F
                goback: int = (foo & 0xF0) << 4
                goback += reader.read(1)[0]

                if repeat:
                    repeat = -(repeat - 0x12)

                else:
                    if goback == 0:
                        return False

                    repeat = reader.read(1)[0] + 0x12

                for _ in range(repeat):
                    # Read byte to copy
                    buffer.seek(-goback, 2)
                    copied_byte: bytes = buffer.read(1)

                    # Write to end of buffer
                    buffer.seek(0, 2)
                    buffer.write(copied_byte)

            else:
                buffer.write(reader.read(1))

            block_map <<= 1

        return True

    def console_preview(self) -> None:
        """Prints the image in the terminal for debugging"""

        for i, pixel in enumerate(self.image):
            if i % self.width == 0:
                print()
            pixel.color_print(end='')

        print()

    def show_palette(self) -> None:
        """Prints a square of each color in the palette to the terminal"""

        for color in self.palette:
            color.color_print(end='')
        print()

    def flat_pixels(self) -> list[float]:
        """Converts the image to a list of floats for Blender"""

        flattened: list[float] = []

        for pixel in self.image:
            flattened.extend(pixel.as_float())

        return flattened

    def get_pixel(self, x: int, y: int) -> BitmapColor:
        """Returns the pixel at the XY coordinates"""

        if x < 0 or y < 0 or x >= self.width or y >= self.height:
            raise IndexError(f'Pixel {x}, {y} out of range')
        return self.image[y * self.width + x]

    def checker_fallback(self: 'BMP | None' = None, square_size: int = 4) -> 'BMP':
        """Returns a fallback texture with a checkerboard pattern"""

        bmp = BMP()
        bmp.width = 8
        bmp.height = 8
        bmp.palette = [
            BitmapColor(r=248, g=0, b=248),  # Magenta
            BitmapColor(r=0, g=0, b=0),  # Black
        ]
        bmp.image = []

        for i in range(bmp.width * bmp.height):
            x = i % bmp.width // square_size
            y = i // bmp.width // square_size
            if (x + y) % 2 == 0:
                bmp.image.append(bmp.palette[0])
            else:
                bmp.image.append(bmp.palette[1])
        return bmp
