"""
Generate the overview index HTML page.
"""

import html
import json
from pathlib import Path
from typing import Dict, List

from .html_utils import zebra_row_class, page_header, page_footer
from .status import InvocationStatus, parse_build_status


def generate_html(
    board: Dict[str, Dict[str, InvocationStatus]],
    sites: List[str],
    invocations: List[str],
    inv_dir_lookup: Dict[str, Dict[str, Path]],
    title: str = "FlashXTest Invocations",
) -> str:
    """Return *index.html* as a single string."""

    lines: List[str] = page_header(title, css_href="style.css")

    # dynamic tooltip support: include tooltip script and container
    lines.append('<script src="js/statsWindow.js"></script>')
    lines.append("<script>window.onload=statsWindowInit;</script>")
    lines.append('<div id="statsWindow" class="stats-window">')
    lines.append('  <div id="statsHeader" class="stats-header"></div>')
    lines.append('  <div id="statsBody" class="stats-body"></div>')
    lines.append("</div>")

    lines.append(f"<h1>{html.escape(title)}</h1>")

    # Start the table
    lines.append("<table>")
    # header row
    lines.append("  <tr>")
    lines.append("    <th>Invocation</th>")
    for site in sites:
        lines.append(f"    <th>{html.escape(site)}</th>")
    lines.append("  </tr>")
    # body rows
    for idx, inv_name in enumerate(invocations):
        lines.append(f'  <tr class="{zebra_row_class(idx)}">')
        # dynamic hover for invocation
        inv_href = f"invocations/{html.escape(inv_name)}.html"

        # header/body for tooltip
        # Build execution summary across all sites
        # Collect all builds for this invocation
        builds = []  # list of (site, build_path)
        for site in sites:
            inv_paths = inv_dir_lookup.get(inv_name, {})
            site_inv = inv_paths.get(site)
            if site_inv and site_inv.is_dir():
                for b in site_inv.iterdir():
                    if b.is_dir():
                        builds.append((site, b))
        total_tests = len(builds)
        failing = []  # list of (site, build_name, exit_msg)
        for site, b in builds:
            status, exit_msg = parse_build_status(b)
            if status.colour != "green":
                failing.append((site, b.name, exit_msg))
        if failing:
            header_text = f"{len(failing)}/{total_tests} tests had some error"
        else:
            header_text = f"All {total_tests} tests completed successfully"
        header_js = json.dumps(header_text)
        body_lines = [f"{name} - {msg}" for _, name, msg in failing]
        body_js = json.dumps("<br>".join(body_lines))
        lines.append(
            f'    <td><a class="cell-link" href="{inv_href}" '
            + f"onMouseOver='appear({header_js},{body_js})' onMouseOut='disappear()'>"
            + f"{html.escape(inv_name)}</a></td>"
        )

        for site in sites:
            status = board.get(inv_name, {}).get(site)
            if status is None:
                lines.append("    <td>&nbsp;</td>")
            else:
                lines.append(f'    <td class="{status.colour}">{status.emoji}</td>')
        lines.append("  </tr>")
    lines.append("</table>")
    lines.extend(page_footer())
    return "\n".join(lines)
