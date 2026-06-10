from typing import Optional

from engine.relationship_engine import RelationshipEngine
from models.analysis_result import AnalysisResult
from storage.storage_interface import StorageInterface


class SituationService:
    def __init__(self, engine: RelationshipEngine, storage: StorageInterface) -> None:
        self.engine = engine
        self.storage = storage

    def analyze_situation(self, input_text: str, image_path: Optional[str] = None) -> AnalysisResult:
        situation_id = self.storage.save_input(input_text, image_path)
        result = self.engine.analyze(input_text, image_path)
        self.storage.save_output(situation_id, result)
        return result

    def get_history(self, limit: int = 20) -> list[dict]:
        return self.storage.list_analyses(limit)

    def get_analysis(self, situation_id: int) -> Optional[dict]:
        return self.storage.get_analysis(situation_id)
