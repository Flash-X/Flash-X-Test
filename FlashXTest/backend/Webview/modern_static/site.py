"""
Build a complete static website (landing page + test results) that can be
published directly, e.g. to GitHub Pages.

Layout of the generated site::

    index.html                 landing page
    about/index.html           about page
    dev/index.html             developer page: latest results per branch
    dev/<label>/...            read-only webview of the latest run for that label
    .nojekyll

The site is updated incrementally, one label at a time, so it can be a clone of
the publishing git repository.
"""

import html
import json
from pathlib import Path
from typing import List

from .fs_utils import list_invocation_dirs, list_site_dirs
from .generator import generate_flashx_testview
from .html_utils import page_footer, page_header, page_nav
from .status import InvocationStatus, classify_invocation, parse_build_status

PROJECT_NAME = "Flash-MX"
PROJECT_TAGLINE = "Incompressible Multiphase Flow"
PROJECT_DESCRIPTION = (
    "Flash-MX is a software system for simulating incompressible multiphase "
    "flows, including boiling and heat transfer, immersed boundaries and solid "
    "mechanics. It is derived from Flash-X and keeps the Flash-X composable "
    "architecture: unit-based setup, the Grid, IO and Driver units, and "
    "support for AMReX and PARAMESH grids."
)
FEATURES = [
    ("Multiphase flow", "Incompressible two-phase flow with interface tracking, "
     "including boiling and heat transfer."),
    ("Immersed boundaries and solids", "Immersed boundary methods and solid "
     "mechanics for fluid-structure problems."),
    ("Composable architecture", "Unit-based setup with Grid, IO and Driver "
     "units, running on AMReX and PARAMESH grids."),
]
PROJECT_REPO = "https://github.com/Flash-MX/Flash-MX"
FLASHX_REPO = "https://github.com/Flash-X/Flash-X"


SUMMARY_FILE = "summary.json"


def _write_summary(results_dir: Path, label_dir: Path) -> None:
    """Record the latest invocation of each site, so the results index can be
    rebuilt from the published site alone."""
    entries = []
    for site_path in list_site_dirs(results_dir):
        invs = list_invocation_dirs(site_path)  # newest first
        if not invs:
            continue
        inv_dir = invs[0]
        counts = {"green": 0, "yellow": 0, "red": 0}
        for b in (d for d in inv_dir.iterdir() if d.is_dir()):
            counts[parse_build_status(b)[0].colour] += 1
        entries.append(
            {
                "site": site_path.name,
                "invocation": inv_dir.name,
                "colour": classify_invocation(inv_dir).colour,
                "counts": counts,
            }
        )
    (label_dir / SUMMARY_FILE).write_text(json.dumps(entries, indent=2), encoding="utf-8")


def _card(label: str, entries: List[dict]) -> List[str]:
    lines = ['<div class="card">', f"  <h2>{html.escape(label)}</h2>"]
    if not entries:
        lines.append('  <p class="empty-note">No results found.</p>')
    for e in entries:
        counts = e["counts"]
        total = sum(counts.values())
        emoji = InvocationStatus(e["colour"]).emoji
        href = f"{html.escape(label)}/invocations/{html.escape(e['invocation'])}.html"
        lines += [
            f'  <div class="meta">{html.escape(e["site"])} &middot; latest invocation '
            f'<a href="{href}">{html.escape(e["invocation"])}</a></div>',
            '  <table class="summary-table">',
            "    <tr><th>Overall</th><th>Passed</th><th>Warnings</th><th>Failed</th><th>Total</th></tr>",
            f'    <tr><td class="{e["colour"]}">{emoji}</td>'
            f'<td>{counts["green"]}</td><td>{counts["yellow"]}</td>'
            f'<td>{counts["red"]}</td><td>{total}</td></tr>',
            "  </table>",
        ]
    lines.append(f'  <p><a href="{html.escape(label)}/index.html">Run details &rarr;</a></p>')
    lines.append("</div>")
    return lines


def _results_index(dev_out: Path, css: str) -> str:
    lines = page_header("Dev – Flash-MX", css)
    lines += page_nav("..", "dev")
    lines += [
        '<div class="hero">',
        "  <h1>Development status</h1>",
        "  <p>Results of the latest automated test-suite run on each branch. "
        "<strong>staged</strong> collects merged pull requests for the nightly "
        "integration run; <strong>main</strong> holds code that has passed it. "
        "Only the most recent run of each branch is kept.</p>",
        "</div>",
        '<div class="cards">',
    ]
    for summary in sorted(dev_out.glob(f"*/{SUMMARY_FILE}")):
        entries = json.loads(summary.read_text(encoding="utf-8"))
        lines += _card(summary.parent.name, entries)
    lines.append("</div>")
    lines += page_footer()
    return "\n".join(lines)


