from io import BytesIO
import os
import struct
import pathlib


class JamItem:
    """
    A file or directory in the JAM file.

    Attributes:
        path (pathlib.Path): The file path within the JAM file
        data (BytesIO): The binary content of the file
        pointer(int): The index of the first byte of the file
        size (int): The size of the file in bytes
        is_directory (bool): Whether this is a directory instead of a file
        directory_contents (list[JamItem]): List of contained items, if a directory
        parent (JamItem): The parent directory
        jam (JAM): The containing JAM file
    """

    path: pathlib.Path
    _data: BytesIO | None
    jam: 'JAM'
    pointer: int
    size: int
    is_directory: bool
    directory_contents: list['JamItem']
    parent: 'JamItem'

    def __init__(
        self, path: str, jam: 'JAM', pointer: int, size: int, directory: bool = False
    ) -> None:
        self.path = pathlib.Path(path).resolve()
        self._data = None
        self.jam = jam
        self.pointer = pointer
        self.size = size
        self.is_directory = directory
        self.directory_contents = []

    @property
    def data(self) -> BytesIO:
        if self._data is None:
            self._data = BytesIO(self.jam.data[self.pointer : self.pointer + self.size])

        return self._data

    def __str__(self) -> str:
        return (
            f'{"Directory" if self.is_directory else "File"}: {{'
            f'Path: {str(self.path)}, '
            f'Position: {hex(self.pointer)}, '
            f'{f"Items: {len(self.directory_contents)}" if self.is_directory else f"Size: {self.size}"}'
            f'}}'
        )

    def reset(self) -> None:
        """Reset the seek position"""
        self.data.seek(0)


class JAM:
    """
    A JAM file

    Attributes:
        path (pathlib.Path): Filepath of the JAM
        directories (list[JamItem]): List of directories within the JAM
        files (list[JamItem]): List of files within the JAM
        file_map (dict[str, JamItem]): Dictionary of contained files and directories for access by internal path strings
        root (JamItem): The internal root directory
        JAM_file (bytes): The binary data of the file
    """

    path: pathlib.Path
    directories: list[JamItem]
    files: list[JamItem]
    file_map: dict[str, JamItem]
    root: JamItem
    data: bytes

    def __init__(self, jam_file_name: str) -> None:
        self.path = pathlib.Path(jam_file_name)

        self.directories = []
        self.files = []
        self.file_map = {}

        self.read_jam(self.path)

    def extract_file(self, file_path: str) -> JamItem:
        """Find and return the file or directory corresponding to the provided internal file path"""

        # Make sure the file exists
        if file_path not in self.file_map:
            raise FileNotFoundError(f'File: {file_path} not in {self.path}')

        return self.file_map[file_path]

    def generate_file_map(self) -> None:
        """Make it easy to find a file pointer"""

        for file in (*self.files, *self.directories):
            self.file_map[str(file.path)] = file

    def build_directory_tree(self) -> None:
        """Organize the files into a navigable tree"""

        for file in (*self.files, *self.directories):
            file.parent = self.file_map[str(file.path.parent)]
            file.parent.directory_contents.append(file)
            if str(file.path) == '/':
                self.root = file

    def read_uint32(self, offset: int) -> int:
        """Pull an integer out of the jam"""

        return int(struct.unpack('<i', self.data[offset : offset + 4])[0])

    def read_string(self, offset: int) -> str:
        """Read 12 bytes and remove the trailing null characters"""

        data: bytes = self.data[offset : offset + 12]
        return data.decode().strip('\x00')

    def list_directories(
        self, offset: int, number: int, directory_path: str
    ) -> list[JamItem]:
        directory_list: list[JamItem] = []

        for _ in range(number):
            # Read in the directory name
            name: str = directory_path
            name += self.read_string(offset)

            position: int = self.read_uint32(offset + 12)

            directory_list.append(JamItem(name, self, position, 0, directory=True))
            offset += 16

        return directory_list

    def list_files(
        self, offset: int, number: int, directory_path: str
    ) -> list[JamItem]:
        file_list: list[JamItem] = []

        for _ in range(number):
            # Read in the file name
            name: str = directory_path + os.sep
            name += self.read_string(offset)

            position: int = self.read_uint32(offset + 12)
            size: int = self.read_uint32(offset + 16)

            file_list.append(JamItem(name, self, position, size))
            offset += 20

        return file_list

    def recurse(self, directories_list: list[JamItem]) -> None:
        self.directories.extend(directories_list)

        for f in directories_list:
            total_files = self.read_uint32(f.pointer)

            if total_files == 0:  # Only contains directories
                self.recurse(
                    self.list_directories(
                        f.pointer + 8,
                        self.read_uint32(f.pointer + 4),
                        str(f.path) + os.sep,
                    )
                )

            else:
                # Add files to the list
                self.files.extend(
                    self.list_files(
                        f.pointer + 4, self.read_uint32(f.pointer), str(f.path)
                    )
                )

                # Check for subdirectories
                directory_count_position: int = total_files * 20 + f.pointer + 4
                directory_count: int = self.read_uint32(directory_count_position)
                if directory_count > 0:
                    self.recurse(
                        self.list_directories(
                            directory_count_position + 4,
                            directory_count,
                            str(f.path) + os.sep,
                        )
                    )

    def read_jam(self, jam_file_path: pathlib.Path) -> None:
        with open(jam_file_path, 'rb') as file:
            self.data = file.read()

        # Make sure this is really a JAM file
        if len(self.data) < 4 or self.data[0:4] != b'LJAM':
            raise AssertionError('Not a JAM file')

        # Recursively create a list of all files
        self.recurse([JamItem(os.sep, self, pointer=4, size=0, directory=True)])

        # Build structures for file access
        self.generate_file_map()
        self.build_directory_tree()
