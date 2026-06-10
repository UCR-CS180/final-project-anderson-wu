# AI Relationship Summarizer Requirements and Design

## 1. Project Overview

AI Relationship Summarizer is a local terminal-based Python application. The user enters a written relationship situation involving their partner, and the app uses the Google Gemini API to generate a clear summary, identify the main issue, provide practical next-step advice, optionally suggest a message the user can send, and flag possible safety risks.

The application is designed for educational use. It is not a replacement for therapy, legal advice, emergency services, or professional support.

## 2. Goals

- Provide a simple terminal workflow for entering a relationship situation.
- Use Gemini to create a calm, balanced, non-diagnostic analysis.
- Store the original situation and AI result locally in SQLite.
- Allow the user to view past saved analyses.
- Maintain clear separation between interface, engine, storage, and service layers.
- Avoid hardcoded API keys by loading configuration from environment variables.

## 3. Stakeholders and Users

Primary user:

- A person who wants help summarizing a relationship situation and thinking through practical next steps.

Developer or maintainer:

- A student or reviewer who needs to understand, run, test, and evaluate the project.

## 4. Functional Requirements

### FR1: Terminal Input

The app shall welcome the user and prompt them to describe a relationship situation.

### FR2: Input Validation

The app shall reject empty input.

The app shall reject situation text shorter than 20 characters.

### FR3: Optional Image Path

The app shall ask the user whether they want to provide an optional image or screenshot path.

If the path is empty, the app shall continue with text-only analysis.

If the path does not exist, the app shall warn the user and continue with text-only analysis.

### FR4: AI Analysis

The app shall send the validated text to the engine layer.

The engine shall call the Google Gemini API using the official Google GenAI Python SDK.

The engine shall request structured JSON output from Gemini.

The engine shall return an `AnalysisResult` object with these fields:

- `summary`
- `main_issue`
- `advice`
- `next_steps`
- `suggested_message`
- `risk_flags`

### FR5: Safety and Risk Flags

The prompt shall instruct Gemini to flag signs of abuse, threats, violence, self-harm, coercion, stalking, or danger.

When risk signs are present, the advice should encourage the user to contact trusted people or appropriate professional or emergency support.

### FR6: Local Storage

The app shall save the original input text, optional image path, timestamp, and AI output in SQLite.

The app shall store `next_steps` and `risk_flags` as JSON strings in SQLite.

### FR7: History Viewing

The app shall provide a terminal menu option to view past saved analyses.

The app shall allow the user to select a saved analysis by ID and display the original situation and AI result.

### FR8: Repeated Use

After each analysis, the app shall let the user analyze another situation, view history, or exit.

## 5. Non-Functional Requirements

### NFR1: Layer Separation

The interface layer shall handle terminal input and output only.

The engine layer shall handle prompt construction, Gemini API calls, response parsing, and `AnalysisResult` creation only.

The storage layer shall handle SQLite setup, saving, and retrieval only.

The service layer shall coordinate the interface, engine, and storage layers.

### NFR2: Security

The app shall load `GEMINI_API_KEY` from `.env`.

The app shall not hardcode API keys in Python files.

The `.env` file shall be excluded from version control.

### NFR3: Simplicity

The app shall use a simple beginner-friendly Python design.

The app shall not use web frameworks, Docker, Firebase, Supabase, or deployment tooling.

### NFR4: Reliability

The app shall handle normal user mistakes without crashing.

The app shall provide safe fallback output if the Gemini API fails or returns invalid JSON.

## 6. System Architecture

The architecture uses four main layers.

```text
Terminal User
    |
    v
Interface Layer
interface/cli.py
    |
    v
Service Layer
services/situation_service.py
    |
    +--> Engine Layer
    |    engine/relationship_engine.py
    |    engine/prompts.py
    |    engine/schemas.py
    |
    +--> Storage Layer
         storage/sqlite_storage.py
         storage/storage_interface.py
```

## 7. Layer Responsibilities

### Interface Layer

Files:

- `interface/cli.py`

Responsibilities:

- Print welcome text.
- Read user input.
- Validate empty or too-short input.
- Ask for optional image path.
- Display analysis output.
- Display the menu for analyze again, view saved analyses, or exit.

The interface layer does not call Gemini directly and does not write directly to SQLite.

### Engine Layer

Files:

- `engine/relationship_engine.py`
- `engine/prompts.py`
- `engine/schemas.py`

Responsibilities:

