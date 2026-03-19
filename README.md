# Chat Client Toy

A multi-provider LLM chat client with streaming and tool-calling support. One interface, many LLMs.

## Architecture

```
main.py                         # CLI entry point (--model, --system-prompt, --stream)
│
├── providers/
│   ├── base.py                 # AsyncBaseLLMClient (abstract)
│   ├── models.py               # Conversation & tool schemas (Pydantic)
│   ├── openai_compat_base.py   # Shared base for OpenAI-compatible APIs
│   ├── OpenAIClient.py         # OpenAI provider
│   ├── OllamaClient.py         # Ollama provider (local models)
│   ├── AnthropicClient.py      # Anthropic provider (Claude)
│   ├── GrokClient.py           # Grok provider (xAI)
│   ├── GroqClient.py           # Groq provider (open source models)
│   └── ProviderFactory.py      # Auto-selects provider from model name
│
└── tools/
    ├── tools.py                # ToolRegistry + @tool decorator
    ├── readFile.py             # read_file tool
    └── runBash.py              # run_bash tool
```

## Setup

### 1. Install dependencies

Requires Python 3.12+ and [uv](https://docs.astral.sh/uv/):

```bash
uv sync
```

### 2. Configure environment variables

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Then fill in your API keys:

```env
# Required for OpenAI models (gpt-4o, gpt-5.2, o1, etc.)
OPENAI_API_KEY="sk-your-openai-key-here"

# Required for Anthropic models (claude-sonnet, claude-opus, etc.)
ANTHROPIC_API_KEY="sk-ant-your-anthropic-key-here"

# Required for Grok models (grok-2, grok-3, etc.)
XAI_API_KEY="xai-your-grok-key-here"

# Required for Groq models (llama, mistral, mixtral, gemma, etc.)
GROQ_API_KEY="gsk-your-groq-key-here"

# Optional — Ollama runs locally, these are the defaults
OLLAMA_BASE_URL="http://localhost:11434/v1"
OLLAMA_API_KEY="ollama"

# Optional — only needed for the PageIndex challenges and chunk ingestion
PAGEINDEX_API_KEY="your-pageindex-api-key-here"
# Optional — override for self-hosted PageIndex (default: https://api.pageindex.ai)
# PAGEINDEX_BASE_URL="http://localhost:8080"
```

> **Note:** `.env` is in `.gitignore` — your keys won't be committed.

**Where to get API keys:**
- OpenAI: https://platform.openai.com/api-keys
- Anthropic: https://console.anthropic.com/settings/keys
- Grok (xAI): https://console.x.ai/
- Groq: https://console.groq.com/keys
- Brave Search: https://brave.com/search/api/
- PageIndex: https://pageindex.ai/
- Ollama: No key needed — just install and run [Ollama](https://ollama.com/) locally

### 3. (Optional) Install Ollama for local models

```bash
# macOS
brew install ollama

# Start the server
ollama serve

# Pull a model
ollama pull llama3.1
```

## Usage

```bash
# Default model (gpt-5.2) with streaming enabled
uv run python main.py

# Specify a model — provider is auto-detected
uv run python main.py --model gpt-4o                       # → OpenAI
uv run python main.py --model claude-sonnet-4-20250514      # → Anthropic
uv run python main.py --model grok-3                        # → Grok (xAI)
uv run python main.py --model llama-3.3-70b-versatile       # → Groq (cloud)
uv run python main.py --model mistral-saba-24b              # → Groq (cloud)

# Disable streaming (responses appear all at once)
uv run python main.py --model gpt-4o --no-stream

# Custom system prompt
uv run python main.py --model gpt-4o --system-prompt "You are a Python expert"
```

Type `exit` to quit the chat.

## Streaming

Streaming is **enabled by default**. Tokens are printed to the terminal as they're generated, giving you a much more responsive experience.

```bash
# Streaming on (default)
uv run python main.py --model gpt-4o --stream

# Streaming off (wait for full response)
uv run python main.py --model gpt-4o --no-stream
```

| | Without Streaming | With Streaming |
|---|---|---|
| **Time to first token** | Full generation time (5-30s) | ~200-500ms |
| **Perceived latency** | High | Low |
| **User experience** | Text appears all at once | Text appears word by word |

## Provider Auto-Detection

The `ProviderFactory` maps model name prefixes to providers:

| Prefix           | Provider   | Example models                          |
|------------------|------------|-----------------------------------------|
| `gpt`            | OpenAI     | `gpt-4o`, `gpt-5.2`, `gpt-4o-mini`     |
| `o1`             | OpenAI     | `o1`, `o1-mini`                         |
| `claude`         | Anthropic  | `claude-sonnet-4-20250514`, `claude-opus-4-20250514` |
| `grok`           | Grok (xAI) | `grok-2`, `grok-3`                      |
| `llama`          | Groq       | `llama-3.3-70b-versatile`, `llama-3.1-8b-instant` |
| `mistral`        | Groq       | `mistral-saba-24b`                      |
| `qwen`           | Groq       | `qwen-qwq-32b`                         |
| `openai/gpt-oss-120b` | Groq       | `openai/gpt-oss-120b`                         |

| *(other)*  | Ollama     | Any unrecognized model (runs locally)   |

> Unrecognized models default to Ollama, which can serve many open-source models locally.

## Providers

### OpenAI
Supports GPT and o1 models via OpenAI's Responses API. Requires `OPENAI_API_KEY`.

### Anthropic
Supports Claude models via Anthropic's Messages API. Requires `ANTHROPIC_API_KEY`.

### Grok (xAI)
Supports xAI's proprietary Grok models. OpenAI-compatible API. Requires `XAI_API_KEY`.

### Groq
Hosts **open source models** (Llama, Mistral, Mixtral, Gemma, etc.) with ultra-fast inference on custom LPU hardware. OpenAI-compatible API. Requires `GROQ_API_KEY`.

### Ollama
Runs open source models **locally** on your machine. No API key needed. Falls back to Ollama for any unrecognized model name.

## Tools

The chat client can use tools during conversation:

| Tool          | Description                                        | Requires               |
|---------------|----------------------------------------------------|------------------------|
| `read_file`   | Read contents of a local file (truncated at 100 KB) | —                      |
| `run_bash`    | Execute a bash command (30s timeout)               | —                      |

Tools are auto-registered via the `@tool` decorator and made available to all providers.

## RAG Pipeline (Chunk Context)

The chat client supports local document-grounded Q&A via `--chunks`. Documents are pre-indexed through PageIndex, stored in SQLite, and searched at query time using BM25.

### Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│ 📥 OFFLINE INGESTION                                               │
│                                                                     │
│  PDF ──→ PageIndex API ──→ get_tree(doc_id, node_summary=True)     │
│                   │              │                                   │
│                   │         tree nodes with:                         │
│                   │           • title, node_id, page_index           │
│                   │           • summary (AI-generated)               │
│                   │           • text (OCR content)                   │
│                   │           • child nodes (hierarchy)              │
│                   │              │                                   │
│                   ▼              ▼                                   │
│              doc_id        Build enriched node_path:                 │
│                            "Chapter (covers A, B, C)                 │
│                               > Section (covers X, Y)               │
│                                 > Subsection"                       │
│                                      │                              │
│                                      ▼                              │
│                            ChunkRecord(path, summary, text)         │
│                                      │                              │
│                                      ▼                              │
│                              SQLite chunks table                    │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────────────┐
│ 🔧 STARTUP  (main.py --chunks)                                     │
│                                                                     │
│  Load all ChunkRecords from SQLite                                 │
│       │                                                             │
│       ▼                                                             │
│  build_index() ──→ tokenize every chunk                            │
│                ──→ compute IDF per word                             │
│                ──→ compute avg doc length                           │
│                ──→ BM25 index ready                                 │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────────────┐
│ 💬 PER-QUERY                                                       │
│                                                                     │
│  User: "How does gradient descent converge?"                       │
│       │                                                             │
│       ▼                                                             │
│  🔍 BM25 Search                                                    │
│    1. tokenize → ['gradient', 'descent', 'converge']               │
│    2. Score each chunk:                                             │
│       IDF(w) × tf·(k₁+1) / (tf + k₁·(1 − b + b·dl/avgdl))       │
│    3. Return top-K by score                                         │
│       │                                                             │
│       ▼                                                             │
│  📋 Format Context (path → summary → text)                         │
│                                                                     │
│    [Relevant document context]                                      │
│    --- [Intro to Optimization (covers Basic Terminology,            │
│         Unconstrained Optimization, Stochastic gradient, ...)       │
│           > Unconstrained Optimization (covers Conditions           │
│             for optimality, Convex sets, Rate of convergence)       │
│               > Line search] (page 58) ---                          │
│    Summary: Details convergence analysis for optimization           │
│    algorithms, deriving general and strongly convex rates.          │
│                                                                     │
│    F(x_{t+1}) - F(x*) ≤ F(x_t) - F(x*) - C|∇F(x_t)|² ...       │
│    [End of context]                                                 │
│       │                                                             │
│       ▼                                                             │
│  📝 Enriched query = context + original question                    │
│       │                                                             │
│       ▼                                                             │
│  🤖 LLM (GPT-5.2 / Claude / etc.)                                 │
│       │                                                             │
│       ▼                                                             │
│  ✅ Answer grounded in document content                             │
└─────────────────────────────────────────────────────────────────────┘
```

### Usage

```bash
# Chat with document-grounded context
uv run python main.py --model gpt-5.2 --chunks

# Custom DB and chunk count
uv run python main.py --model gpt-5.2 --chunks --chunk-db data/pageindex_cache.db --chunk-top-k 3
```

### Ingestion CLI

Add new PDFs to the chunk database using `ingest.py`:

```bash
# Ingest a single PDF (uploads to PageIndex + extracts tree → chunks → DB)
uv run python ingest.py data/report.pdf

# Ingest multiple PDFs
uv run python ingest.py data/*.pdf

# List all ingested documents
uv run python ingest.py --list

# Re-ingest (clear old chunks, re-fetch from PageIndex)
uv run python ingest.py data/report.pdf --reingest

# Skip upload (reuse existing doc_id — useful when PageIndex limit is reached)
uv run python ingest.py data/report.pdf --reingest --skip-upload

# Custom database path
uv run python ingest.py data/report.pdf --db my_chunks.db

# Clear all chunks
uv run python ingest.py --clear
```

### Node Path Format

Ancestor nodes include their children as hints, giving the LLM structural context:

```
General Notation (covers Linear algebra, Topology, Calculus, Probability theory)
  > Topology (covers Open and closed sets, Compact sets, Metric spaces)
    > Compact sets
```

## Design Patterns

- **Adapter Pattern** — Each provider normalizes a different API (OpenAI, Anthropic, Ollama, Grok, Groq) to one interface (`AsyncBaseLLMClient`)
- **Strategy Pattern** — Swap providers at runtime via `--model` flag
- **Factory Pattern** — `ProviderFactory.from_model()` picks the right provider class
- **Template Method** — `generate_response()` defines the flow; subclasses implement `_call_api()`, `_extract_tool_calls()`, etc.
- **Decorator Pattern** — `@tool` registers functions as callable tools

## Adding a New Provider

If the provider is **OpenAI-compatible** (most are), just create a new file following the pattern in `OllamaClient.py` or `GroqClient.py`:

```python
import os
from openai import AsyncOpenAI
from providers.openai_compat_base import AsyncOpenAICompatClient

BASE_URL = os.getenv("MY_PROVIDER_BASE_URL", "https://api.example.com/v1")
API_KEY = os.getenv("MY_PROVIDER_API_KEY", "")

class AsyncMyProviderClient(AsyncOpenAICompatClient):
    def _create_client(self) -> AsyncOpenAI:
        return AsyncOpenAI(base_url=BASE_URL, api_key=API_KEY)
```

Then register it in `ProviderFactory.py` and `__init__.py`.
