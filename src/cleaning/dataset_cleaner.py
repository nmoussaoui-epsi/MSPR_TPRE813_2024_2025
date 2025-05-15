from abc import ABC, abstractmethod
from pathlib import Path


class DatasetCleaner(ABC):
    def __init__(self, input_dir: Path, output_file: Path):
        self.input_dir = input_dir
        self.output_file = output_file

    @abstractmethod
    def run(self) -> None:
        pass

    def _log(self, message: str) -> None:
        print(f"[{self.__class__.__name__}] {message}")
