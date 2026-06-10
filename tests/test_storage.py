from models.analysis_result import AnalysisResult
from storage.sqlite_storage import SQLiteStorage


def test_database_initializes(tmp_path) -> None:
    database_path = tmp_path / "relationship_summarizer.db"
    SQLiteStorage(str(database_path))
    assert database_path.exists()


def test_save_input_works(tmp_path) -> None:
    storage = SQLiteStorage(str(tmp_path / "relationship_summarizer.db"))
    situation_id = storage.save_input("This is a valid relationship situation.")
    assert situation_id == 1


def test_save_output_works(tmp_path) -> None:
    storage = SQLiteStorage(str(tmp_path / "relationship_summarizer.db"))
    situation_id = storage.save_input("This is a valid relationship situation.")
    result = AnalysisResult(
        summary="They are having a conflict about communication.",
        main_issue="Communication mismatch.",
        advice="Use a calm I feel statement.",
        next_steps=["Pause before replying", "Ask for a specific time to talk"],
        suggested_message="I feel disconnected and would like to talk.",
        risk_flags=[],
    )

    output_id = storage.save_output(situation_id, result)
    saved = storage.get_analysis(situation_id)

    assert output_id == 1
    assert saved is not None
    assert saved["summary"] == result.summary
    assert saved["next_steps"] == result.next_steps


def test_retrieve_history_works(tmp_path) -> None:
    storage = SQLiteStorage(str(tmp_path / "relationship_summarizer.db"))
    situation_id = storage.save_input("This is a valid relationship situation.")
    storage.save_output(
        situation_id,
        AnalysisResult(
            summary="A short summary.",
            main_issue="A main issue.",
            advice="Calm advice.",
            next_steps=["Step one"],
            suggested_message="I feel hurt when this happens.",
            risk_flags=["No immediate danger described."],
        ),
    )

    history = storage.list_analyses()

    assert len(history) == 1
    assert history[0]["id"] == situation_id
    assert history[0]["risk_flags"] == ["No immediate danger described."]
