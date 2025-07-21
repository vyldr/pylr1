from typing import IO
import types

from abc import ABC, abstractmethod
import pathlib
from io import FileIO


class LRFile(ABC):
    """
    Base class for LR files.

    Attributes:
        path (pathlib.Path): The file path
        data (IO[bytes]): The binary content of the file
        is_directory (bool): Whether this is a directory instead of a file
        directory_contents (list[LRFile]): List of contained files, if a directory
        parent (LRFile): The parent directory
    """

    path: pathlib.Path
    _data: IO[bytes] | None
    is_directory: bool
    _directory_contents: list['LRFile'] | None
    _parent: 'LRFile | None'

    @property
    @abstractmethod
    def data(self) -> IO[bytes]:
        """Return the file data as a byte stream"""
        pass

    def reset(self) -> None:
        """Reset the seek position"""
        self.data.seek(0)

    @abstractmethod
    def scan_directory(self) -> list['LRFile']:
        """Scan the directory and return a list of contained files"""
        pass

    @abstractmethod
    def get_file(self, path: pathlib.Path) -> 'LRFile':
        """Get a file by name from the directory"""
        pass

    @property
    def directory_contents(self) -> list['LRFile']:
        if not self.is_directory:
            raise NotADirectoryError(f'{self.path} is not a directory')
        elif self._directory_contents is None:
            self._directory_contents = self.scan_directory()
        return self._directory_contents

    def __enter__(self) -> 'LRFile':
        return self

    def __exit__(
        self, exc_type: type, exc_value: Exception, traceback: types.TracebackType
    ) -> None:
        """Close the file if it is open"""
        if self._data is not None:
            self._data.close()
            self._data = None


class LRFileItem(LRFile):
    """
    A file or directory on the filesystem.
    """

    files_dict: dict[pathlib.Path, 'LRFileItem'] = {}

    def __init__(
        self, path: str | pathlib.Path, parent: 'LRFileItem | None' = None
    ) -> None:
        # Make a real path object
        if isinstance(path, str):
            self.path = pathlib.Path(path).resolve()
        else:
            self.path = path.resolve()

        # Check if the file exists
        if not self.path.exists():
            raise FileNotFoundError(f'File not found: {self.path}')

        # Check if the path is a directory
        self.is_directory = self.path.is_dir()

        self._data = None
        self._parent = None
        self._directory_contents = None

    @property
    def data(self) -> IO[bytes]:
        if self._data is None:
            self._data = FileIO(self.path, 'rb')

        return self._data

    @property
    def parent(self) -> 'LRFile':
        if self._parent is None:
            parent_path = self.path.parent
            if parent_path != self.path:
                self._parent = LRFileItem(parent_path)
            else:
                self._parent = self
        return self._parent

    def scan_directory(self) -> list['LRFile']:
        """Scan the directory and update the contents"""
        if not self.is_directory:
            raise NotADirectoryError(f'{self.path} is not a directory')
        return [LRFileItem(item, self) for item in self.path.iterdir()]

    def get_file(self, path: pathlib.Path) -> 'LRFile':
        # Resolve the path
        path = path.resolve()

        # Check if the file is already loaded
        if path in LRFileItem.files_dict:
            return LRFileItem.files_dict[path]

        # Open the file
        new_file: 'LRFileItem' = LRFileItem(path)
        LRFileItem.files_dict[path] = new_file

        return new_file
