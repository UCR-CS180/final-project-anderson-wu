from pathlib import Path
from typing import Optional

from models.analysis_result import AnalysisResult
from services.situation_service import SituationService


MIN_SITUATION_LENGTH = 20


def validate_situation_text(text: str) -> str:
    cleaned = text.strip()
    if not cleaned:
        raise ValueError("Situation description cannot be empty.")
    if len(cleaned) < MIN_SITUATION_LENGTH:
        raise ValueError(
            f"Please enter at least {MIN_SITUATION_LENGTH} characters so the app has enough context."
        )
    return cleaned


class RelationshipCLI:
    def __init__(self, service: SituationService) -> None:
        self.service = service

    def run(self) -> None:
        self._print_welcome()
        try:
            while True:
                self._handle_analysis()
                if not self._handle_next_action_menu():
                    break
        except KeyboardInterrupt:
            print("\nExiting. Take care.")

    def _print_welcome(self) -> None:
        print("AI Relationship Summarizer")
        print("Describe a relationship situation, and the app will summarize it and suggest practical next steps.")
        print("This is not therapy, legal advice, or emergency support.\n")

    def _handle_analysis(self) -> None:
        situation_text = self._prompt_for_situation()
        image_path = self._prompt_for_image_path()

        print("\nAnalyzing...\n")
        try:
            result = self.service.analyze_situation(situation_text, image_path)
        except Exception as exc:
            print(f"Sorry, the analysis could not be completed: {exc}")
            return

        print(result.to_display_string())
        print()

    def _prompt_for_situation(self) -> str:
        while True:
            print("Describe your relationship situation.")
            print("Press Enter on a blank line when finished.")
            raw_text = self._read_multiline_input()
            try:
                return validate_situation_text(raw_text)
            except ValueError as exc:
                print(f"\n{exc}\n")

    def _read_multiline_input(self) -> str:
        lines: list[str] = []
        while True:
            line = input("> ")
            if line == "":
                break
            lines.append(line)
        return "\n".join(lines)

    def _prompt_for_image_path(self) -> Optional[str]:
        raw_path = input("Optional image/screenshot path (press Enter to skip): ").strip()
        if not raw_path:
            return None

        cleaned_path = raw_path.strip('"').strip("'")
        image_path = Path(cleaned_path).expanduser()
        if not image_path.exists():
            print("Warning: image path was not found. Continuing with text-only analysis.")
            return None

        print("Image path saved. This version still analyzes the situation text only.")
        return str(image_path.resolve())

    def _handle_next_action_menu(self) -> bool:
        while True:
            print("What would you like to do next?")
            print("1. Analyze another situation")
            print("2. View past saved analyses")
            print("3. Exit")
            choice = input("> ").strip()

            if choice == "1":
                print()
                return True
            if choice == "2":
                print()
                self._show_history()
                continue
            if choice == "3":
                print("Exiting. Take care.")
                return False

            print("Please choose 1, 2, or 3.\n")

    def _show_history(self) -> None:
        try:
            history = self.service.get_history()
        except Exception as exc:
            print(f"Could not load saved analyses: {exc}\n")
            return

        if not history:
            print("No saved analyses yet.\n")
            return

        print("Past Saved Analyses")
        for item in history:
            summary = item.get("summary") or "No summary saved"
            preview = summary[:77] + "..." if len(summary) > 80 else summary
            print(f"{item['id']}. {item['created_at']} - {preview}")

        selected = input("\nEnter an analysis ID to view details, or press Enter to return: ").strip()
        if not selected:
            print()
            return
        if not selected.isdigit():
            print("Please enter a numeric analysis ID.\n")
            return

        record = self.service.get_analysis(int(selected))
        if record is None:
            print("No saved analysis found with that ID.\n")
            return

        self._display_saved_analysis(record)

    def _display_saved_analysis(self, record: dict) -> None:
        print("\n=== Original Situation ===")
        print(record["input_text"])
        if record.get("image_path"):
            print(f"\nSaved image path: {record['image_path']}")

        result = AnalysisResult.from_dict(record)
        print()
        print(result.to_display_string())
        print()
