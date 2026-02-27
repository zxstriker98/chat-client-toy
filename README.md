# Chat Client Toy

A multi-provider LLM chat client with tool-calling support. One interface, many LLMs.

## Architecture

```
main.py                         # CLI entry point (--model, --system-prompt)
│
├── providers/
│   ├── base.py                 # BaseLLMClient / AsyncBaseLLMClient (abstract)
│   ├── models.py               # Conversation & ConversationHistory (Pydantic)
│   ├── openai_compat_base.py   # Shared base for OpenAI-compatible APIs
│   ├── OpenAIClient.py         # OpenAI provider
│   ├── OllamaClient.py         # Ollama provider (local models)
│   ├── AnthropicClient.py      # Anthropic provider (Claude)
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
# Default model (gpt-5.2)
uv run python main.py

# Specify a model — provider is auto-detected
uv run python main.py --model gpt-4o              # → OpenAI
uv run python main.py --model claude-sonnet-4-20250514     # → Anthropic
uv run python main.py --model llama3.1             # → Ollama (local)

# Custom system prompt
uv run python main.py --model gpt-4o --system-prompt "You are a Python expert"
```

Type `exit` to quit the chat.

## Provider Auto-Detection

The `ProviderFactory` maps model name prefixes to providers:

| Prefix     | Provider   | Example models                     |
|------------|------------|-------------------------------------|
| `gpt`      | OpenAI     | `gpt-4o`, `gpt-5.2`, `gpt-4o-mini` |
| `o1`       | OpenAI     | `o1`, `o1-mini`                     |
| `sonnet`   | Anthropic  | `claude-sonnet-4-20250514`                  |
| `opus`     | Anthropic  | `claude-opus-4-20250514`                    |
| `llama`    | Ollama     | `llama3.1`, `llama3.2`              |
| *(other)*  | Ollama     | Any unrecognized model              |

> Unrecognized models default to Ollama, since Ollama can serve many open-source models.

## Tools

The chat client can use tools during conversation:

| Tool          | Description                          | Requires          |
|---------------|--------------------------------------|--------------------|
| `read_file`   | Read contents of a local file        | —                  |
| `run_bash`    | Execute a bash command (10s timeout) | —                  |
| `web_search`  | Search the web via Brave Search      | `BRAVE_SEARCH_API_KEY` |

Tools are auto-registered via the `@tool` decorator and made available to all providers.

## Design Patterns

- **Adapter Pattern** — Each provider normalizes a different API (OpenAI, Anthropic, Ollama) to one interface (`BaseLLMClient`)
- **Strategy Pattern** — Swap providers at runtime via `--model` flag
- **Factory Pattern** — `ProviderFactory.from_model()` picks the right provider class
- **Template Method** — `generate_response()` defines the flow; subclasses implement `_call_api()`, `_extract_tool_calls()`, etc.
- **Decorator Pattern** — `@tool` registers functions as callable tools
