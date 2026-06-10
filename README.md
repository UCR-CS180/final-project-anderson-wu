# AI Relationship Summarizer

By: Anderson Wu

A simple terminal app that summarizes a user's relationship situation and gives grounded, practical advice using the Google Gemini API. It stores past analyses locally in SQLite so the user can review them later.

This app is for educational use. It is not a replacement for therapy, emergency help, legal advice, or professional support.

## Submission Materials

- Source code directory: project root and layer folders `interface/`, `engine/`, `storage/`, `services/`, and `models/`
- Test directory: `tests/`
- Requirement specification and design document: [`docs/requirements_and_design.md`](docs/requirements_and_design.md)
- Demo video: [link](https://youtu.be/L5or6qVHFm8)
- Setup and execution instructions: see the Setup section below

## Architecture

The project keeps responsibilities separated:

- Interface layer: terminal input, validation, menus, and output formatting in `interface/`
- Engine layer: Gemini prompt building, API calls, JSON parsing, and AI result creation in `engine/`
- Storage layer: SQLite setup, saving, and retrieval in `storage/`
- Service layer: coordinates the interface, engine, and storage in `services/`

The engine never prints, reads terminal input, or saves to SQLite. The storage layer never calls Gemini or builds prompts. The CLI never talks directly to the database or Gemini.

## Setup

Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate
```

On Windows:

```powershell
python -m venv venv
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create your local environment file:

```bash
cp .env.example .env
```

On Windows:

```powershell
copy .env.example .env
```

Open `.env` and replace the example API key value with your real Google Gemini API key.

Run the app:

```bash
python main.py
```

## Testing

Run tests with:

```bash
pytest
```

The tests mock Gemini responses and do not call the real Gemini API.

## Security Notes

- Do not commit `.env`.
- Do not hardcode API keys in Python files.
- Relationship data can be sensitive, and the SQLite database is stored locally.
- If a situation involves immediate danger, threats, abuse, coercion, stalking, or self-harm, contact trusted people and appropriate professional or emergency support.
