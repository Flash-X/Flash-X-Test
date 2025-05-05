"""Utility functions for generating HTML pages."""
import html
from typing import List, Optional


# zebra-stripe rows
def zebra_row_class(idx: int) -> str:
    return "row-alt" if idx % 2 else "row"


def page_header(
    title: str,
    css_href: str,
    base_target: Optional[str] = None,
    body_class: Optional[str] = None,
) -> List[str]:
    """Return common HTML header lines including DOCTYPE, head, and opening body.
    Optionally set <base> and a CSS class on <body>."""
    lines: List[str] = [
        "<!DOCTYPE html>",
        '<html lang="en">',
        "<head>",
        '  <meta charset="utf-8">',
        f"  <title>{html.escape(title)}</title>",
        f'  <link rel="stylesheet" href="{css_href}">',
        "</head>",
    ]
    # opening body with optional class
    body_attrs = []
    if body_class:
        body_attrs.append(f'class="{body_class}"')
    body_tag = "<body"
    if body_attrs:
        body_tag += " " + " ".join(body_attrs)
    body_tag += ">"
    lines.append(body_tag)
    # optional base target for frames
    if base_target:
        lines.append(f"<base target=\"{base_target}\">")
    return lines


def page_header_nobody(title: str, css_href: str) -> List[str]:
    """Return HTML header lines without opening body (e.g., for frameset pages)."""
    return [
        "<!DOCTYPE html>",
        "<html lang=\"en\">",
        "<head>",
        "  <meta charset=\"utf-8\">",
        f"  <title>{html.escape(title)}</title>",
        f"  <link rel=\"stylesheet\" href=\"{css_href}\">",
        "</head>",
    ]


def page_footer() -> List[str]:
    """Return closing body and html tags."""
    return ["</body>", "</html>"]
