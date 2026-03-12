import subprocess
from pydantic import BaseModel, Field
from tools.tools import tool

BASH_TIMEOUT: int = 30

MAX_OUTPUT_LENGTH: int = 500_000


class RunBashParams(BaseModel):
    command: str = Field(description="The bash command to execute")


@tool("run_bash", "Execute a bash command and return the output", RunBashParams)
def run_bash(command: str) -> str:
    """Execute a bash command and return the output."""
    try:
        result: subprocess.CompletedProcess[str] = subprocess.run(
            command, shell=True, capture_output=True, text=True, timeout=BASH_TIMEOUT
        )
        output: str = result.stdout
        if result.stderr:
            output += result.stderr
        if not output:
            return "(no output)"
        if len(output) > MAX_OUTPUT_LENGTH:
            output = output[:MAX_OUTPUT_LENGTH] + f"\n... [truncated — {len(output)} chars total, showing first {MAX_OUTPUT_LENGTH}]"
        return output
    except subprocess.TimeoutExpired:
        return f"Error: Command timed out after {BASH_TIMEOUT} seconds"
    except Exception as e:
        return f"Error: {str(e)}"
