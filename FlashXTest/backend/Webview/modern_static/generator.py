#!/usr/bin/env python3
"""Static site generator for legacy FlashTest output directories."""
from __future__ import annotations

import argparse
import sys
import shutil
from pathlib import Path
from typing import Dict, Set

from .fs_utils import list_site_dirs, list_invocation_dirs
from .status import classify_invocation, InvocationStatus
from .index_page import generate_html
from .invocation_page import generate_combined_invocation_page
from .build_page import (
    generate_build_page_frameset,
    generate_left_frame_html,
    generate_right_frame_html,
)


def generate_flashx_testview(
    target_dir: Path, output_dir: Path, *, force_rewrite=False
) -> None:
    """Generate the static FlashTest site into output_dir from target_dir."""
    target_dir = target_dir.expanduser().resolve()
    output_dir = output_dir.expanduser().resolve()
    if not target_dir.is_dir():
        raise FileNotFoundError(
            f"Target directory '{target_dir}' does not exist or is not a directory."
        )

    # Harvest invocation statuses
    board: Dict[str, Dict[str, InvocationStatus]] = {}
    inv_dir_lookup: Dict[str, Dict[str, Path]] = {}
    all_invocations: Set[str] = set()
    site_paths = list_site_dirs(target_dir)
    sites = [p.name for p in site_paths]

    for site_path in site_paths:
        site_name = site_path.name
        for inv_dir in list_invocation_dirs(site_path):
            inv_name = inv_dir.name
            all_invocations.add(inv_name)
            status = classify_invocation(inv_dir)
            board.setdefault(inv_name, {})[site_name] = status
            inv_dir_lookup.setdefault(inv_name, {})[site_name] = inv_dir
    sites.sort()
    invocations_sorted = sorted(all_invocations, reverse=True)

    # Prepare output_dir
    if output_dir.exists():
        if not output_dir.is_dir():
            raise FileExistsError(
                f"Output directory '{output_dir}' exists but is not a directory."
            )
        if not force_rewrite:
            reply = (
                input(f"'{output_dir}' is not empty. Delete everything inside? [y/N] ")
                .strip()
                .lower()
            )
            if reply not in {"y", "yes"}:
                raise RuntimeError("Aborted by user.")
        # Either force=True or user said yes → wipe it
        shutil.rmtree(output_dir)
        print(f"⚠️ Deleted existing output directory '{output_dir}'")

    output_dir.mkdir(parents=True, exist_ok=False)

    # Write overview index.html
    index_html = generate_html(board, sites, invocations_sorted, inv_dir_lookup)
    (output_dir / "index.html").write_text(index_html, encoding="utf-8")

    # Write site-combined invocation pages
    inv_index_dir = output_dir / "invocations"
    inv_index_dir.mkdir(parents=True, exist_ok=True)
    for inv_name in invocations_sorted:
        combined = generate_combined_invocation_page(
            inv_name, inv_dir_lookup.get(inv_name, {}), sites
        )
        (inv_index_dir / f"{inv_name}.html").write_text(combined, encoding="utf-8")

    # Copy shared CSS and JS assets
    pkg_dir = Path(__file__).parent
    # style.css
    style_src = pkg_dir / "style.css"
    if style_src.is_file():
        shutil.copy(style_src, output_dir / "style.css")
    # js assets
    js_src = pkg_dir / "js"
    if js_src.is_dir():
        dst_js = output_dir / "js"
        shutil.copytree(js_src, dst_js, dirs_exist_ok=True)

    # Generate build pages (frameset, left/right)
    for site_path in site_paths:
        site_output_dir = output_dir / site_path.name
        for inv_dir in list_invocation_dirs(site_path):
            inv_output_dir = site_output_dir / inv_dir.name
            for b in sorted(inv_dir.iterdir(), key=lambda p: p.name):
                if not b.is_dir():
                    continue
                build_output_dir = inv_output_dir / b.name
                build_output_dir.mkdir(parents=True, exist_ok=True)
                # Frameset
                (build_output_dir / "frameset.html").write_text(
                    generate_build_page_frameset(site_path.name, inv_dir.name, b.name),
                    encoding="utf-8",
                )
                # Left frame
                (build_output_dir / "leftframe.html").write_text(
                    generate_left_frame_html(site_path.name, inv_dir.name, b.name, b),
                    encoding="utf-8",
                )
                # Right frame
                (build_output_dir / "rightframe.html").write_text(
                    generate_right_frame_html(site_path.name, inv_dir.name, b.name),
                    encoding="utf-8",
                )

    print(f"✅  Static FlashXTestView generated in {output_dir}")
    print(f"    Open {output_dir}/index.html in your browser")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate static FlashTest dashboard.")
    parser.add_argument(
        "--target-dir",
        required=True,
        type=Path,
        help="Path to a FlashTest out directory (contains site sub-dirs)",
    )
    parser.add_argument(
        "--output-dir",
        default=Path("site"),
        type=Path,
        help="Where to place generated HTML (default: ./site)",
    )
    parser.add_argument(
        "--force-rewrite",
        action="store_true",
        default=False,
        help="Force overwrite of existing output directory",
    )
    args = parser.parse_args()
    try:
        generate_flashx_testview(
            args.target_dir, args.output_dir, force_rewrite=args.force_rewrite
        )
    except Exception as e:
        sys.exit(str(e))


if __name__ == "__main__":
    main()
