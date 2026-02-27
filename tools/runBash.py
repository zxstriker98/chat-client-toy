import subprocess
from pydantic import BaseModel, Field
from tools.tools import tool


class RunBashParams(BaseModel):
    command: str = Field(description="The bash command to execute")


@tool("run_bash", "Execute a bash command and return the output", RunBashParams)
def run_bash(command: str) -> str:
    """Execute a bash command and return the output."""
    try:
        result: subprocess.CompletedProcess[str] = subprocess.run(
            command, shell=True, capture_output=True, text=True, timeout=10
        )
        output: str = result.stdout
        if result.stderr:
            output += result.stderr
        return output if output else "(no output)"
    except subprocess.TimeoutExpired:
        return f"Error: Command timed out after 10 seconds"
    except Exception as e:
        return f"Error: {str(e)}"
