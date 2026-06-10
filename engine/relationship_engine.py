import json
from typing import Any, Optional

from engine.prompts import build_relationship_prompt
from models.analysis_result import AnalysisResult


class RelationshipEngine:
    def __init__(
        self,
        api_key: Optional[str],
        model: str = "gemini-2.5-flash",
        client: Optional[Any] = None,
    ) -> None:
        self.api_key = api_key
        self.model = model
        self.client = client

    def analyze(self, user_text: str, image_path: Optional[str] = None) -> AnalysisResult:
        cleaned_text = user_text.strip()
        if not cleaned_text:
            return self._safe_result(
                summary="Analysis could not run because the situation text was empty.",
                main_issue="Missing input.",
                advice="Please describe the situation with enough detail and try again.",
                next_steps=["Enter at least 20 characters of context.", "Run the analysis again."],
            )

        prompt = build_relationship_prompt(cleaned_text, image_path)

        try:
            raw_response = self._request_analysis(prompt)
        except MissingApiKeyError:
            return self._safe_result(
                summary="Analysis could not run because the Gemini API key is missing.",
                main_issue="Missing API configuration.",
                advice="Create a .env file from .env.example and add your real Gemini API key.",
                next_steps=[
                    "Copy .env.example to .env.",
                    "Add your Gemini API key to .env.",
                    "Run python main.py again.",
                ],
            )
        except ImportError:
            return self._safe_result(
                summary="Analysis could not run because the Google GenAI SDK is not installed.",
                main_issue="Missing Python dependency.",
                advice="Install the project dependencies with pip install -r requirements.txt.",
                next_steps=["Activate your virtual environment.", "Run pip install -r requirements.txt."],
            )
        except Exception as exc:
            return self._safe_result(
                summary="Analysis could not be completed because the Gemini request failed.",
                main_issue="Gemini API failure.",
                advice=f"Try again later, check your API key, or verify the configured model. Details: {exc}",
                next_steps=["Check your .env settings.", "Confirm your internet connection.", "Try again."],
            )

        return self._parse_response(raw_response)

    def _request_analysis(self, prompt: str) -> str:
        client = self._get_client()
        config = self._json_generation_config()
        response = client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=config,
        )
        return self._extract_response_text(response)

    def _get_client(self) -> Any:
        if self.client is not None:
            return self.client

        if not self.api_key or not self.api_key.strip():
            raise MissingApiKeyError()

        from google import genai

        self.client = genai.Client(api_key=self.api_key)
        return self.client

    def _json_generation_config(self) -> Any:
        try:
            from google.genai import types

            return types.GenerateContentConfig(response_mime_type="application/json")
        except ImportError:
            return {"response_mime_type": "application/json"}

    def _extract_response_text(self, response: Any) -> str:
        direct_text = getattr(response, "text", None)
        if direct_text:
            return str(direct_text)

        try:
            candidates = getattr(response, "candidates", []) or []
            parts = candidates[0].content.parts
            text_parts = [getattr(part, "text", "") for part in parts]
            combined = "".join(text_parts).strip()
            if combined:
                return combined
        except Exception:
            pass

        return str(response)

    def _parse_response(self, raw_response: str) -> AnalysisResult:
        data = self._load_json(raw_response)
        if data is None:
            return self._safe_result(
                summary="The AI response could not be parsed into the expected JSON format.",
                main_issue="Invalid model response.",
                advice="Please try again. If this keeps happening, use a simpler situation description or check the configured Gemini model.",
                next_steps=["Try the analysis again.", "Check that GEMINI_MODEL is set correctly."],
                risk_flags=["The model response was malformed, so no reliable risk assessment was completed."],
            )

        return AnalysisResult.from_dict(data)

    def _load_json(self, raw_response: str) -> Optional[dict]:
        cleaned = self._strip_code_fence(raw_response.strip())

        try:
            loaded = json.loads(cleaned)
            return loaded if isinstance(loaded, dict) else None
        except json.JSONDecodeError:
            pass

        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start == -1 or end == -1 or end <= start:
            return None

        try:
            loaded = json.loads(cleaned[start : end + 1])
            return loaded if isinstance(loaded, dict) else None
        except json.JSONDecodeError:
            return None

    def _strip_code_fence(self, text: str) -> str:
        if not text.startswith("```"):
            return text

        lines = text.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        return "\n".join(lines).strip()

    def _safe_result(
        self,
        summary: str,
        main_issue: str,
        advice: str,
        next_steps: Optional[list[str]] = None,
        suggested_message: str = "",
        risk_flags: Optional[list[str]] = None,
    ) -> AnalysisResult:
        return AnalysisResult(
            summary=summary,
            main_issue=main_issue,
            advice=advice,
            next_steps=next_steps or [],
            suggested_message=suggested_message,
            risk_flags=risk_flags or [],
        )


class MissingApiKeyError(Exception):
    pass
