import os

from pydantic import BaseModel, Field
from tools.tools import tool

MAX_READ_SIZE: int = 100_000  # ~100 KB


class ReadFileParams(BaseModel):
    path: str = Field(description="The file path to read")


@tool("read_file", "Read the contents of a file at the given path (large files are truncated)", ReadFileParams)
def read_file(path: str) -> str:
    """Read the contents of a file at the given path."""
    try:
        file_size: int = os.path.getsize(path)
        with open(path, "r") as f:
            content: str = f.read(MAX_READ_SIZE)
        if file_size > MAX_READ_SIZE:
            content += f"\n... [truncated — file is {file_size:,} bytes, showing first {MAX_READ_SIZE:,}]"
        return content
    except FileNotFoundError:
        return f"Error: File not found: {path}"
    except PermissionError:
        return f"Error: Permission denied: {path}"
    except UnicodeDecodeError:
        return f"Error: Cannot read binary file: {path}"
    except OSError as e:
        return f"Error reading file: {e}"
