"""Sequential startup script runner."""
from pathlib import Path
from src.shell import Result


def run_script(path: Path, execute, write) -> None:
    """Echo through execute; stop at the first failure or exit."""
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as exc:
        write(f"Error: cannot read startup script: {exc}")
        return
    for number, line in enumerate(lines, 1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        result: Result = execute(line)
        if result.error:
            write(f"Startup script stopped at line {number}: {path}")
            return
        if result.exit:
            return