def _home_page(css: str) -> str:
    lines = page_header(f"{PROJECT_NAME} – {PROJECT_TAGLINE}", css)
    lines += page_nav(".", "home")
    lines += [
        '<section class="hero hero-lg">',
        f"  <h1>{PROJECT_NAME}</h1>",
        f'  <p class="tagline">{PROJECT_TAGLINE}</p>',
        f"  <p>{html.escape(PROJECT_DESCRIPTION)}</p>",
        '  <p class="actions">',
        f'    <a class="button" href="{PROJECT_REPO}">Source on GitHub</a>',
        '    <a class="button secondary" href="about/index.html">About</a>',
        '    <a class="button secondary" href="dev/index.html">Development status</a>',
        "  </p>",
        "</section>",
        '<div class="cards">',
    ]
    for title, text in FEATURES:
        lines += [
            '<div class="card">',
            f"  <h2>{html.escape(title)}</h2>",
            f"  <p>{html.escape(text)}</p>",
            "</div>",
        ]
    lines.append("</div>")
    lines += page_footer()
    return "\n".join(lines)


def _about_page(css: str) -> str:
    lines = page_header(f"About – {PROJECT_NAME}", css)
    lines += page_nav("..", "about")
    lines += [
        '<div class="hero prose">',
        f"  <h1>About {PROJECT_NAME}</h1>",
        f"  <p>{html.escape(PROJECT_DESCRIPTION)}</p>",
        "  <h2>Relationship to Flash-X</h2>",
        f'  <p>Flash-MX is derived from <a href="{FLASHX_REPO}">Flash-X</a>. '
        "The compressible hydrodynamics and astrophysics physics units, and the "
        "setups and libraries that depend on them, are not part of Flash-MX. The "
        "version-control history of the retained code is preserved.</p>",
        "  <h2>Contributing</h2>",
        "  <p>Contributors fork the repository (or branch from <strong>main</strong> "
        "if they have write access) and open a pull request against "
        "<strong>staged</strong>. A nightly test-suite run covers everything "
        "merged into staged. If it passes, the change is promoted to "
        "<strong>main</strong>; if it fails, fixing it is the top priority. See "
        f'the <a href="{PROJECT_REPO}#gittesting-workflow">full workflow</a> in the README.</p>',
        "  <h2>Testing</h2>",
        "  <p>Tests are managed with FlashXTest. Unit, comparison and composite "
        "tests run in a container on every push to main and staged; the latest "
        'results are on the <a href="../dev/index.html">Dev page</a>.</p>',
        "  <h2>License</h2>",
        "  <p>Licensed under the Apache License, Version 2.0. Copyright "
        "UChicago Argonne, LLC as Operator of Argonne National Laboratory; see "
        f'<a href="{PROJECT_REPO}/blob/main/NOTICE">NOTICE</a> for provenance.</p>',
        "</div>",
    ]
    lines += page_footer()
    return "\n".join(lines)


def publish_results(output_dir: Path, label: str, results_dir: Path) -> None:
    """Publish the latest run in *results_dir* into the website at *output_dir*.

    Only ``dev/<label>`` is replaced, and it holds just the newest invocation
    of each site (history is purged). Other labels, ``.git`` and any other
    files in *output_dir* are left alone. The home, about and dev pages are
    refreshed from whatever labels are present.

    results_dir is a FlashXTest results directory (contains <site>/<invocation>/).
    """
    output_dir = output_dir.expanduser().resolve()
    results_dir = results_dir.expanduser().resolve()
    if not results_dir.is_dir():
        raise FileNotFoundError(f"Results directory not found: {results_dir}")
    if "/" in label or label in {"", ".", ".."}:
        raise ValueError(f"Invalid results label: {label!r}")

    css_path = Path(__file__).parent / "style.css"
    css = css_path.read_text(encoding="utf-8") if css_path.is_file() else ""

    dev_out = output_dir / "dev"
    dev_out.mkdir(parents=True, exist_ok=True)
    label_dir = dev_out / label

    generate_flashx_testview(
        results_dir,
        label_dir,
        force_rewrite=True,  # label_dir only; never prompts
        root_prefix="../..",
        title=f"Latest results – {label}",
        copy_files=True,
        latest_only=True,
    )
    _write_summary(results_dir, label_dir)

    (output_dir / "about").mkdir(exist_ok=True)
    (output_dir / "index.html").write_text(_home_page(css), encoding="utf-8")
    (output_dir / "about" / "index.html").write_text(_about_page(css), encoding="utf-8")
    (output_dir / ".nojekyll").write_text("", encoding="utf-8")
    (dev_out / "index.html").write_text(_results_index(dev_out, css), encoding="utf-8")

    print(f"✅  Published '{label}' results to {output_dir}")
