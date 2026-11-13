"""
Generate site-combined invocation pages that list builds.
"""

import html
from pathlib import Path
from typing import Dict, List

from .html_utils import zebra_row_class, page_header, page_footer
from .status import parse_build_status

# Maps status colour to a numeric sort value so dropdowns produce a
# consistent order (worst → best: red=0, yellow=1, green=2).
_STATUS_SORT = {"red": "0", "yellow": "1", "green": "2"}


def _generate_site_table_header(site: str) -> List[str]:
    """Generate the filter controls header for one site section."""
    return [
        '<div class="site-header">',
        f"  <h2>{html.escape(site)}</h2>",
        '  <div class="filters">',
        '    <label>Status:',
        '      <span class="select-wrap">',
        '        <select class="status-filter">',
        '          <option value="all">All</option>',
        '          <option value="green">Passed</option>',
        '          <option value="yellow">Warnings</option>',
        '          <option value="red">Fail</option>',
        "        </select>",
        "      </span>",
        "    </label>",
        '    <label>Error Type:',
        '      <span class="select-wrap">',
        '        <select class="type-filter">',
        '          <option value="all">All</option>',
        '          <option value="setup">Setup</option>',
        '          <option value="compilation">Compilation</option>',
        '          <option value="execution">Execution</option>',
        '          <option value="testing">Testing</option>',
        "        </select>",
        "      </span>",
        "    </label>",
        "  </div>",
        "</div>",  # close site-header
    ]


def generate_combined_invocation_page(
    inv_name: str, site_dirs: Dict[str, Path], site_order: List[str], css_content: str
) -> str:
    """Produce a page listing all sites for one invocation with filterable build tables."""
    sections: List[str] = []
    for site in site_order:
        inv_dir = site_dirs.get(site)
        if not inv_dir:
            continue

        sections.append('<div class="site-section">')
        sections.extend(_generate_site_table_header(site))

        sections.append('<table class="inv-table">')
        sections.append("  <tr>")
        sections.append('    <th class="col-build">Build</th>')
        sections.append('    <th class="col-status">Status</th>')
        sections.append('    <th class="col-summary">Summary</th>')
        sections.append("  </tr>")

        builds = sorted(
            [d for d in inv_dir.iterdir() if d.is_dir()], key=lambda p: p.name
        )
        for idx, b in enumerate(builds):
            status, exit_msg = parse_build_status(b)
            rel_link = (
                f"../{html.escape(site)}/{html.escape(inv_name)}"
                f"/{html.escape(b.name)}/frameset.html"
            )
            # Determine error types for the type-filter dropdown
            err_types = []
            lm = exit_msg.lower()
            if "setup" in lm:
                err_types.append("setup")
            if "compilation" in lm:
                err_types.append("compilation")
            if "execution" in lm:
                err_types.append("execution")
            if "testing" in lm:
                err_types.append("testing")
            types_str = " ".join(err_types)
            sort_val = _STATUS_SORT.get(status.colour, "9")

            sections.extend(
                [
                    f'  <tr class="{zebra_row_class(idx)}"'
                    f' data-status="{status.colour}"'
                    f' data-errortypes="{types_str}">',
                    f'    <td class="col-build">'
                    f'<a class="cell-link" href="{rel_link}">'
                    f"{html.escape(b.name)}</a></td>",
                    f'    <td class="col-status {status.colour}"'
                    f' data-sort-value="{sort_val}">{status.emoji}</td>',
                    f'    <td class="col-summary">{html.escape(exit_msg)}</td>',
                    "  </tr>",
                ]
            )

        sections.append("</table>")
        # "No results" message shown by JS when all rows are filtered out
        sections.append('<p class="no-results-msg">No builds match the selected filters.</p>')
        sections.append("</div>")  # close site-section

    title = f"Invocation {inv_name}"
    header = page_header(title, css_content)
    content = [
        f"<h1>{html.escape(title)}</h1>",
        '<p><a href="../index.html">&larr; Back to overview</a></p>',
        *sections,
        '<script src="../js/invocation_filter.js"></script>',
        "<script>",
        "window.onload = function() { initInvocationFilter(); };",
        "</script>",
    ]
    footer = page_footer()
    return "\n".join(header + content + footer)
