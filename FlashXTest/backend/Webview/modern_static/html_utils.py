"""Utility functions for generating HTML pages."""

import html
from typing import List, Optional


# zebra-stripe rows
def zebra_row_class(idx: int) -> str:
    return "row-alt" if idx % 2 else "row"


def _css_tag(css_content: str) -> str:
    return f"  <style>\n{css_content}\n  </style>"


def page_header(
    title: str,
    css_content: str,
    base_target: Optional[str] = None,
    body_class: Optional[str] = None,
) -> List[str]:
    """Return common HTML header lines including DOCTYPE, head, and opening body."""
    lines: List[str] = [
        "<!DOCTYPE html>",
        '<html lang="en">',
        "<head>",
        '  <meta charset="utf-8">',
        '  <meta name="viewport" content="width=device-width, initial-scale=1">',
        f"  <title>{html.escape(title)}</title>",
        _css_tag(css_content),
        "</head>",
    ]
    body_attrs = []
    if body_class:
        body_attrs.append(f'class="{body_class}"')
    body_tag = "<body"
    if body_attrs:
        body_tag += " " + " ".join(body_attrs)
    body_tag += ">"
    lines.append(body_tag)
    if base_target:
        lines.append(f'<base target="{base_target}">')
    return lines


def page_header_nobody(title: str, css_content: str) -> List[str]:
    """Return HTML header lines without opening body (e.g., for frameset pages)."""
    return [
        "<!DOCTYPE html>",
        '<html lang="en">',
        "<head>",
        '  <meta charset="utf-8">',
        '  <meta name="viewport" content="width=device-width, initial-scale=1">',
        f"  <title>{html.escape(title)}</title>",
        _css_tag(css_content),
        "</head>",
    ]


def page_footer() -> List[str]:
    """Return closing body and html tags."""
    return ["</body>", "</html>"]
