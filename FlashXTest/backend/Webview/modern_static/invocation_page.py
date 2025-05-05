"""
Generate site-combined invocation pages that list builds.
"""
import html
from pathlib import Path
from typing import Dict, List

from .html_utils import zebra_row_class, page_header, page_footer
from .status import parse_build_status


def generate_combined_invocation_page(
    inv_name: str, site_dirs: Dict[str, Path], site_order: List[str]
) -> str:
    """Produce a page that lists all sites for one invocation with build tables."""
    sections: List[str] = []
    for site in site_order:
        inv_dir = site_dirs.get(site)
        if not inv_dir:
            continue
        sections.append(f"<h2>{html.escape(site)}</h2>")
        sections.append("<table>")
        sections.append("  <tr><th>Build</th><th>Status</th><th>Summary</th></tr>")
        builds = sorted(
            [d for d in inv_dir.iterdir() if d.is_dir()], key=lambda p: p.name
        )
        for idx, b in enumerate(builds):
            status, exit_msg = parse_build_status(b)
            # link to detailed build frameset page
            rel_link = f"../{html.escape(site)}/{html.escape(inv_name)}/{html.escape(b.name)}/frameset.html"
            sections.extend(
                [
                    f"  <tr class=\"{zebra_row_class(idx)}\">",
                    f'    <td><a class=\"cell-link\" href="{rel_link}">{html.escape(b.name)}</a></td>',
                    f'    <td class="{status.colour}">{status.emoji}</td>',
                    f"    <td>{html.escape(exit_msg)}</td>",
                    "  </tr>",
                ]
            )
        sections.append("</table>")

    title = f"Invocation {inv_name}"
    header = page_header(title, css_href="../style.css")
    content = [
        f"<h1>{html.escape(title)}</h1>",
        '<p><a href="../index.html">&larr; Back to overview</a></p>',
        *sections,
    ]
    footer = page_footer()

    return "\n".join(header + content + footer)
