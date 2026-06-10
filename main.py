import os

from dotenv import load_dotenv

from engine.relationship_engine import RelationshipEngine
from interface.cli import RelationshipCLI
from services.situation_service import SituationService
from storage.sqlite_storage import SQLiteStorage


def build_app() -> RelationshipCLI:
    load_dotenv()

    database_path = os.getenv("DATABASE_PATH", "data/relationship_summarizer.db")
    api_key = os.getenv("GEMINI_API_KEY")
    model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    storage = SQLiteStorage(database_path)
    engine = RelationshipEngine(api_key=api_key, model=model)
    service = SituationService(engine=engine, storage=storage)
    return RelationshipCLI(service)


def main() -> None:
    app = build_app()
    app.run()


if __name__ == "__main__":
    main()
