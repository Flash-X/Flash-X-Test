"""
Filesystem utilities for FlashTest static generator.
"""

import re
from pathlib import Path
from typing import List

DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}.*")


def list_site_dirs(target_dir: Path) -> List[Path]:
    """Return all first-level directories in *target_dir* (sites)."""
    return sorted([d for d in target_dir.iterdir() if d.is_dir()])


def list_invocation_dirs(site_dir: Path) -> List[Path]:
    """Return all invocation directories in *site_dir* matching YYYY-MM-DD*, skipping .lock."""
    inv_dirs: List[Path] = []
    for d in site_dir.iterdir():
        if not d.is_dir():
            continue
        if (d / ".lock").exists():
            continue
        if DATE_PATTERN.match(d.name):
            inv_dirs.append(d)
    return sorted(inv_dirs, key=lambda p: p.name, reverse=True)
