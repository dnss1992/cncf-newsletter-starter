from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Item:
    """Represents a collected item for the newsletter."""

    project: str
    type: str
    title: str
    url: str
    published_at: datetime
    summary: Optional[str] = None
    version: Optional[str] = None
    content_text: Optional[str] = None
