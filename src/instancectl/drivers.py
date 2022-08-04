import json
from abc import ABC, abstractmethod
from pathlib import Path


class StorageDriver(ABC):
    @abstractmethod
    def persist(self, obj):
        pass

    @abstractmethod
    def restore(self):
        pass


class FileSystemDriver(StorageDriver):
    def __init__(self, path) -> None:
        super().__init__()
        self._path = Path(path).expanduser()

    def persist(self, obj, *, ensure_ascii=False, indent=2, sort_keys=True):
        with open(self._path, "wt") as fp:
            json.dump(obj, fp, ensure_ascii=ensure_ascii, indent=indent, sort_keys=sort_keys)
            fp.write("\n")  # add trailing newline

    def restore(self):
        with open(self._path) as fp:
            return json.load(fp)
