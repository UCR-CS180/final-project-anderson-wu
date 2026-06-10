import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from models.analysis_result import AnalysisResult
from storage.storage_interface import StorageInterface


class SQLiteStorage(StorageInterface):
    def __init__(self, database_path: str = "data/relationship_summarizer.db") -> None:
        self.database_path = database_path
        self.initialize()

    def initialize(self) -> None:
        try:
            if self.database_path != ":memory:":
                Path(self.database_path).parent.mkdir(parents=True, exist_ok=True)

            with self._connect() as connection:
                connection.execute(
                    """
                    CREATE TABLE IF NOT EXISTS situations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        input_text TEXT NOT NULL,
                        image_path TEXT,
                        created_at TEXT NOT NULL
                    )
                    """
                )
                connection.execute(
                    """
                    CREATE TABLE IF NOT EXISTS ai_outputs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        situation_id INTEGER NOT NULL,
                        summary TEXT NOT NULL,
                        main_issue TEXT,
                        advice TEXT NOT NULL,
                        next_steps TEXT,
                        suggested_message TEXT,
                        risk_flags TEXT,
                        created_at TEXT NOT NULL,
                        FOREIGN KEY (situation_id) REFERENCES situations(id)
                    )
                    """
                )
        except sqlite3.Error as exc:
            raise StorageError(f"Could not initialize SQLite database: {exc}") from exc

    def save_input(self, input_text: str, image_path: Optional[str] = None) -> int:
        try:
            with self._connect() as connection:
                cursor = connection.execute(
                    """
                    INSERT INTO situations (input_text, image_path, created_at)
                    VALUES (?, ?, ?)
                    """,
                    (input_text, image_path, _now_iso()),
                )
                return int(cursor.lastrowid)
        except sqlite3.Error as exc:
            raise StorageError(f"Could not save situation: {exc}") from exc

    def save_output(self, situation_id: int, result: AnalysisResult) -> int:
        try:
            with self._connect() as connection:
                cursor = connection.execute(
                    """
                    INSERT INTO ai_outputs (
                        situation_id,
                        summary,
                        main_issue,
                        advice,
                        next_steps,
                        suggested_message,
                        risk_flags,
                        created_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        situation_id,
                        result.summary,
                        result.main_issue,
                        result.advice,
                        json.dumps(result.next_steps),
                        result.suggested_message,
                        json.dumps(result.risk_flags),
                        _now_iso(),
                    ),
                )
                return int(cursor.lastrowid)
        except sqlite3.Error as exc:
            raise StorageError(f"Could not save AI output: {exc}") from exc

    def list_analyses(self, limit: int = 20) -> list[dict]:
        try:
            with self._connect() as connection:
                rows = connection.execute(
                    """
                    SELECT
                        s.id,
                        s.input_text,
                        s.image_path,
                        s.created_at,
                        o.summary,
                        o.main_issue,
                        o.advice,
                        o.next_steps,
                        o.suggested_message,
                        o.risk_flags
                    FROM situations s
                    LEFT JOIN ai_outputs o ON o.situation_id = s.id
                    ORDER BY s.id DESC
                    LIMIT ?
                    """,
                    (limit,),
                ).fetchall()
                return [self._row_to_record(row) for row in rows]
        except sqlite3.Error as exc:
            raise StorageError(f"Could not retrieve saved analyses: {exc}") from exc

    def get_analysis(self, situation_id: int) -> Optional[dict]:
        try:
            with self._connect() as connection:
                row = connection.execute(
                    """
                    SELECT
                        s.id,
                        s.input_text,
                        s.image_path,
                        s.created_at,
                        o.summary,
                        o.main_issue,
                        o.advice,
                        o.next_steps,
                        o.suggested_message,
                        o.risk_flags
                    FROM situations s
                    LEFT JOIN ai_outputs o ON o.situation_id = s.id
                    WHERE s.id = ?
                    """,
                    (situation_id,),
                ).fetchone()
                return self._row_to_record(row) if row else None
        except sqlite3.Error as exc:
            raise StorageError(f"Could not retrieve saved analysis: {exc}") from exc

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def _row_to_record(self, row: sqlite3.Row) -> dict:
        record = dict(row)
        record["next_steps"] = _loads_list(record.get("next_steps"))
        record["risk_flags"] = _loads_list(record.get("risk_flags"))
        return record


class StorageError(RuntimeError):
    pass


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _loads_list(value: Optional[str]) -> list[str]:
    if not value:
        return []
    try:
        loaded = json.loads(value)
    except json.JSONDecodeError:
        return [value]
    if isinstance(loaded, list):
        return [str(item) for item in loaded]
    return [str(loaded)]
