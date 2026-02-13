# Chat Client Toy

A minimal, extensible chat client that demonstrates how to call OpenAI (or a local Ollama instance) with tool support. The project is intentionally small so you can quickly experiment with tool calling, conversation history, and different model backends.

## Features

- Simple REPL chat loop via `main.py`.
- OpenAI and Ollama clients with the same interface.
- Tool registry and decorators for easy tool registration.
- Example tools for reading files and running shell commands.

## Project Layout

```
.
├── client/
│   ├── OpenAIClient.py
│   └── OllamaClient.py
├── tools/
│   ├── readFile.py
│   ├── runBash.py
│   └── tools.py
├── main.py
├── pyproject.toml
└── README.md
```

## Requirements

- Python 3.12+
- An OpenAI API key (for OpenAI usage)
- Optional: Ollama running locally for local models

## Setup

1. Create a virtual environment and install dependencies:

```
python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -e .
```

2. Configure environment variables:

Create a `.env` file in the project root:

```
OPENAI_API_KEY=your_api_key_here
```

The app loads environment variables via `python-dotenv` in `main.py`.

## Usage

### OpenAI client (default)

Run the chat loop:

```
python main.py
```

Type messages at the prompt. Type `exit` to quit.

### Ollama client

To use Ollama, swap the client used in `main.py`:

```python
from client.OllamaClient import OllamaClient

client = OllamaClient(
    model="llama3.1",
    instructions="you are a generic chat-bot with access to tools",
    tool_registry=registry,
)
```

Ensure Ollama is running locally:

```
ollama serve
```

## Tooling

Tools are registered via a decorator in `tools/tools.py`:

```python
from tools.tools import tool
from pydantic import BaseModel

class MyToolParams(BaseModel):
    value: str

@tool("my_tool", "Describe the tool", MyToolParams)
def my_tool(value: str) -> str:
    return f"received: {value}"
```

Any module imported by `tools/tools.py` will register its tools automatically. Existing tools:

- `read_file(path: str)` in `tools/readFile.py`
- `run_bash(command: str)` in `tools/runBash.py`

## Conversation Flow

Both clients store a simple conversation history and loop until the model stops requesting tool calls. When a tool call is returned, the tool is executed and the tool result is added back into the conversation.

## Configuration Notes

- OpenAI client uses `OpenAI()` with your `OPENAI_API_KEY`.
- Ollama client uses `OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")` to target the local server.
- Model names are passed directly to the client (for OpenAI defaults, update `model` in `main.py`).

## Troubleshooting

- If you see authentication errors, confirm your `OPENAI_API_KEY` is set.
- If Ollama requests fail, verify `ollama serve` is running and the model is pulled (e.g., `ollama pull llama3.1`).
- If tools are not discovered, ensure the module defining them is imported in `tools/tools.py`.

## Development Tips

- Keep tools small and pure where possible for easier debugging.
- Use `run_bash` sparingly and consider limiting command scope if using untrusted inputs.

## License

This project is provided as-is for experimentation and learning.
