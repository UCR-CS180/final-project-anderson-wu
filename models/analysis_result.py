import json
from dataclasses import dataclass, field
from typing import Any


@dataclass
class AnalysisResult:
    summary: str
    main_issue: str
    advice: str
    next_steps: list[str] = field(default_factory=list)
    suggested_message: str = ""
    risk_flags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "main_issue": self.main_issue,
            "advice": self.advice,
            "next_steps": list(self.next_steps),
            "suggested_message": self.suggested_message,
            "risk_flags": list(self.risk_flags),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AnalysisResult":
        return cls(
            summary=str(data.get("summary") or ""),
            main_issue=str(data.get("main_issue") or ""),
            advice=str(data.get("advice") or ""),
            next_steps=_coerce_list(data.get("next_steps")),
            suggested_message=str(data.get("suggested_message") or ""),
            risk_flags=_coerce_list(data.get("risk_flags")),
        )

    def to_display_string(self) -> str:
        next_steps = self._format_numbered_list(self.next_steps, "No specific next steps suggested.")
        risk_flags = self._format_plain_list(self.risk_flags, "None identified.")
        suggested_message = self.suggested_message or "No suggested message provided."

        return "\n".join(
            [
                "=== Situation Summary ===",
                self.summary,
                "",
                "=== Main Issue ===",
                self.main_issue,
                "",
                "=== Advice ===",
                self.advice,
                "",
                "=== Next Steps ===",
                next_steps,
                "",
                "=== Suggested Message ===",
                suggested_message,
                "",
                "=== Safety / Risk Flags ===",
                risk_flags,
            ]
        )

    def _format_numbered_list(self, values: list[str], empty_message: str) -> str:
        cleaned_values = [value for value in values if value.strip()]
        if not cleaned_values:
            return empty_message
        return "\n".join(f"{index}. {value}" for index, value in enumerate(cleaned_values, start=1))

    def _format_plain_list(self, values: list[str], empty_message: str) -> str:
        cleaned_values = [value for value in values if value.strip()]
        if not cleaned_values:
            return empty_message
        return "\n".join(cleaned_values)


def _coerce_list(value: Any) -> list[str]:
    if value is None:
        return []

    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]

    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            return []

        try:
            loaded = json.loads(stripped)
        except json.JSONDecodeError:
            return [stripped]

        if isinstance(loaded, list):
            return [str(item).strip() for item in loaded if str(item).strip()]
        return [stripped]

    return [str(value).strip()] if str(value).strip() else []
