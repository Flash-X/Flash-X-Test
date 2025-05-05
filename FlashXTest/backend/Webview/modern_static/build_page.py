"""
Generate build detail frameset, left frame, and right frame HTML.
"""
import html
import re
from pathlib import Path
from typing import List, Dict

from .html_utils import page_header, page_header_nobody, page_footer


def generate_build_page_frameset(site_name: str, inv_name: str, build_name: str) -> str:
    """Return a frameset HTML page."""
    title = f"{site_name} – {inv_name} – {build_name}"
    lines: List[str] = page_header_nobody(title, css_href="../../../style.css")
    lines.append("<frameset cols=\"40%,*\">")
    lines.append("  <frame src=\"leftframe.html\" name=\"leftframe\">")
    lines.append("  <frame src=\"rightframe.html\" name=\"rightframe\">")
    lines.append("</frameset>")
    lines.append("</html>")
    return "\n".join(lines)


def generate_left_frame_html(
    site_name: str, inv_name: str, build_name: str, build_dir: Path
) -> str:
    """Return HTML for the left frame listing structured sections for a build."""
    title = f"{site_name} – {inv_name} – {build_name}"
    lines: List[str] = page_header(
        title,
        css_href="../../../style.css",
        base_target="rightframe",
        body_class="left-frame",
    )
    lines.append(f"<h1>{html.escape(build_name)}</h1>")
    lines.append(
        f"<h2><a href='../../../invocations/{html.escape(inv_name)}.html' target='_top'>" +
        f"{html.escape(inv_name)}</a></h2>"
    )

    # invocation files
    lines.append("<ul>")
    ti = build_dir / "test.info"
    if ti.is_file():
        lines.append(f"  <li><a href=\"{ti.resolve().as_uri()}\">test.info</a></li>")
    df = build_dir / "deleted_files"
    if df.is_file():
        lines.append(f"  <li><a href=\"{df.resolve().as_uri()}\">deleted_files</a></li>")
    lines.append("</ul>")

    # Setup
    sc = build_dir / "setup_call"
    so = build_dir / "setup_output"
    if sc.is_file():
        lines.append("<h3>Setup</h3>")
        lines.append("<ul>")
        call_text = sc.read_text().strip()
        if so.is_file():
            lines.append(f"  <li><a href=\"{so.resolve().as_uri()}\">{html.escape(call_text)}</a></li>")
        else:
            lines.append(f"  <li>{html.escape(call_text)}</li>")
        lines.append("</ul>")

    # Compilation
    gc = build_dir / "gmake_call"
    go = build_dir / "gmake_output"
    ge = build_dir / "gmake_error"
    ct = build_dir / "compilation_time"
    if gc.is_file() or go.is_file() or ge.is_file() or ct.is_file():
        lines.append("<h3>Compilation</h3>")
        lines.append("<ul>")
        if gc.is_file():
            lines.append(f"  <li><a href=\"{gc.resolve().as_uri()}\">gmake_call</a></li>")
        if go.is_file():
            lines.append(f"  <li><a href=\"{go.resolve().as_uri()}\">gmake_output</a></li>")
        if ge.is_file():
            lines.append(f"  <li><a href=\"{ge.resolve().as_uri()}\">gmake_error</a></li>")
        lines.append("</ul>")
        if ct.is_file():
            lines.append(f"<p>Compilation time: {html.escape(ct.read_text().strip())}</p>")

    # Execution section
    runs = sorted([d for d in build_dir.iterdir() if d.is_dir()], key=lambda x: x.name)
    if runs:
        lines.append(f"<h2>execution performed against {len(runs)} parfiles</h2>")
        for run_dir in runs:
            props: Dict[str, str] = {}
            rs = run_dir / "run_summary"
            if rs.is_file():
                for summary_line in rs.read_text().splitlines():
                    if ":" in summary_line:
                        k, v = summary_line.split(":", 1)
                        k, v = k.strip(), v.strip()
                        if k in props:
                            if k == "wallClockTime":
                                v = props[k] + " + " + v
                            elif k == "numProcs":
                                if v != props[k]:
                                    v = props[k] + " / " + v
                        props[k] = v
            # run failure
            run_failed = False
            errf = run_dir / "errors"
            if errf.is_file():
                try:
                    first = int(errf.read_text().splitlines()[0].strip())
                    run_failed = first > 0
                except Exception:
                    pass
            header = f"{run_dir.name}.par" + (" (failed)" if run_failed else "")
            lines.append(f"<h3>{html.escape(header)}</h3>")

            # processors, wall-clock time, number of checkfiles
            lines.append("<pre>")
            if "numProcs" in props:
                lines.append(
                    f"  Used {html.escape(props['numProcs'])} processor" +
                    f"{'s' if props['numProcs']!='1' else ''}"
                )
            if "wallClockTime" in props:
                lines.append(
                    f"  Wall-clock time: {html.escape(props['wallClockTime'])}"
                )
            if "numCheckfiles" in props:
                lines.append(
                    f"  produced {html.escape(props['numCheckfiles'])} checkfile" +
                    f"{'s' if props['numCheckfiles']!='1' else ''}"
                )
            lines.append("</pre>")

            def _process_li_line(file: Path) -> str:
                """A Helper function to build string for a list item."""
                return(f"  <li><a href=\"{file.resolve().as_uri()}\">{html.escape(file.name)}</a></li>")

            lines.append("<ul>")
            # checkpoint files
            chk_files = sorted(
                [f for f in run_dir.iterdir() if f.is_file() and re.match(r".*?_chk_\d+", f.name)],
                key=lambda x: x.name,
            )
            for cf in chk_files:
                lines.append(_process_li_line(cf))

            # .dat files
            dat_files = sorted(
                [f for f in run_dir.iterdir() if f.is_file() and f.suffix==".dat"],
                key=lambda x: x.name,
            )
            for df in dat_files:
                lines.append(_process_li_line(df))

            # .log files
            log_files = sorted(
                [
                    f
                    for f in run_dir.iterdir()
                    if f.is_file() and f.suffix == ".log" and f.name != "amr.log"
                ],
                key=lambda x: x.name,
            )
            for lf in log_files:
                lines.append(_process_li_line(lf))

            # AMR params
            amrp = run_dir / "amr_runtime_parameters"
            if amrp.is_file():
                lines.append(_process_li_line(amrp))
            amrpd = run_dir / "amr_runtime_parameters.dump"
            if amrpd.is_file():
                lines.append(_process_li_line(amrpd))

            # .par files
            par_files = sorted(
                [f for f in run_dir.iterdir() if f.is_file() and f.suffix == ".par"],
                key=lambda x: x.name,
            )
            for pf in par_files:
                lines.append(_process_li_line(pf))
            # flash files and deleted
            for fn in ["flash_call", "flash_output", "flash_error", "deleted_files"]:
                p = run_dir / fn
                if p.is_file():
                    lines.append(_process_li_line(p))
            lines.append("</ul>")
            # End of list

            # Test Results (sfocu)
            lines.append("<h3>Test Results</h3>")
            to = run_dir / "test_output"
            if to.is_file() and to.stat().st_size>0:
                lines.append("<pre>")
                # NOTE: `test_output` has <b> tag, so don't escape it.
                lines.append(to.read_text())
                lines.append("</pre>")

    lines.extend(page_footer())

    return "\n".join(lines)


def generate_right_frame_html(site_name: str, inv_name: str, build_name: str) -> str:
    """Return HTML for the right frame initial content."""
    title = f"{site_name} – {inv_name} – {build_name}"
    lines: List[str] = page_header(
        title,
        css_href="../../../style.css",
        body_class="right-frame",
    )
    lines.append("<p>Select a file from the left to view its contents.</p>")
    lines.extend(page_footer())
    return "\n".join(lines)
