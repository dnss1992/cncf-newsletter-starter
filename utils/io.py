from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

import yaml


def read_yaml(path: str | Path) -> Dict[str, Any]:
    """Load YAML from a file."""

    with open(path, "r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def write_json(path: str | Path, data: Any) -> None:
    """Write an object as JSON."""

    with open(path, "w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, ensure_ascii=False)