- Build the Gemini prompt.
- Call Gemini using the official Google GenAI SDK.
- Request JSON output.
- Parse model responses.
- Return an `AnalysisResult`.
- Provide safe fallback responses for missing API keys, API failures, missing dependencies, or malformed model output.

The engine layer does not read terminal input, print terminal output, or save to SQLite.

### Storage Layer

Files:

- `storage/storage_interface.py`
- `storage/sqlite_storage.py`

Responsibilities:

- Initialize the SQLite database.
- Create `situations` and `ai_outputs` tables.
- Save user input.
- Save AI output.
- Retrieve saved analyses.
- Retrieve one analysis by ID.

The storage layer does not call Gemini and does not build prompts.

### Service Layer

Files:

- `services/situation_service.py`

Responsibilities:

- Receive validated input from the CLI.
- Save the user situation through the storage layer.
- Call the engine layer.
- Save the AI output through the storage layer.
- Return the result to the CLI.

## 8. Data Model

The main application model is `AnalysisResult`.

File:

- `models/analysis_result.py`

Fields:

- `summary: str`
- `main_issue: str`
- `advice: str`
- `next_steps: list[str]`
- `suggested_message: str`
- `risk_flags: list[str]`

Helper methods:

- `to_dict()`
- `from_dict()`
- `to_display_string()`

## 9. Database Design

Database:

- SQLite

Default path:

- `data/relationship_summarizer.db`

### Table: situations

| Column | Type | Description |
| --- | --- | --- |
| `id` | INTEGER PRIMARY KEY AUTOINCREMENT | Unique situation ID |
| `input_text` | TEXT NOT NULL | Original user situation |
| `image_path` | TEXT | Optional image path |
| `created_at` | TEXT NOT NULL | Timestamp |

### Table: ai_outputs

| Column | Type | Description |
| --- | --- | --- |
| `id` | INTEGER PRIMARY KEY AUTOINCREMENT | Unique output ID |
| `situation_id` | INTEGER NOT NULL | Related situation ID |
| `summary` | TEXT NOT NULL | AI summary |
| `main_issue` | TEXT | Main issue |
| `advice` | TEXT NOT NULL | Practical advice |
| `next_steps` | TEXT | JSON string list |
| `suggested_message` | TEXT | Suggested message |
| `risk_flags` | TEXT | JSON string list |
| `created_at` | TEXT NOT NULL | Timestamp |

## 10. AI Prompt Design

The prompt instructs Gemini to act as a calm relationship summarizer and advisor, not a therapist.

Prompt rules include:

- Do not diagnose the user or partner with mental illnesses.
- Do not claim certainty about the partner's intention.
- Do not encourage manipulation, revenge, stalking, coercion, or emotional games.
- Give grounded, calm, practical advice.
- Use careful wording such as "It sounds like..." and "One possible interpretation is..."
- Include safety flags when the situation suggests abuse, threats, self-harm, coercion, stalking, or danger.
- Make clear that the output is not professional therapy or legal advice.
- Use valid JSON only.

Expected JSON shape:

```json
{
  "summary": "...",
  "main_issue": "...",
  "advice": "...",
  "next_steps": ["...", "...", "..."],
  "suggested_message": "...",
  "risk_flags": ["..."]
}
```

## 11. Error Handling

The app handles:

- Missing Gemini API key.
- Missing Google GenAI dependency.
- Gemini API failure.
- Invalid or malformed model JSON.
- Empty input.
- Input shorter than 20 characters.
- Missing image file path.
- SQLite errors.

Normal user mistakes should produce readable messages instead of uncaught crashes.

## 12. Testing Plan

Tests are located in:

- `tests/`

Test files:

- `tests/test_cli_validation.py`
- `tests/test_storage.py`
- `tests/test_engine_mock.py`

Covered behavior:

- Empty input fails validation.
- Too-short input fails validation.
- Valid input passes validation.
- SQLite database initializes.
- User input saves correctly.
- AI output saves correctly.
- Saved history can be retrieved.
- Gemini response can be mocked.
- Engine returns an `AnalysisResult`.
- Malformed Gemini JSON is handled safely.

Tests do not call the real Gemini API.

## 13. Setup and Execution Summary

Install dependencies:

```bash
pip install -r requirements.txt
```

Create `.env` from `.env.example`, then add a real Gemini API key.

Run the app:

```bash
python main.py
```

Run tests:

```bash
pytest
```

## 14. Limitations and Future Work

- Image path support is currently saved for record keeping, but image contents are not analyzed.
- The app is terminal-only.
- The app stores data locally without encryption.
- Future work could include real multimodal image analysis, editing or deleting saved analyses, and export features.
