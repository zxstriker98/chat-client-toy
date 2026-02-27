import json
from typing import Any, Callable


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

    def execute(self, name: str, arguments: str) -> str:
        """Execute a registered tool by name with JSON arguments."""
        if name not in self.tool_function:
            return f"Unknown tool: {name}"
        args: dict[str, Any] = json.loads(arguments)
        return self.tool_function[name](**args)


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


# Import tool modules so their @tool decorators run and register
import tools.readFile
import tools.runBash
import tools.webSearch