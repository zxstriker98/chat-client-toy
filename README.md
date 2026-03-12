# Chat Client Toy

A multi-provider LLM chat client with streaming and tool-calling support. One interface, many LLMs.

## Architecture

```
main.py                         # CLI entry point (--model, --system-prompt, --stream)
│
├── providers/
│   ├── base.py                 # BaseLLMClient / AsyncBaseLLMClient (abstract)
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
    ├── runBash.py              # run_bash tool
    └── webSearch.py            # web_search tool (Brave Search API)
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

# Optional — only needed for the web_search tool
BRAVE_SEARCH_API_KEY="your-brave-search-key-here"
```

> **Note:** `.env` is in `.gitignore` — your keys won't be committed.

**Where to get API keys:**
- OpenAI: https://platform.openai.com/api-keys
- Anthropic: https://console.anthropic.com/settings/keys
- Grok (xAI): https://console.x.ai/
- Groq: https://console.groq.com/keys
- Brave Search: https://brave.com/search/api/
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

| Prefix     | Provider   | Example models                          |
|------------|------------|-----------------------------------------|
| `gpt`      | OpenAI     | `gpt-4o`, `gpt-5.2`, `gpt-4o-mini`     |
| `o1`       | OpenAI     | `o1`, `o1-mini`                         |
| `claude`   | Anthropic  | `claude-sonnet-4-20250514`, `claude-opus-4-20250514` |
| `grok`     | Grok (xAI) | `grok-2`, `grok-3`                      |
| `llama`    | Groq       | `llama-3.3-70b-versatile`, `llama-3.1-8b-instant` |
| `mistral`  | Groq       | `mistral-saba-24b`                      |
| `qwen`     | Groq       | `qwen-qwq-32b`                         |
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

| Tool          | Description                          | Requires          |
|---------------|--------------------------------------|-------------------|
| `read_file`   | Read contents of a local file        | —                 |
| `run_bash`    | Execute a bash command (10s timeout) | —                 |
| `web_search`  | Search the web via Brave Search      | `BRAVE_SEARCH_API_KEY` |

Tools are auto-registered via the `@tool` decorator and made available to all providers.

## Design Patterns

- **Adapter Pattern** — Each provider normalizes a different API (OpenAI, Anthropic, Ollama, Grok, Groq) to one interface (`BaseLLMClient`)
- **Strategy Pattern** — Swap providers at runtime via `--model` flag
- **Factory Pattern** — `ProviderFactory.from_model()` picks the right provider class
- **Template Method** — `generate_response()` defines the flow; subclasses implement `_call_api()`, `_extract_tool_calls()`, etc.
- **Decorator Pattern** — `@tool` registers functions as callable tools

## Adding a New Provider

If the provider is **OpenAI-compatible** (most are), just create a new file following the pattern in `OllamaClient.py` or `GroqClient.py`:

```python
import os
from openai import OpenAI, AsyncOpenAI
from providers.openai_compat_base import OpenAICompatClient, AsyncOpenAICompatClient

BASE_URL = os.getenv("MY_PROVIDER_BASE_URL", "https://api.example.com/v1")
API_KEY = os.getenv("MY_PROVIDER_API_KEY", "")

class MyProviderClient(OpenAICompatClient):
    def _create_client(self) -> OpenAI:
        return OpenAI(base_url=BASE_URL, api_key=API_KEY)

class AsyncMyProviderClient(AsyncOpenAICompatClient):
    def _create_client(self) -> AsyncOpenAI:
        return AsyncOpenAI(base_url=BASE_URL, api_key=API_KEY)
```

Then register it in `ProviderFactory.py` and `__init__.py`.
