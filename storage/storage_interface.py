from abc import ABC, abstractmethod
from typing import Optional

from models.analysis_result import AnalysisResult


class StorageInterface(ABC):
    @abstractmethod
    def initialize(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def save_input(self, input_text: str, image_path: Optional[str] = None) -> int:
        raise NotImplementedError

    @abstractmethod
    def save_output(self, situation_id: int, result: AnalysisResult) -> int:
        raise NotImplementedError

    @abstractmethod
    def list_analyses(self, limit: int = 20) -> list[dict]:
        raise NotImplementedError

    @abstractmethod
    def get_analysis(self, situation_id: int) -> Optional[dict]:
        raise NotImplementedError
