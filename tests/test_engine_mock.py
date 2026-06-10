import json

from engine.relationship_engine import RelationshipEngine
from models.analysis_result import AnalysisResult


class FakeResponse:
    def __init__(self, text: str) -> None:
        self.text = text


class FakeModels:
    def __init__(self, response_text: str) -> None:
        self.response_text = response_text
        self.calls = []

    def generate_content(self, model: str, contents: str, config) -> FakeResponse:
        self.calls.append({"model": model, "contents": contents, "config": config})
        return FakeResponse(self.response_text)


class FakeClient:
    def __init__(self, response_text: str) -> None:
        self.models = FakeModels(response_text)


def test_engine_returns_analysis_result_from_mock_gemini_response() -> None:
    response_text = json.dumps(
        {
            "summary": "It sounds like the user feels dismissed during disagreements.",
            "main_issue": "Communication and validation.",
            "advice": "Ask for a calmer conversation and describe the impact without blaming.",
            "next_steps": ["Name the feeling", "Ask for a time to talk", "Listen for their view"],
            "suggested_message": "I feel hurt when our talks turn sharp, and I would like us to reset.",
            "risk_flags": [],
        }
    )
    fake_client = FakeClient(response_text)
    engine = RelationshipEngine(api_key="test-key", client=fake_client)

    result = engine.analyze("My partner shuts down during conflict and I feel ignored.")

    assert isinstance(result, AnalysisResult)
    assert result.summary.startswith("It sounds like")
    assert result.next_steps == ["Name the feeling", "Ask for a time to talk", "Listen for their view"]
    assert fake_client.models.calls[0]["model"] == "gemini-2.5-flash"


def test_engine_handles_malformed_json_safely() -> None:
    fake_client = FakeClient("This is not valid JSON")
    engine = RelationshipEngine(api_key="test-key", client=fake_client)

    result = engine.analyze("My partner and I keep misunderstanding each other after arguments.")

    assert isinstance(result, AnalysisResult)
    assert "could not be parsed" in result.summary
    assert result.risk_flags
