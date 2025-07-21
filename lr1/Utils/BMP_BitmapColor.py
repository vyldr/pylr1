from typing import IO


class BitmapColor:
    """Representation of a RGBA color, with one byte per color"""

    r: int
    g: int
    b: int
    a: int

    def __init__(
        self,
        reader: IO[bytes] | None = None,
        r: int = 0,
        g: int = 0,
        b: int = 0,
        a: int = 0xFF,
    ) -> None:
        # Read the color from the binary file
        if reader:
            # BGR
            self.b = reader.read(1)[0]
            self.g = reader.read(1)[0]
            self.r = reader.read(1)[0]
            self.a = 0xFF

        # Set the color directly
        else:
            self.r = r
            self.g = g
            self.b = b
            self.a = a

        if self.r < 0 or self.g < 0 or self.b < 0 or self.a < 0:
            raise ValueError(
                f'Negative color?! R:{self.r}, G:{self.g}, B:{self.b}, A:{self.a}'
            )

    def as_float(self) -> tuple[float, float, float, float]:
        """Converts colors to float values in the range 0.0 - 1.0"""

        return (self.r / 255, self.g / 255, self.b / 255, self.a / 255)

    def __str__(self) -> str:
        return f'BitmapColor: {{ R:{self.r:<3}, G:{self.g:<3}, B:{self.b:<3}, A:{self.a:<3} }}'

    def color_print(self, end: str = '\n') -> None:
        """Draws a square of the color to the console"""

        print(f'\033[48;2;{self.r};{self.g};{self.b}m  \033[0m', end=end)
