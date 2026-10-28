"""CLI and YAML configuration; file values override CLI values."""
import argparse
from dataclasses import dataclass
from pathlib import Path
import yaml


@dataclass
class Config:
    """Resolved application parameters."""
    vfs: Path
    startup: Path | None = None


def load_config(argv=None) -> Config:
    """Read arguments and safely parse a YAML mapping."""
    parser = argparse.ArgumentParser(description="GUI UNIX emulator, variant 26")
    parser.add_argument("--vfs", default="examples/vfs.xml")
    parser.add_argument("--startup")
    parser.add_argument("--config")
    args = parser.parse_args(argv)
    values = {"vfs": args.vfs, "startup": args.startup}
    if args.config:
        path = Path(args.config).resolve()
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                raise ValueError("expected a YAML mapping")
            if set(data) - {"vfs", "startup"}:
                raise ValueError("allowed keys: vfs, startup")
            for key, value in data.items():
                if not isinstance(value, str) or not value.strip():
                    raise ValueError(f"{key}: expected a nonempty path string")
                values[key] = str(path.parent / value)
        except (OSError, UnicodeError, yaml.YAMLError, ValueError) as exc:
            parser.error(f"cannot read configuration: {exc}")
    return Config(
        Path(values["vfs"]).resolve(),
        Path(values["startup"]).resolve() if values["startup"] else None,
    )
