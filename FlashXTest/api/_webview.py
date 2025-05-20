"""Python API for FlashXTest"""

import os
from pathlib import Path

from .. import lib
from .. import backend


def webview(outdir, force_rewrite):

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
