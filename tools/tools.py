import importlib
import json
from concurrent.futures import ThreadPoolExecutor, Future, TimeoutError as FuturesTimeoutError
from pathlib import Path
from typing import Any, Callable

# Maximum time (seconds) any single tool invocation may run before being aborted.
DEFAULT_TOOL_TIMEOUT: int = 300

MAX_TOOL_RESULT_LENGTH: int = 40_000

_tool_executor = ThreadPoolExecutor(max_workers=2)


class ToolRegistry:
    def __init__(self) -> None:
        self.tool_spec: dict[str, dict[str, Any]] = {}
        self.tool_function: dict[str, Callable[..., str]] = {}

    def register(self, name: str, description: str, param_model: type) -> Callable[[Callable[..., str]], Callable[..., str]]:
        """Decorator that registers a function as a tool."""
        def decorator(func: Callable[..., str]) -> Callable[..., str]:
            self.tool_spec[name] = {
                "type": "function",
                "name": name,
                "description": description,
                "parameters": param_model.model_json_schema()
            }
            self.tool_function[name] = func
            return func
        return decorator

    def execute(self, name: str, arguments: str, timeout: int = DEFAULT_TOOL_TIMEOUT) -> str:
        """Execute a registered tool by name with JSON arguments.

        The tool is run in a separate thread with a timeout.  If the tool does
        not complete within *timeout* seconds the call is abandoned and an error
        string is returned.  Results longer than MAX_TOOL_RESULT_LENGTH are
        truncated.
        """
        if name not in self.tool_function:
            return f"Unknown tool: {name}"

        args: dict[str, Any] = json.loads(arguments)
        future: Future[str] = _tool_executor.submit(self.tool_function[name], **args)
        try:
            result: str = future.result(timeout=timeout)
        except FuturesTimeoutError:
            future.cancel()
            return f"Error: Tool '{name}' timed out after {timeout} seconds"
        except Exception as e:
            return f"Error executing tool '{name}': {type(e).__name__}: {e}"

        # Truncate overly-large results to avoid blowing the context window.
        if len(result) > MAX_TOOL_RESULT_LENGTH:
            result = result[:MAX_TOOL_RESULT_LENGTH] + f"\n... [truncated — {len(result)} chars total, showing first {MAX_TOOL_RESULT_LENGTH}]"

        return result


# Global registry — tools register themselves when imported
registry = ToolRegistry()


def tool(name: str, description: str, param_model: type) -> Callable:
    """Standalone decorator to register a function as a tool.

    Usage:
        @tool("read_file", "Read a file's contents", ReadFileParams)
        def read_file(path: str) -> str:
            ...
    """
    return registry.register(name, description, param_model)

def autodiscover(dir_name: str, exclude: list[str]) -> None:
    modules = [f"{dir_name}.{path.stem}" for path in Path(dir_name).glob("*.py") if path.stem not in exclude]
    for module in modules:
        importlib.import_module(module)

# Import tool modules so their @tool decorators run and register
autodiscover("tools", exclude=["__init__", "tools"])
