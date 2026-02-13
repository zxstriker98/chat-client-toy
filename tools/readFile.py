from pydantic import BaseModel, Field
from tools.tools import tool


class ReadFileParams(BaseModel):
    path: str = Field(description="The file path to read")


@tool("read_file", "Read the contents of a file at the given path", ReadFileParams)
def read_file(path: str) -> str:
    """Read the contents of a file at the given path."""
    try:
        with open(path, "r") as f:
            return f.read()
    except FileNotFoundError:
        return f"Error: File not found: {path}"
    except PermissionError:
        return f"Error: Permission denied: {path}"
