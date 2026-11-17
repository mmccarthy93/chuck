# C.H.U.C.K.

**Cognitive Heuristic Utility & Command Kernel**

C.H.U.C.K. is a modular personal AI assistant built with Python, FastAPI, and the OpenAI API.

The project aims to create a privacy-conscious, extensible AI assistant with persistent fact-based memory, temporary conversation context, and a configurable personality.

## Features — v0.1

- Web-based chat interface
- OpenAI-powered conversations
- Configurable assistant personality
- Persistent fact memory using SQLite
- Temporary conversation history stored in RAM
- Natural-language memory saving, retrieval, and deletion
- Confirmation workflow for implicit memory changes
- Privacy classifications for stored memories
- Tool execution through a centralized orchestrator and dispatcher
- Automated regression tests

## Tech Stack

- Python 3.13
- FastAPI
- OpenAI Responses API
- SQLite
- HTML, CSS, and JavaScript
- pytest

## Getting Started

### 1. Clone the repository

```powershell
git clone <repository-url>
cd chuck
```

### 2. Create a virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
python -m pip install -r requirements.txt
```

### 4. Configure environment variables

Copy `.env.example` to `.env`:

```powershell
Copy-Item .env.example .env
```

Edit `.env` and provide your OpenAI API key.

### 5. Start CHUCK

```powershell
python -m uvicorn app.main:app --reload --host 127.0.0.1
```

Open http://127.0.0.1:8000 in your browser.

## Running Tests

```powershell
python -m pytest tests/ -v
```

## Memory and Privacy

CHUCK stores long-term facts in SQLite and keeps recent conversation context in RAM.

Memories have four privacy classifications:

| Classification | Cloud model access |
|---|---|
| `general` | Allowed |
| `personal` | Allowed |
| `local_only` | Blocked |
| `sensitive` | Blocked |

Only cloud-permitted memories can be passed to the OpenAI model.

**Current limitations:** This is a localhost development prototype, not a production-hardened application. Memory intent detection relies partly on explicit command patterns, and keyword-based fact retrieval may miss relevant information. The application does not yet support user authentication.

For v0.1, keep CHUCK bound to `127.0.0.1` and do not expose it publicly.

## Roadmap

### Phase 1 — Core Foundation
- Modular model-provider architecture
- Persistent fact memory and temporary sessions
- Privacy-aware retrieval
- Orchestrator-managed tools
- Web chat interface
- Basic regression testing

### Phase 2 — Intelligence Improvements
- LLM-based natural-language intent understanding
- Improved semantic memory retrieval
- More reliable memory extraction and authorization
- Better uncertainty handling and conversational context

### Future Phases
- Voice interaction
- Local LLM support
- Computer control and automation
- Home Assistant integration
- Additional tools and integrations

## Project Status

**Version:** 0.1.0 — Local development prototype

**License:** Not yet specified.