"""
Generate site-combined invocation pages that list builds.
"""

import html
from pathlib import Path
from typing import Dict, List

from .html_utils import zebra_row_class, page_header, page_footer
from .status import parse_build_status


def _generate_site_table_header(site: str) -> List[str]:
    """A helper function to generate the header for a site table."""
    content = [
        '<div class="site-header">',
        f"<h2>{html.escape(site)}</h2>",
        '<div class="filters">',
        '  <label>Status: <select class="status-filter"> ',
        '    <option value="all">All</option>',
        '    <option value="green">Passed</option>',
        '    <option value="yellow">Warnings</option>',
        '    <option value="red">Fail</option>',
        "  </select></label>",
        '  <label>Error Type: <select class="type-filter"> ',
        '    <option value="all">All</option>',
        '    <option value="setup">Setup</option>',
        '    <option value="compilation">Compilation</option>',
        '    <option value="execution">Execution</option>',
        '    <option value="testing">Testing</option>',
        "  </select></label>",
        "</div>",
        "</div>",  # close site-header
    ]
    return content


def generate_combined_invocation_page(
    inv_name: str, site_dirs: Dict[str, Path], site_order: List[str]
) -> str:
    """Produce a page that lists all sites for one invocation with build tables."""
    sections: List[str] = []
    for site in site_order:
        inv_dir = site_dirs.get(site)
        if not inv_dir:
            continue
        # Section per site with heading and its own filter controls
        sections.append('<div class="site-section">')

        # Generate the header for the site table
        sections.extend(_generate_site_table_header(site))

        # Build table with fixed layout and column classes
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
            # link to detailed build frameset page
            rel_link = f"../{html.escape(site)}/{html.escape(inv_name)}/{html.escape(b.name)}/frameset.html"
            # Determine error types for filtering
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
            # Table row with data attributes and column classes
            sections.extend(
                [
                    f'  <tr class="{zebra_row_class(idx)}" data-status="{status.colour}" data-errortypes="{types_str}">',
                    f'    <td class="col-build"><a class="cell-link" href="{rel_link}">{html.escape(b.name)}</a></td>',
                    f'    <td class="col-status {status.colour}">{status.emoji}</td>',
                    f'    <td class="col-summary">{html.escape(exit_msg)}</td>',
                    "  </tr>",
                ]
            )
        sections.append("</table>")
        # Close the site section
        sections.append("</div>")

    title = f"Invocation {inv_name}"
    header = page_header(title, css_href="../style.css")
    # Page content: heading, back link, filters, site tables, and init script
    content = [
        f"<h1>{html.escape(title)}</h1>",
        '<p><a href="../index.html">&larr; Back to overview</a></p>',
        *sections,
        "<!-- Include filter script -->",
        '<script src="../js/invocation_filter.js"></script>',
        "<script>window.onload = initInvocationFilter;</script>",
    ]
    footer = page_footer()

    return "\n".join(header + content + footer)
