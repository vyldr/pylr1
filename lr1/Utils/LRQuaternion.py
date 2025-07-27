from typing import TYPE_CHECKING
import math

if TYPE_CHECKING:
    from ..IO.LRBinaryReader import LRBinaryReader


class LRQuaternion:
    w: float
    x: float
    y: float
    z: float

    def __init__(self, q: tuple[float, float, float, float] = (1, 0, 0, 0)) -> None:
        self.w = q[0]
        self.x = q[1]
        self.y = q[2]
        self.z = q[3]

    def read(self, reader: 'LRBinaryReader') -> 'LRQuaternion':
        val: LRQuaternion = LRQuaternion()
        val.w = reader.read_float(True) / 127.0
        val.x = reader.read_float(True) / 127.0
        val.y = reader.read_float(True) / 127.0
        val.z = reader.read_float(True) / 127.0

        return val

    def normalize(self) -> 'LRQuaternion':
        length: float = math.sqrt(self.w**2 + self.x**2 + self.y**2 + self.z**2)
        if length == 0:
            raise ValueError('Cannot normalize a zero-length quaternion')
        self.w = self.w / length
        self.x = self.x / length
        self.y = self.y / length
        self.z = self.z / length

        return self

    def __matmul__(self, vec: tuple[float, float, float]) -> tuple[float, float, float]:
        vx, vy, vz = vec
        qw, qx, qy, qz = self.w, self.x, self.y, self.z

        # Quaternion * Vector as Quaternion
        # Convert vector to quaternion (0, vx, vy, vz)
        # Apply: q * v * q^-1
        # Compute q * v:
        iw = -qx * vx - qy * vy - qz * vz
        ix = qw * vx + qy * vz - qz * vy
        iy = qw * vy + qz * vx - qx * vz
        iz = qw * vz + qx * vy - qy * vx

        # Compute result = (q * v) * q^-1
        # rw = iw * qw - ix * qx - iy * qy - iz * qz
        rx = iw * qx + ix * qw + iy * qz - iz * qy
        ry = iw * qy - ix * qz + iy * qw + iz * qx
        rz = iw * qz + ix * qy - iy * qx + iz * qw

        return (rx, ry, rz)

    def to_tuple(self) -> tuple[float, float, float, float]:
        return (self.w, self.x, self.y, self.z)

    def __str__(self) -> str:
        return f'LRQuaternion: {{W:{self.w}, X:{self.x}, Y:{self.y}, Z:{self.z}}}'

    def __len__(self) -> int:
        return 4

    def __getitem__(self, i: int) -> float:
        match i:
            case 0:
                return self.w
            case 1:
                return self.x
            case 2:
                return self.y
            case 3:
                return self.z
            case _:
                raise IndexError(f'Index out of range: {i}')
