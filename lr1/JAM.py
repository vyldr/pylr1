
from io import BytesIO
import os
import struct


class JAM:

    jam_file_name: str
    folders: list[tuple[str, int]] = []
    file_paths_list: list[tuple[str, int, int]] = []
    file_map: dict[str, tuple[int, int]]
    JAM_file: bytes

    def __init__(self, jam_file_name: str) -> None:
        self.jam_file_name = jam_file_name

        self.file_map = {}

        self.read_jam(self.jam_file_name)

    # Find and return the binary data corresponding to the provided internal file path
    def extract_file(self, file_path: str) -> BytesIO:
        # Make sure the file exists
        if file_path not in self.file_map:
            raise FileNotFoundError(
                f'File: {file_path} not in {self.jam_file_name}')

        file_pointer: int = self.file_map[file_path][0]
        file_size: int = self.file_map[file_path][1]
        file = BytesIO(self.JAM_file[file_pointer:file_pointer + file_size])
        return file

    # Make it easy to find a file pointer
    def generate_file_map(self):
        for file in self.file_paths_list:
            self.file_map[file[0]] = (file[1], file[2])

    # Pull an integer out of the jam
    def read_uint32(self, offset: int) -> int:
        return struct.unpack('<i', self.JAM_file[offset:offset + 4])[0]

    # Read 12 bytes and remove the trailing nulls
    def read_string(self, offset: int) -> str:
        data: bytes = self.JAM_file[offset:offset + 12]
        return data.decode().strip('\x00')

    def list_folders(self, offset: int, number: int, folder_path: str) -> list[tuple[str, int]]:
        folder_list: list[tuple[str, int]] = []

        for _ in range(number):
            # Read in the folder name
            name: str = folder_path
            name += self.read_string(offset)

            position: int = self.read_uint32(offset + 12)

            folder_list.append((name, position))
            offset += 16

        return folder_list

    def list_files(self, offset: int, number: int, folder_path: str) -> list[tuple[str, int, int]]:
        file_list: list[tuple[str, int, int]] = []

        for _ in range(number):
            # Read in the file name
            name: str = folder_path + os.sep
            name += self.read_string(offset)

            position: int = self.read_uint32(offset + 12)
            size: int = self.read_uint32(offset + 16)

            file_list.append((name, position, size))
            offset += 20

        return file_list

    def recurse(self, folders_list: list[tuple[str, int]]):
        self.folders.extend(folders_list)

        for f in folders_list:
            total_files = self.read_uint32(f[1])

            if total_files == 0:  # Only contains folders
                self.recurse(self.list_folders(
                    f[1] + 8, self.read_uint32(f[1] + 4), f[0] + os.sep))

            else:
                # Add files to the list
                self.file_paths_list.extend(self.list_files(
                    f[1] + 4, self.read_uint32(f[1]), f[0]))

                # Check for subfolders
                folder_count_position: int = total_files * 20 + f[1] + 4
                folder_count: int = self.read_uint32(folder_count_position)
                if folder_count > 0:
                    self.recurse(self.list_folders(
                        folder_count_position + 4, folder_count, f[0] + os.sep))

    def read_jam(self, jam_file_path: str) -> None:
        with open(jam_file_path, 'rb') as file:
            self.JAM_file = file.read()

        # Make sure this is really a JAM file
        if len(self.JAM_file) < 4 or self.JAM_file[0:4] != b'LJAM':
            raise AssertionError('Not a JAM file')

        # Recursively create a list of all files
        self.recurse([('', 4)])

        # Generate the file map so we can look up files by name
        self.generate_file_map()
