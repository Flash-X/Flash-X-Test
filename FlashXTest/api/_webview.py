"""Python API for FlashXTest"""

import os
from pathlib import Path

from .. import lib
from .. import backend


def webview(outdir, force_rewrite, results=None):
    """
    Generate a static, read-only webview.

    Arguments
    ---------
    outdir        : Output directory
    force_rewrite : Do not prompt before replacing outdir
    results       : Optional path to a results directory. If given, a
                    self-contained webview of it is packaged into outdir
                    and no "config" is required. Otherwise the view archive
                    from "config" is used.
    """
    if results:
        backend.Webview.generate_flashx_testview(
            target_dir=Path(results),
            output_dir=Path(outdir),
            force_rewrite=force_rewrite,
            copy_files=True,
        )
        return

    # Retrive pathToViewArchive
    apiDict = locals()
    apiDict["testDir"] = os.getcwd()
    apiDict["pathToConfig"] = apiDict["testDir"] + "/config"

    mainDict = lib.config.getMainDict(apiDict)

    view_archive = mainDict["pathToViewArchive"]

    if view_archive is None:
        raise ValueError(
            "No view archive is set. Please run flashxtest init with -vv option."
        )

    # Call backend generator
    backend.Webview.generate_flashx_testview(
        target_dir=Path(view_archive),
        output_dir=Path(outdir),
        force_rewrite=force_rewrite,
    )
